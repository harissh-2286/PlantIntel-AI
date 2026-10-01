import os
import sys
import numpy as np
import torch
from PIL import Image
import io

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.model import ai_model
from app.config import settings
from app.ml.gradcam import GradCAMPlusPlus, find_gradcam_target_layer, generate_gradcam_explanation
from app.ml.adaptive_model import AdaptiveEfficientNetV2S

def test_target_layer_identification():
    print("[TEST 1/6] Testing Grad-CAM++ Target Layer Identification...")
    model = AdaptiveEfficientNetV2S(num_classes=10, pretrained=False)
    layer, name = find_gradcam_target_layer(model, "auto")
    assert layer is not None, "Failed to identify target layer in AdaptiveEfficientNetV2S!"
    assert name == "backbone[-1]", f"Unexpected target layer name: {name}"
    print(f"  -> Identified target layer successfully: {name}")

def test_gradcam_hooks_and_gradient_calculation():
    print("[TEST 2/6] Testing Activation & Gradient Hooks on Target Layer...")
    model = AdaptiveEfficientNetV2S(num_classes=5, pretrained=False)
    model.eval()
    
    target_layer, _ = find_gradcam_target_layer(model, "auto")
    explainer = GradCAMPlusPlus(model, target_layer)
    
    try:
        x = torch.randn(1, 3, 224, 224)
        cam_np, target_class, confidence, probabilities = explainer.generate_cam(x, target_class=2)
        
        # Verify activation & gradient hooks fired
        assert explainer.activations is not None, "Activation hook did not fire!"
        assert explainer.gradients is not None, "Gradient hook did not fire!"
        
        # Verify feature map and gradient map existence
        assert explainer.activations.shape[0] == 1, f"Unexpected activation shape: {explainer.activations.shape}"
        assert explainer.gradients.shape[0] == 1, f"Unexpected gradient shape: {explainer.gradients.shape}"
        
        print("  -> Activation and gradient hooks fired successfully.")
    finally:
        explainer.remove_hooks()
        assert len(explainer.handles) == 0, "Hooks were not properly removed!"

def test_heatmap_values_and_normalization():
    print("[TEST 3/6] Testing Heatmap Values, NaN/Infinity Check, & Normalization...")
    model = AdaptiveEfficientNetV2S(num_classes=5, pretrained=False)
    target_layer, _ = find_gradcam_target_layer(model, "auto")
    explainer = GradCAMPlusPlus(model, target_layer)
    
    try:
        x = torch.randn(1, 3, 224, 224)
        cam_np, target_class, confidence, probabilities = explainer.generate_cam(x, target_class=0)
        
        assert not np.isnan(cam_np).any(), "Heatmap contains NaN values!"
        assert not np.isinf(cam_np).any(), "Heatmap contains Infinity values!"
        assert cam_np.min() >= 0.0, f"Heatmap min value < 0: {cam_np.min()}"
        assert cam_np.max() <= 1.0 + 1e-6, f"Heatmap max value > 1: {cam_np.max()}"
        assert cam_np.ndim == 2, f"Expected 2D matrix, got shape {cam_np.shape}"
        
        print("  -> Heatmap values are finite, normalized [0, 1], and properly shaped.")
    finally:
        explainer.remove_hooks()

def test_target_class_sanity():
    print("[TEST 4/6] Testing Target Class Sanity & Dynamic Target Resolution...")
    model = AdaptiveEfficientNetV2S(num_classes=5, pretrained=False)
    target_layer, _ = find_gradcam_target_layer(model, "auto")
    explainer = GradCAMPlusPlus(model, target_layer)
    
    try:
        x = torch.randn(1, 3, 224, 224)
        
        # Auto predicted class
        _, class_auto, _, _ = explainer.generate_cam(x, target_class=None)
        assert 0 <= class_auto < 5, f"Invalid auto target class resolved: {class_auto}"
        
        # Specific target class
        _, class_specified, _, _ = explainer.generate_cam(x, target_class=3)
        assert class_specified == 3, f"Target class mismatch! Expected 3, got {class_specified}"
        
        print(f"  -> Target class resolution verified (Auto: {class_auto}, Specified: {class_specified}).")
    finally:
        explainer.remove_hooks()

def test_full_explanation_service_and_base64():
    print("[TEST 5/6] Testing Full Grad-CAM++ Service & Base64 Data URL Output...")
    ai_model.mode = "attention"
    settings.MODEL_MODE = "attention"
    ai_model.load_model()
    
    # Create test leaf image
    img = Image.new("RGB", (300, 300), color=(50, 180, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()
    
    res = generate_gradcam_explanation(ai_model, img_bytes, target_class=None)
    
    assert "model" in res, "Missing 'model' key in response!"
    assert "prediction" in res, "Missing 'prediction' key in response!"
    assert "explanation" in res, "Missing 'explanation' key in response!"
    assert "explanation_time_ms" in res, "Missing 'explanation_time_ms' key!"
    
    exp = res["explanation"]
    assert exp["method"] == "Grad-CAM++", f"Unexpected explanation method: {exp['method']}"
    assert exp["original"].startswith("data:image/png;base64,"), "Original image is not a valid base64 PNG data URL!"
    assert exp["heatmap"].startswith("data:image/png;base64,"), "Heatmap image is not a valid base64 PNG data URL!"
    assert exp["overlay"].startswith("data:image/png;base64,"), "Overlay image is not a valid base64 PNG data URL!"
    
    print(f"  -> Service generated explanation in {res['explanation_time_ms']} ms.")

def test_multi_image_visualizations():
    print("[TEST 6/6] Testing Grad-CAM++ Visualizations on Multiple Image Colors...")
    ai_model.mode = "attention"
    ai_model.load_model()
    
    colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (220, 220, 50), (100, 100, 100)]
    for idx, color in enumerate(colors):
        img = Image.new("RGB", (224, 224), color=color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()
        
        res = generate_gradcam_explanation(ai_model, img_bytes, target_class=0)
        assert len(res["explanation"]["overlay"]) > 100, f"Empty overlay base64 string for image {idx+1}"
        
    print(f"  -> Generated valid visualizations across {len(colors)} test images successfully.")

def run_all_gradcam_tests():
    print("==================================================")
    print("      PLANTINTEL AI - PHASE 7 GRAD-CAM++ TESTS    ")
    print("==================================================")
    test_target_layer_identification()
    test_gradcam_hooks_and_gradient_calculation()
    test_heatmap_values_and_normalization()
    test_target_class_sanity()
    test_full_explanation_service_and_base64()
    test_multi_image_visualizations()
    print("==================================================")
    print("      ALL PHASE 7 GRAD-CAM++ TESTS PASSED (6/6)!  ")
    print("==================================================")

if __name__ == "__main__":
    run_all_gradcam_tests()
