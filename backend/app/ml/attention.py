import torch
import torch.nn as nn

class ChannelAttention(nn.Module):
    """
    Lightweight Channel Attention Mechanism.
    Aggregates global spatial context via Global Average Pooling,
    computes inter-channel dependencies via a bottleneck 1x1 conv layer,
    and produces dynamic channel weights.
    """
    def __init__(self, in_channels: int, reduction_ratio: int = 8):
        super().__init__()
        reduced_channels = max(1, in_channels // reduction_ratio)
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(in_channels, reduced_channels, kernel_size=1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(reduced_channels, in_channels, kernel_size=1, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor):
        # x: [B, C, H, W]
        b, c, _, _ = x.size()
        avg = self.avg_pool(x) # [B, C, 1, 1]
        channel_weights = self.fc(avg) # [B, C, 1, 1]
        return x * channel_weights, channel_weights


class SpatialAttention(nn.Module):
    """
    Lightweight Spatial Attention Mechanism.
    Aggregates channel descriptor information (channel-wise mean and max pooling),
    concatenates descriptors, applies a 7x7 spatial convolution, and produces
    a normalized spatial attention map.
    """
    def __init__(self, kernel_size: int = 7):
        super().__init__()
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor):
        # x: [B, C, H, W]
        avg_out = torch.mean(x, dim=1, keepdim=True) # [B, 1, H, W]
        max_out, _ = torch.max(x, dim=1, keepdim=True) # [B, 1, H, W]
        spatial_descriptors = torch.cat([avg_out, max_out], dim=1) # [B, 2, H, W]
        spatial_weights = self.sigmoid(self.conv(spatial_descriptors)) # [B, 1, H, W]
        return x * spatial_weights, spatial_weights


class AdaptiveLightweightAttention(nn.Module):
    """
    Combined Adaptive Lightweight Attention Module.
    Sequentially applies channel attention followed by spatial attention
    on EfficientNetV2-S feature representations.
    """
    def __init__(self, in_channels: int, reduction_ratio: int = 8, use_channel: bool = True, use_spatial: bool = True):
        super().__init__()
        self.use_channel = use_channel
        self.use_spatial = use_spatial

        if self.use_channel:
            self.channel_attn = ChannelAttention(in_channels, reduction_ratio=reduction_ratio)
        else:
            self.channel_attn = None

        if self.use_spatial:
            self.spatial_attn = SpatialAttention(kernel_size=7)
        else:
            self.spatial_attn = None

    def forward(self, x: torch.Tensor, return_maps: bool = False):
        channel_weights = None
        spatial_weights = None

        if self.use_channel and self.channel_attn is not None:
            x, channel_weights = self.channel_attn(x)

        if self.use_spatial and self.spatial_attn is not None:
            x, spatial_weights = self.spatial_attn(x)

        if return_maps:
            return x, {
                "channel_attention": channel_weights,
                "spatial_attention": spatial_weights
            }

        return x
