import os
import sys
import torch
import torch.nn as nn
from PIL import Image
import io

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.attention import ChannelAttention, SpatialAttention, AdaptiveLightweightAttention
from app.ml.adaptive_model import AdaptiveEfficientNetV2S, get_parameter_counts
from app.ml.model import ai_model
from app.config import settings

def test_channel_attention_shapes():
    print("[TEST 1/7] Testing ChannelAttention shapes...")
    x = torch.randn(2, 1280, 12, 12)
    ch_attn = ChannelAttention(in_channels=1280, reduction_ratio=8)
    out, weights = ch_attn(x)
    
    assert out.shape == x.shape, f"ChannelAttention output shape mismatch! Expected {x.shape}, got {out.shape}"
    assert weights.shape == (2, 1280, 1, 1), f"Channel weights shape mismatch! Got {weights.shape}"
    print("  -> ChannelAttention shapes verified successfully.")

def test_spatial_attention_shapes():
    print("[TEST 2/7] Testing SpatialAttention shapes...")
    x = torch.randn(2, 1280, 12, 12)
    sp_attn = SpatialAttention(kernel_size=7)
    out, weights = sp_attn(x)
    
    assert out.shape == x.shape, f"SpatialAttention output shape mismatch! Expected {x.shape}, got {out.shape}"
    assert weights.shape == (2, 1, 12, 12), f"Spatial weights shape mismatch! Got {weights.shape}"
    print("  -> SpatialAttention shapes verified successfully.")

def test_adaptive_attention_combined():
    print("[TEST 3/7] Testing combined AdaptiveLightweightAttention...")
    x = torch.randn(2, 1280, 12, 12)
    attn_module = AdaptiveLightweightAttention(in_channels=1280, reduction_ratio=8)
    out, maps = attn_module(x, return_maps=True)
    
    assert out.shape == x.shape, f"Combined attention shape mismatch! Got {out.shape}"
    assert "channel_attention" in maps and "spatial_attention" in maps, "Attention maps dictionary missing keys!"
    print("  -> Combined AdaptiveLightweightAttention verified successfully.")

def test_adaptive_model_forward():
    print("[TEST 4/7] Testing AdaptiveEfficientNetV2S forward pass...")
    num_classes = 10
    x = torch.randn(2, 3, 224, 224)
    model = AdaptiveEfficientNetV2S(num_classes=num_classes, reduction_ratio=8, pretrained=False)
    
    logits = model(x)
    assert logits.shape == (2, num_classes), f"Model logits shape mismatch! Expected (2, {num_classes}), got {logits.shape}"

    logits_attn, maps = model.forward_with_attention(x)
    assert logits_attn.shape == (2, num_classes), f"Forward with attention logits mismatch! Got {logits_attn.shape}"
    assert maps["spatial_attention"] is not None and maps["channel_attention"] is not None, "Attention maps missing in forward_with_attention!"
    print("  -> AdaptiveEfficientNetV2S forward pass verified successfully.")

def test_gradient_flow_sanity():
    print("[TEST 5/7] Testing Gradient Flow through Attention Module...")
    model = AdaptiveEfficientNetV2S(num_classes=5, reduction_ratio=8, pretrained=False)
    model.train()
    
    x = torch.randn(2, 3, 224, 224)
    target = torch.tensor([0, 2], dtype=torch.long)
    
    criterion = nn.CrossEntropyLoss()
    outputs = model(x)
    loss = criterion(outputs, target)
    loss.backward()

    # Verify gradients flow into channel and spatial attention modules
    for name, param in model.attention.named_parameters():
        assert param.grad is not None, f"Gradient for attention parameter '{name}' is NONE! Gradient flow broken!"
        assert param.grad.abs().sum().item() > 0, f"Gradient for attention parameter '{name}' is zero!"
    
    print("  -> Gradient flow sanity test PASSED! Attention parameters receive non-zero gradients.")

def test_overfitting_sanity():
    print("[TEST 6/7] Testing Overfitting Sanity on Synthetic Batch...")
    model = AdaptiveEfficientNetV2S(num_classes=2, reduction_ratio=8, pretrained=False)
    model.train()
    
    x = torch.randn(4, 3, 64, 64)
    y = torch.tensor([0, 0, 1, 1], dtype=torch.long)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    initial_loss = criterion(model(x), y).item()
    for _ in range(30):
        optimizer.zero_grad()
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        
    final_loss = loss.item()
    assert final_loss < initial_loss, f"Model failed to overfit small batch! Initial: {initial_loss:.4f}, Final: {final_loss:.4f}"
    print(f"  -> Overfitting sanity test PASSED! Loss decreased from {initial_loss:.4f} to {final_loss:.4f}.")

def test_attention_api_prediction():
    print("[TEST 7/7] Testing AI Model Attention Map API service...")
    settings.MODEL_MODE = "attention"
    ai_model.mode = "attention"
    ai_model.load_model()
    
    img = Image.new("RGB", (224, 224), color=(60, 160, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()
    
    attn_res = ai_model.get_attention_map(img_bytes)
    assert "model" in attn_res, "Attention response missing 'model' field!"
    assert "prediction" in attn_res, "Attention response missing 'prediction' field!"
    assert "attention" in attn_res, "Attention response missing 'attention' field!"
    
    print("  -> AI Model Attention API service verified successfully.")

def run_all_unit_tests():
    print("==================================================")
    print("      PLANTINTEL AI - PHASE 5 UNIT TESTS          ")
    print("==================================================")
    test_channel_attention_shapes()
    test_spatial_attention_shapes()
    test_adaptive_attention_combined()
    test_adaptive_model_forward()
    test_gradient_flow_sanity()
    test_overfitting_sanity()
    test_attention_api_prediction()
    print("==================================================")
    print("      ALL PHASE 5 UNIT TESTS PASSED (7/7)!        ")
    print("==================================================")

if __name__ == "__main__":
    run_all_unit_tests()
