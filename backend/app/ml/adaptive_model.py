import torch
import torch.nn as nn
from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
from app.ml.attention import AdaptiveLightweightAttention

class AdaptiveEfficientNetV2S(nn.Module):
    """
    Proposed Model Architecture:
    EfficientNetV2-S Feature Extraction
    ↓
    Adaptive Lightweight Attention (Channel + Spatial)
    ↓
    Global Average Pooling
    ↓
    Classifier Head
    """
    def __init__(
        self,
        num_classes: int = 1000,
        reduction_ratio: int = 8,
        use_channel: bool = True,
        use_spatial: bool = True,
        pretrained: bool = True
    ):
        super().__init__()
        weights = EfficientNet_V2_S_Weights.DEFAULT if pretrained else None
        base_model = efficientnet_v2_s(weights=weights)
        
        # 1. Feature Extractor (Backbone features output 1280 channels)
        self.backbone = base_model.features
        in_channels = 1280

        # 2. Adaptive Lightweight Attention Module
        self.attention = AdaptiveLightweightAttention(
            in_channels=in_channels,
            reduction_ratio=reduction_ratio,
            use_channel=use_channel,
            use_spatial=use_spatial
        )

        # 3. Global Pooling
        self.pooling = nn.AdaptiveAvgPool2d(1)

        # 4. Classifier Head
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(in_channels, num_classes)
        )

    def forward(self, x: torch.Tensor):
        features = self.backbone(x)
        refined_features = self.attention(features)
        pooled = self.pooling(refined_features)
        pooled = torch.flatten(pooled, 1)
        logits = self.classifier(pooled)
        return logits

    def forward_with_attention(self, x: torch.Tensor):
        features = self.backbone(x)
        refined_features, attn_maps = self.attention(features, return_maps=True)
        pooled = self.pooling(refined_features)
        pooled = torch.flatten(pooled, 1)
        logits = self.classifier(pooled)
        return logits, attn_maps

def get_parameter_counts(model: nn.Module):
    """
    Programmatically calculates total and trainable parameters of a PyTorch model.
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {
        "total_params": total_params,
        "trainable_params": trainable_params
    }
