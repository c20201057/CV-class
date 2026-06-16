import torch
import torch.nn as nn


class ConvBNAct(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size=1,
        stride=1,
        dilation=1,
        groups=1,
    ):
        super().__init__()
        padding = dilation * (kernel_size // 2)
        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                stride=stride,
                padding=padding,
                dilation=dilation,
                groups=groups,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels=None, kernel_size=3, dilation=1):
        super().__init__()
        out_channels = out_channels or in_channels
        self.block = nn.Sequential(
            ConvBNAct(
                in_channels,
                in_channels,
                kernel_size=kernel_size,
                dilation=dilation,
                groups=in_channels,
            ),
            ConvBNAct(in_channels, out_channels, kernel_size=1),
        )

    def forward(self, x):
        return self.block(x)


class LiteChannelSpatialAttention(nn.Module):
    def __init__(self, channels, reduction=8):
        super().__init__()
        hidden = max(channels // reduction, 4)
        self.channel_gate = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, hidden, 1, bias=True),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden, channels, 1, bias=True),
            nn.Sigmoid(),
        )
        self.spatial_gate = nn.Sequential(
            nn.Conv2d(2, 1, kernel_size=3, padding=1, bias=True),
            nn.Sigmoid(),
        )

    def forward(self, x):
        channel_weight = self.channel_gate(x)
        x = x * channel_weight
        spatial_context = torch.cat(
            [x.mean(dim=1, keepdim=True), x.amax(dim=1, keepdim=True)],
            dim=1,
        )
        return x * self.spatial_gate(spatial_context)
