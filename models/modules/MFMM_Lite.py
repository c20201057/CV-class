import torch
import torch.nn as nn
import torch.nn.functional as F
from kornia.filters import laplacian
from torchvision.transforms.functional import rgb_to_grayscale

from models.modules.LiteBlocks import (
    ConvBNAct,
    DepthwiseSeparableConv,
    LiteChannelSpatialAttention,
)


class LiteMTA(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, use_laplace: bool = True) -> None:
        super().__init__()
        self.use_laplace = use_laplace
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

        self.mask_gate = nn.Sequential(
            nn.Conv2d(1, in_channels, kernel_size=3, padding=1, bias=True),
            nn.Sigmoid(),
        )
        self.edge_gate = nn.Sequential(
            nn.Conv2d(1, in_channels, kernel_size=3, padding=1, bias=True),
            nn.Sigmoid(),
        )
        self.laplace_gate = (
            nn.Sequential(
                nn.Conv2d(1, in_channels, kernel_size=3, padding=1, bias=True),
                nn.Sigmoid(),
            )
            if use_laplace
            else None
        )

        self.mask_branch = DepthwiseSeparableConv(in_channels, in_channels, dilation=1)
        self.edge_branch = DepthwiseSeparableConv(in_channels, in_channels, dilation=2)
        self.laplace_branch = (
            DepthwiseSeparableConv(in_channels, in_channels, dilation=3)
            if use_laplace
            else None
        )
        fuse_in_channels = in_channels * (3 if use_laplace else 2)
        self.fuse = nn.Sequential(
            ConvBNAct(fuse_in_channels, out_channels, kernel_size=1),
            DepthwiseSeparableConv(out_channels, out_channels, dilation=2),
        )
        self.attn = LiteChannelSpatialAttention(out_channels)

    def forward(self, x, pred, edge, image):
        mask = F.interpolate(
            pred.detach(), size=x.shape[2:], mode="bilinear", align_corners=False
        )
        edge = F.interpolate(
            edge.detach(), size=x.shape[2:], mode="bilinear", align_corners=False
        )

        mask_feature = self.mask_branch(x * (1.0 + self.mask_gate(mask)))
        edge_feature = self.edge_branch(x * (1.0 + self.edge_gate(edge))) * self.alpha
        features = [mask_feature, edge_feature]

        if self.use_laplace:
            gray = rgb_to_grayscale(image)
            laplace = laplacian(gray, kernel_size=5, normalized=True)
            laplace = F.interpolate(
                laplace, size=x.shape[2:], mode="bilinear", align_corners=False
            )
            laplace_feature = (
                self.laplace_branch(x * (1.0 + self.laplace_gate(laplace))) * self.beta
            )
            features.append(laplace_feature)

        fused = self.fuse(torch.cat(features, dim=1))
        return self.attn(fused)
