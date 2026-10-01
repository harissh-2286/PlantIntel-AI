import os
import io
import time
import base64
import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image

from app.ml.config import ml_config
from app.ml.preprocessing import preprocess_image
from app.ml.adaptive_model import AdaptiveEfficientNetV2S

def find_gradcam_target_layer(model, layer_name_setting="auto"):
    """
    Dynamically identifies the final convolutional feature block of EfficientNetV2-S
    suitable for Grad-CAM++ explanation generation.
    """
    if layer_name_setting != "auto" and hasattr(model, layer_name_setting):
        return getattr(model, layer_name_setting), layer_name_setting

    if hasattr(model, "backbone"):
        # AdaptiveEfficientNetV2S: last Conv block in backbone features
        return model.backbone[-1], "backbone[-1]"
    elif hasattr(model, "features"):
        # Baseline EfficientNetV2-S: last Conv block in features
        return model.features[-1], "features[-1]"
    else:
        # Fallback search for last Conv2d layer
        for name, module in reversed(list(model.named_modules())):
            if isinstance(module, nn.Conv2d):
                return module, name
        raise ValueError("Unable to locate a valid Conv2d target layer for Grad-CAM++.")

class GradCAMPlusPlus:
    """
    REAL Grad-CAM++ Implementation.
    Captures layer activations and backward gradients to compute second-order weighted
    class activation maps for post-hoc explanation of target model predictions.
    """
    def __init__(self, model: nn.Module, target_layer: nn.Module = None):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self.handles = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input_tensor, output_tensor):
            self.activations = output_tensor

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        h1 = self.target_layer.register_forward_hook(forward_hook)
        h2 = self.target_layer.register_full_backward_hook(backward_hook)
        self.handles.extend([h1, h2])

    def remove_hooks(self):
        for h in self.handles:
            h.remove()
        self.handles = []

    def generate_cam(self, input_tensor: torch.Tensor, target_class: int = None):
        self.model.eval()

        # Temporarily enable gradients for Grad-CAM++ computation
        with torch.set_grad_enabled(True):
            input_tensor = input_tensor.clone().detach().requires_grad_(True)
            logits = self.model(input_tensor)

            if target_class is None:
                target_class = torch.argmax(logits, dim=1).item()

            score = logits[0, target_class]
            self.model.zero_grad()
            score.backward(retain_graph=True)

        if self.activations is None or self.gradients is None:
            raise RuntimeError("Grad-CAM++ failed to capture activations or gradients from target layer.")

        A = self.activations[0] # [C, H, W]
        G = self.gradients[0]   # [C, H, W]

        g_pos = torch.relu(G)
        g_sq = G ** 2
        g_cu = G ** 3

        # Grad-CAM++ alpha weighting calculation
        sum_A_gcu = torch.sum(A * g_cu, dim=(1, 2), keepdim=True)
        denom = 2.0 * g_sq + sum_A_gcu + 1e-8
        alpha = g_sq / denom

        # Channel weights: sum_ij (alpha * relu(G))
        w = torch.sum(alpha * g_pos, dim=(1, 2)) # [C]

        # Weighted combination of feature activation maps
        cam = torch.zeros((A.shape[1], A.shape[2]), dtype=torch.float32, device=A.device)
        for i, w_k in enumerate(w):
            cam += w_k * A[i]

        cam = torch.relu(cam)
        cam_np = cam.cpu().detach().numpy()

        # Normalize heatmap to [0, 1]
        c_min, c_max = cam_np.min(), cam_np.max()
        if c_max > c_min:
            cam_np = (cam_np - c_min) / (c_max - c_min + 1e-8)
        else:
            cam_np = np.zeros_like(cam_np)

        probabilities = torch.nn.functional.softmax(logits[0], dim=0)
        confidence = float(probabilities[target_class].item())

        return cam_np, target_class, confidence, probabilities

def image_to_base64_png(image_np: np.ndarray) -> str:
    pil_img = Image.fromarray(image_np)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"

def generate_gradcam_explanation(model_instance, image_bytes: bytes, target_class: int = None):
    """
    Main Service Function to generate Grad-CAM++ Explanation artifacts.
    """
    start_time = time.time()
    
    if not model_instance.is_ready or model_instance.model is None:
        raise RuntimeError("AI model is not loaded.")

    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    orig_np = np.array(pil_img)
    w, h = pil_img.width, pil_img.height

    tensor = preprocess_image(pil_img).to(model_instance.device)

    # 1. Identify Target Layer
    target_layer, layer_name = find_gradcam_target_layer(model_instance.model, ml_config.GRADCAM_TARGET_LAYER)

    # 2. Instantiate Grad-CAM++ Engine
    explainer = GradCAMPlusPlus(model_instance.model, target_layer)

    try:
        # 3. Generate Activation Map
        cam_np, resolved_class_id, confidence, probabilities = explainer.generate_cam(tensor, target_class=target_class)

        # Top predictions for target class exploration on frontend
        k = min(5, len(model_instance.categories))
        top_prob, top_catid = torch.topk(probabilities, k)
        top_predictions = []
        for i in range(top_prob.size(0)):
            idx = top_catid[i].item()
            raw_class_name = model_instance.categories[idx] if idx < len(model_instance.categories) else f"Class_{idx}"
            top_predictions.append({
                "class_id": idx,
                "class_name": raw_class_name,
                "confidence": round(float(top_prob[i].item()), 4)
            })

        # 4. Resize Heatmap to original image dimensions
        resized_cam = cv2.resize(cam_np, (w, h), interpolation=cv2.INTER_CUBIC)

        # 5. Apply Colormap (Jet)
        uint8_cam = np.uint8(255 * resized_cam)
        heatmap_bgr = cv2.applyColorMap(uint8_cam, cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)

        # 6. Generate Blended Overlay
        overlay_rgb = cv2.addWeighted(orig_np, 0.5, heatmap_rgb, 0.5, 0)

        # 7. Convert to Base64 Data URLs
        orig_b64 = image_to_base64_png(orig_np)
        heatmap_b64 = image_to_base64_png(heatmap_rgb)
        overlay_b64 = image_to_base64_png(overlay_rgb)

        raw_class_name = model_instance.categories[resolved_class_id] if resolved_class_id < len(model_instance.categories) else f"Class_{resolved_class_id}"

        inference_time = (time.time() - start_time) * 1000

        return {
            "model": {
                "name": "EfficientNetV2-S",
                "architecture": model_instance.architecture,
                "mode": model_instance.mode,
                "version": model_instance.model_version
            },
            "prediction": {
                "class_id": resolved_class_id,
                "class_name": raw_class_name,
                "confidence": round(confidence, 4)
            },
            "top_predictions": top_predictions,
            "explanation": {
                "method": "Grad-CAM++",
                "target_layer": layer_name,
                "target_class": resolved_class_id,
                "original": orig_b64,
                "original_base64": orig_b64,
                "heatmap": heatmap_b64,
                "heatmap_base64": heatmap_b64,
                "overlay": overlay_b64,
                "overlay_base64": overlay_b64,
                "explanation_text": "The highlighted regions indicate areas that contributed strongly to the model's prediction for the selected class."
            },
            "explanation_time_ms": round(inference_time, 2)
        }
    finally:
        # 8. Clean up hooks to prevent memory leaks
        explainer.remove_hooks()
