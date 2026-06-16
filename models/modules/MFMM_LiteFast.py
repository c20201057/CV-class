import torch
import torch.nn as nn
import torch.nn.functional as F

from models.modules.LiteBlocks import (
    ConvBNAct,
    DepthwiseSeparableConv,
    LiteChannelSpatialAttention,
)


class LiteMTATwoBranch(nn.Module):
    """Lower-cost MTA block for high-resolution decoder stages.

    It keeps the mask and edge guidance from LiteMTA, while removing the
    Laplacian branch on expensive high-resolution feature maps.
    """

    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.alpha = nn.Parameter(torch.tensor(1.0))

        self.mask_gate = nn.Sequential(
            nn.Conv2d(1, in_channels, kernel_size=3, padding=1, bias=True),
            nn.Sigmoid(),
        )
        self.edge_gate = nn.Sequential(
            nn.Conv2d(1, in_channels, kernel_size=3, padding=1, bias=True),
            nn.Sigmoid(),
        )

        self.mask_branch = DepthwiseSeparableConv(in_channels, in_channels, dilation=1)
        self.edge_branch = DepthwiseSeparableConv(in_channels, in_channels, dilation=2)
        self.fuse = nn.Sequential(
            ConvBNAct(in_channels * 2, out_channels, kernel_size=1),
            DepthwiseSeparableConv(out_channels, out_channels, dilation=1),
        )
        self.attn = LiteChannelSpatialAttention(out_channels)

    def forward(self, x, pred, edge, image=None):
        mask = F.interpolate(
            pred.detach(), size=x.shape[2:], mode="bilinear", align_corners=False
        )
        edge = F.interpolate(
            edge.detach(), size=x.shape[2:], mode="bilinear", align_corners=False
        )

        mask_feature = self.mask_branch(x * (1.0 + self.mask_gate(mask)))
        edge_feature = self.edge_branch(x * (1.0 + self.edge_gate(edge))) * self.alpha

        fused = self.fuse(torch.cat([mask_feature, edge_feature], dim=1))
        return self.attn(fused)
