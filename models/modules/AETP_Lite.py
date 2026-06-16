import torch
import torch.nn as nn
import torch.nn.functional as F

from models.modules.LiteBlocks import ConvBNAct, DepthwiseSeparableConv


class LiteReduce(nn.Module):
    def __init__(self, channels, dilation=1):
        super().__init__()
        self.block = nn.Sequential(
            ConvBNAct(channels * 2, channels, kernel_size=1),
            DepthwiseSeparableConv(channels, channels, dilation=dilation),
        )

    def forward(self, x):
        return self.block(x)


class LiteAETP(nn.Module):
    def __init__(self, in_channel):
        super().__init__()
        self.reduce3 = LiteReduce(in_channel, dilation=2)
        self.reduce2 = LiteReduce(in_channel, dilation=2)
        self.reduce1 = LiteReduce(in_channel, dilation=1)

        self.conv4_1 = DepthwiseSeparableConv(in_channel, in_channel, dilation=2)
        self.conv3_1 = DepthwiseSeparableConv(in_channel, in_channel, dilation=2)
        self.conv2_1 = DepthwiseSeparableConv(in_channel, in_channel, dilation=1)

        self.ctx_f3 = DepthwiseSeparableConv(in_channel, in_channel, dilation=2)
        self.ctx_f2 = DepthwiseSeparableConv(in_channel, in_channel, dilation=1)
        self.conv_s2 = ConvBNAct(2 * in_channel, in_channel, kernel_size=1)
        self.ctx_s2 = DepthwiseSeparableConv(in_channel, in_channel, dilation=2)
        self.edge_conv = nn.Sequential(
            ConvBNAct(3 * in_channel, in_channel, kernel_size=1),
            DepthwiseSeparableConv(in_channel, in_channel, dilation=2),
        )
        self.out = nn.Conv2d(in_channel, 1, kernel_size=1)

    def forward(self, features):
        x, x1, x2, x3, x4 = features

        x3 = self.reduce3(
            torch.cat(
                [
                    x3,
                    F.interpolate(
                        x4, size=x3.shape[2:], mode="bilinear", align_corners=False
                    ),
                ],
                dim=1,
            )
        )
        x2 = self.reduce2(
            torch.cat(
                [
                    x2,
                    F.interpolate(
                        x4, size=x2.shape[2:], mode="bilinear", align_corners=False
                    ),
                ],
                dim=1,
            )
        )
        x1 = self.reduce1(
            torch.cat(
                [
                    x1,
                    F.interpolate(
                        x4, size=x1.shape[2:], mode="bilinear", align_corners=False
                    ),
                ],
                dim=1,
            )
        )

        x4 = F.interpolate(x4, size=x3.shape[2:], mode="bilinear", align_corners=False)
        f3 = x3 + self.conv4_1(x4)

        x3_up = F.interpolate(x3, size=x2.shape[2:], mode="bilinear", align_corners=False)
        f2 = x2 + self.conv3_1(x3_up)

        f3 = F.interpolate(f3, size=x2.shape[2:], mode="bilinear", align_corners=False)

        x2_up = F.interpolate(x2, size=x1.shape[2:], mode="bilinear", align_corners=False)
        f1 = x1 + self.conv2_1(x2_up)

        f3 = self.ctx_f3(f3)
        s2 = torch.cat([f2, f3], dim=1)

        f2 = F.interpolate(f2, size=x1.shape[2:], mode="bilinear", align_corners=False)
        f2 = self.ctx_f2(f2)
        s1 = torch.cat([f1, f2], dim=1)

        s2 = F.interpolate(s2, size=x1.shape[2:], mode="bilinear", align_corners=False)
        s2 = self.ctx_s2(self.conv_s2(s2))

        edge = self.edge_conv(torch.cat([s2, s1], dim=1))
        edge = F.interpolate(edge, size=x.shape[2:], mode="bilinear", align_corners=False)
        return self.out(edge)
