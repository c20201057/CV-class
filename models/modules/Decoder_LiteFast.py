import torch
import torch.nn as nn
import torch.nn.functional as F

from models.modules.Decoder_Lite import LiteFEM, LitePatchBlock
from models.modules.LiteBlocks import ConvBNAct, DepthwiseSeparableConv
from models.modules.MFMM_Lite import LiteMTA
from models.modules.MFMM_LiteFast import LiteMTATwoBranch
from models.modules.utils import image2patches


class LiteFastDecoder(nn.Module):
    """FLOPs-oriented LiteDecoder variant.

    The overall ESCNet decoding flow is kept unchanged. The changes are limited
    to narrower image-patch guidance and a two-branch MTA at the highest
    resolution decoder stage.
    """

    def __init__(self, config, in_channel):
        super().__init__()
        patch_channels = max(in_channel // 8, 8)
        self.ipt_blk5 = LitePatchBlock(2**10 * 3, patch_channels)
        self.ipt_blk4 = LitePatchBlock(2**8 * 3, patch_channels)
        self.ipt_blk3 = LitePatchBlock(2**6 * 3, patch_channels)
        self.ipt_blk2 = LitePatchBlock(2**4 * 3, patch_channels)

        self.decoder_block4 = nn.Sequential(
            ConvBNAct(in_channel, in_channel, kernel_size=1),
            DepthwiseSeparableConv(in_channel, in_channel, dilation=2),
        )
        self.decoder_block3 = LiteMTA(in_channel, in_channel)
        self.decoder_block2 = LiteMTA(in_channel, in_channel)
        self.decoder_block1 = LiteMTATwoBranch(in_channel, in_channel)

        self.conv_mask_4 = nn.Conv2d(in_channel, 1, kernel_size=1)
        self.conv_mask_3 = nn.Conv2d(in_channel, 1, kernel_size=1)
        self.conv_mask_2 = nn.Conv2d(in_channel, 1, kernel_size=1)

        self.tra_fr = nn.Sequential(
            nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False),
            ConvBNAct(in_channel, in_channel // 2, kernel_size=1),
        )
        self.predictor_fr = nn.Sequential(
            nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False),
            DepthwiseSeparableConv(in_channel // 2, in_channel // 2, dilation=1),
            nn.Conv2d(in_channel // 2, 1, kernel_size=1),
        )

        fused_channels = in_channel + patch_channels
        self.De_conv4 = LiteFEM(fused_channels, in_channel, edge=True)
        self.De_conv3 = LiteFEM(fused_channels, in_channel, edge=True)
        self.De_conv2 = LiteFEM(fused_channels, in_channel, edge=True)
        self.De_conv1 = LiteFEM(fused_channels, in_channel, edge=True)

    def _add_patch_feature(self, image, feature, patch_block):
        patches = image2patches(
            image,
            patch_ref=feature,
            transformation="b c (hg h) (wg w) -> b (c hg wg) h w",
        )
        patch_feature = patch_block(
            F.interpolate(
                patches,
                size=feature.shape[2:],
                mode="bilinear",
                align_corners=False,
            )
        )
        return torch.cat([feature, patch_feature], dim=1)

    def forward(self, features, edge):
        x, x1, x2, x3, x4 = features

        x4 = self._add_patch_feature(x, x4, self.ipt_blk5)
        x4 = self.De_conv4(
            x4,
            edge=F.interpolate(edge, size=x4.shape[2:], mode="bilinear", align_corners=False),
        )

        x3 = self._add_patch_feature(x, x3, self.ipt_blk4)
        x3 = self.De_conv3(
            x3,
            edge=F.interpolate(edge, size=x3.shape[2:], mode="bilinear", align_corners=False),
        )

        x2 = self._add_patch_feature(x, x2, self.ipt_blk3)
        x2 = self.De_conv2(
            x2,
            edge=F.interpolate(edge, size=x2.shape[2:], mode="bilinear", align_corners=False),
        )

        x1 = self._add_patch_feature(x, x1, self.ipt_blk2)
        x1 = self.De_conv1(
            x1,
            edge=F.interpolate(edge, size=x1.shape[2:], mode="bilinear", align_corners=False),
        )

        p4 = self.decoder_block4(x4)
        m4 = self.conv_mask_4(p4)

        p3 = self.decoder_block3(
            F.interpolate(p4, size=x3.shape[2:], mode="bilinear", align_corners=False) + x3,
            m4,
            edge,
            x,
        )
        m3 = self.conv_mask_3(p3)

        p2 = self.decoder_block2(
            F.interpolate(p3, size=x2.shape[2:], mode="bilinear", align_corners=False) + x2,
            m3,
            edge,
            x,
        )
        m2 = self.conv_mask_2(p2)

        p1 = self.decoder_block1(
            F.interpolate(p2, size=x1.shape[2:], mode="bilinear", align_corners=False) + x1,
            m2,
            edge,
            x,
        )
        m1 = self.predictor_fr(self.tra_fr(p1))

        return [m4, m3, m2, m1]
