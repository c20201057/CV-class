import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBNAct(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, padding=0):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, 1, padding, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class DepthwiseSeparableConv(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1, groups=channels, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, 1, 1, 0, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class LightFPNDecoder(nn.Module):
    def __init__(self, config, in_channel):
        super().__init__()
        self.fuse4 = DepthwiseSeparableConv(in_channel)
        self.fuse3 = DepthwiseSeparableConv(in_channel)
        self.fuse2 = DepthwiseSeparableConv(in_channel)
        self.fuse1 = DepthwiseSeparableConv(in_channel)

        self.mask4 = nn.Conv2d(in_channel, 1, 1)
        self.mask3 = nn.Conv2d(in_channel, 1, 1)
        self.mask2 = nn.Conv2d(in_channel, 1, 1)
        self.mask1 = nn.Sequential(
            DepthwiseSeparableConv(in_channel),
            nn.Conv2d(in_channel, 1, 1),
        )
        self.edge = nn.Sequential(
            DepthwiseSeparableConv(in_channel),
            nn.Conv2d(in_channel, 1, 1),
        )

    @staticmethod
    def _up_like(x, ref):
        return F.interpolate(x, size=ref.shape[2:], mode="bilinear", align_corners=False)

    def forward(self, features):
        x, x1, x2, x3, x4 = features

        p4 = self.fuse4(x4)
        p3 = self.fuse3(x3 + self._up_like(p4, x3))
        p2 = self.fuse2(x2 + self._up_like(p3, x2))
        p1 = self.fuse1(x1 + self._up_like(p2, x1))

        m4 = self.mask4(p4)
        m3 = self.mask3(p3)
        m2 = self.mask2(p2)
        m1 = self.mask1(p1)
        m1 = F.interpolate(m1, size=x.shape[2:], mode="bilinear", align_corners=False)

        edge = self.edge(p1)
        edge = F.interpolate(edge, size=x.shape[2:], mode="bilinear", align_corners=False)

        return edge, [m4, m3, m2, m1]
