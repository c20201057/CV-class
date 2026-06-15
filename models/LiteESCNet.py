import torch
import torch.nn as nn
import torch.nn.functional as F

from models.modules.Encoder import Encoder


class ConvBNAct(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, groups=1):
        super().__init__()
        padding = kernel_size // 2
        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                padding=padding,
                groups=groups,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class DepthwiseSeparableConv(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            ConvBNAct(channels, channels, kernel_size=3, groups=channels),
            ConvBNAct(channels, channels, kernel_size=1),
        )

    def forward(self, x):
        return self.block(x)


class LiteFusionBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.local = DepthwiseSeparableConv(channels)
        self.gate = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, channels, 1, bias=True),
            nn.Sigmoid(),
        )

    def forward(self, high_feature, low_feature=None):
        if low_feature is not None:
            low_feature = F.interpolate(
                low_feature,
                size=high_feature.shape[2:],
                mode="bilinear",
                align_corners=False,
            )
            high_feature = high_feature + low_feature
        fused = self.local(high_feature)
        return fused * self.gate(fused) + fused


class LiteEdgeHead(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.fuse = nn.Sequential(
            ConvBNAct(channels * 3, channels, kernel_size=1),
            DepthwiseSeparableConv(channels),
            nn.Conv2d(channels, 1, kernel_size=1),
        )

    def forward(self, p1, p2, p3, image_size):
        p2 = F.interpolate(p2, size=p1.shape[2:], mode="bilinear", align_corners=False)
        p3 = F.interpolate(p3, size=p1.shape[2:], mode="bilinear", align_corners=False)
        edge = self.fuse(torch.cat([p1, p2, p3], dim=1))
        return F.interpolate(edge, size=image_size, mode="bilinear", align_corners=False)


class LiteESCNet(nn.Module):
    def __init__(self, config, pretrained=True):
        super().__init__()
        self.encoder = Encoder(config, pretrained)
        channels = config.lite_head_channels
        encoder_channels = list(reversed(config.lateral_channels))

        self.proj1 = ConvBNAct(encoder_channels[0], channels, kernel_size=1)
        self.proj2 = ConvBNAct(encoder_channels[1], channels, kernel_size=1)
        self.proj3 = ConvBNAct(encoder_channels[2], channels, kernel_size=1)
        self.proj4 = ConvBNAct(encoder_channels[3], channels, kernel_size=1)

        self.fuse4 = LiteFusionBlock(channels)
        self.fuse3 = LiteFusionBlock(channels)
        self.fuse2 = LiteFusionBlock(channels)
        self.fuse1 = LiteFusionBlock(channels)

        self.edge_head = LiteEdgeHead(channels)
        self.mask4 = nn.Conv2d(channels, 1, kernel_size=1)
        self.mask3 = nn.Conv2d(channels, 1, kernel_size=1)
        self.mask2 = nn.Conv2d(channels, 1, kernel_size=1)
        self.mask1 = nn.Sequential(
            DepthwiseSeparableConv(channels),
            nn.Conv2d(channels, 1, kernel_size=1),
        )
        self.feature_adapters = self._build_feature_adapters(config)

    def _build_feature_adapters(self, config):
        distill_config = getattr(config, "distillation", None)
        if (
            distill_config is None
            or not distill_config.enabled
            or distill_config.feature_loss_weight <= 0
        ):
            return None

        teacher_channels = (
            distill_config.teacher_lateral_channels
            if distill_config.teacher_lateral_channels
            else config.lateral_channels
        )
        student_channels = list(reversed(config.lateral_channels))
        teacher_channels = list(reversed(teacher_channels))

        return nn.ModuleList(
            [
                nn.Conv2d(student_ch, teacher_ch, kernel_size=1, bias=False)
                if student_ch != teacher_ch
                else nn.Identity()
                for student_ch, teacher_ch in zip(student_channels, teacher_channels)
            ]
        )

    def _adapt_features(self, features):
        if self.feature_adapters is None:
            return features
        return tuple(adapter(feature) for adapter, feature in zip(self.feature_adapters, features))

    def forward(self, x, return_features=False):
        raw_features = self.encoder(x)
        x1, x2, x3, x4 = raw_features

        p4 = self.fuse4(self.proj4(x4))
        p3 = self.fuse3(self.proj3(x3), p4)
        p2 = self.fuse2(self.proj2(x2), p3)
        p1 = self.fuse1(self.proj1(x1), p2)

        out_edge = self.edge_head(p1, p2, p3, x.shape[2:])
        m4 = self.mask4(p4)
        m3 = self.mask3(p3)
        m2 = self.mask2(p2)
        m1 = self.mask1(p1)
        m1 = F.interpolate(m1, size=x.shape[2:], mode="bilinear", align_corners=False)
        out_masks = [m4, m3, m2, m1]

        if return_features:
            return out_edge, out_masks, self._adapt_features(raw_features)
        return out_edge, out_masks
