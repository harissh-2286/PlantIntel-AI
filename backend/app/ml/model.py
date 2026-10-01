import os
import io
import time
import logging
import numpy as np
import torch
import torch.nn as nn
from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
from PIL import Image

from app.config import settings
from app.ml.preprocessing import preprocess_image
from app.ml.adaptive_model import AdaptiveEfficientNetV2S, get_parameter_counts
from app.utils.image_utils import heatmap_to_base64

logger = logging.getLogger(__name__)

class PlantDiseaseModel:
    def __init__(self):
        self.model = None
        self.device = None
        self.weights = None
        self.mode = settings.MODEL_MODE
        self.categories = []
        self.is_ready = False
        self.weights_type = "ImageNet"
        self.checkpoint_name = None
        self.architecture = "EfficientNetV2-S"
        self.model_version = "efficientnetv2s-v1"
        self.total_params = 0
        self.trainable_params = 0

    def load_model(self):
        try:
            try:
                torch.set_num_threads(1)
            except Exception:
                pass

            if settings.DEVICE == "auto":
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            else:
                self.device = torch.device(settings.DEVICE)
                
            logger.info(f"[AI] Device: {self.device}")

            # Target Checkpoints
            attn_ckpt = settings.ATTENTION_MODEL_PATH
            base_ckpt = settings.BASELINE_MODEL_PATH
            if not os.path.exists(base_ckpt):
                base_ckpt = settings.MODEL_PATH

            # --- MODE 1: PROPOSED ADAPTIVE ATTENTION MODEL ---
            if self.mode == "attention" and os.path.exists(attn_ckpt):
                logger.info(f"[AI] Loading Adaptive Lightweight Attention checkpoint from '{attn_ckpt}'")
                checkpoint = torch.load(attn_ckpt, map_location=self.device)
                
                idx_to_class = checkpoint.get("idx_to_class", {})
                class_to_idx = checkpoint.get("class_to_idx", {})

                formatted_idx_to_class = {}
                if isinstance(idx_to_class, dict):
                    for k, v in idx_to_class.items():
                        formatted_idx_to_class[int(k)] = v

                num_classes = len(class_to_idx) if class_to_idx else len(formatted_idx_to_class)
                self.categories = [formatted_idx_to_class.get(i, f"Class_{i}") for i in range(num_classes)]

                self.model = AdaptiveEfficientNetV2S(
                    num_classes=num_classes,
                    reduction_ratio=8,
                    use_channel=True,
                    use_spatial=True,
                    pretrained=False
                )
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.architecture = "Adaptive Lightweight Attention"
                self.model_version = "efficientnetv2s-adaptive-attention-v1"
                self.weights_type = "fine_tuned"
                self.checkpoint_name = os.path.basename(attn_ckpt)

            # --- MODE 2: BASELINE EFFICIENTNETV2-S MODEL ---
            elif (self.mode == "baseline" or self.mode == "plant_disease") and os.path.exists(base_ckpt):
                logger.info(f"[AI] Loading Baseline EfficientNetV2-S checkpoint from '{base_ckpt}'")
                checkpoint = torch.load(base_ckpt, map_location=self.device)
                
                idx_to_class = checkpoint.get("idx_to_class", {})
                class_to_idx = checkpoint.get("class_to_idx", {})

                formatted_idx_to_class = {}
                if isinstance(idx_to_class, dict):
                    for k, v in idx_to_class.items():
                        formatted_idx_to_class[int(k)] = v

                num_classes = len(class_to_idx) if class_to_idx else len(formatted_idx_to_class)
                self.categories = [formatted_idx_to_class.get(i, f"Class_{i}") for i in range(num_classes)]

                self.model = efficientnet_v2_s(weights=None)
                in_features = self.model.classifier[1].in_features
                self.model.classifier = nn.Sequential(
                    nn.Dropout(p=0.2, inplace=True),
                    nn.Linear(in_features, num_classes)
                )
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.architecture = "Standard Baseline"
                self.model_version = "efficientnetv2s-baseline-v1"
                self.weights_type = "fine_tuned"
                self.checkpoint_name = os.path.basename(base_ckpt)

            # --- FALLBACK: PRETRAINED IMAGENET MODEL ---
            else:
                logger.warning(f"[AI] Target checkpoint not found for mode '{self.mode}'. Falling back to ImageNet pretrained prototype.")
                self.mode = "pretrained"
                try:
                    self.weights = EfficientNet_V2_S_Weights.DEFAULT
                    self.model = efficientnet_v2_s(weights=self.weights)
                    self.categories = self.weights.meta["categories"]
                except Exception as w_err:
                    logger.warning(f"[AI] Weights download fallback triggered: {w_err}")
                    self.weights = None
                    self.model = efficientnet_v2_s(weights=None)
                    self.categories = [f"Class_{i}" for i in range(1000)]
                self.architecture = "ImageNet Pretrained Prototype"
                self.model_version = "efficientnetv2s-pretrained-v1"
                self.weights_type = "ImageNet"
                self.checkpoint_name = None

            self.model.to(self.device)
            self.model.eval()

            params_info = get_parameter_counts(self.model)
            self.total_params = params_info["total_params"]
            self.trainable_params = params_info["trainable_params"]

            self.is_ready = True
            logger.info(f"[AI] Model ready: {self.architecture} ({self.total_params:,} parameters)")
        except Exception as e:
            logger.error(f"[AI] Failed to load model: {e}")
            self.is_ready = False

    def predict(self, image_bytes: bytes):
        if not self.is_ready or self.model is None:
            self.load_model()
        if not self.is_ready or self.model is None:
            raise RuntimeError("Model is not loaded.")
            
        try:
            start_time = time.time()
            
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            tensor = preprocess_image(image).to(self.device)
            
            with torch.no_grad():
                output = self.model(tensor)
                
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
            k = min(5, len(self.categories))
            top_prob, top_catid = torch.topk(probabilities, k)
            
            top_predictions = []
            for i in range(top_prob.size(0)):
                idx = top_catid[i].item()
                raw_class_name = self.categories[idx] if idx < len(self.categories) else f"Class {idx}"
                
                class_name = raw_class_name
                if self.mode == "pretrained":
                    class_name = f"ImageNet class: {raw_class_name}"
                    
                top_predictions.append({
                    "class_id": idx,
                    "class_name": class_name,
                    "confidence": float(top_prob[i].item())
                })
                
            inference_time_ms = (time.time() - start_time) * 1000

            top_confidence = top_predictions[0]["confidence"]
            confidence_warning = None
            if top_confidence < settings.CONFIDENCE_THRESHOLD:
                confidence_warning = f"Low-confidence prediction ({(top_confidence * 100):.1f}%). Consider uploading another clear image."
            
            return {
                "prediction": top_predictions[0],
                "top_predictions": top_predictions,
                "inference_time_ms": round(inference_time_ms, 2),
                "confidence_warning": confidence_warning
            }
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            raise RuntimeError("Model inference failed.")

    def get_attention_map(self, image_bytes: bytes):
        """
        Extracts real channel and spatial attention weights generated by AdaptiveEfficientNetV2S.
        """
        if not self.is_ready or self.model is None:
            raise RuntimeError("Model is not loaded.")

        start_time = time.time()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = preprocess_image(image).to(self.device)

        if isinstance(self.model, AdaptiveEfficientNetV2S):
            with torch.no_grad():
                output, attn_maps = self.model.forward_with_attention(tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)

            top_prob, top_catid = torch.topk(probabilities, 1)
            idx = top_catid[0].item()
            predicted_class = self.categories[idx] if idx < len(self.categories) else f"Class {idx}"

            # Spatial attention map [1, 1, H, W]
            spatial_map_tensor = attn_maps["spatial_attention"]
            if spatial_map_tensor is not None:
                spatial_np = spatial_map_tensor[0, 0].cpu().numpy() # [H, W]
                heatmap_b64 = heatmap_to_base64(spatial_np, target_size=(image.width, image.height))
                spatial_dims = [int(spatial_np.shape[0]), int(spatial_np.shape[1])]
            else:
                heatmap_b64 = None
                spatial_dims = [0, 0]

            # Channel attention weights [1, C, 1, 1]
            channel_map_tensor = attn_maps["channel_attention"]
            top_channel_weights = []
            if channel_map_tensor is not None:
                ch_weights = channel_map_tensor[0, :, 0, 0].cpu().numpy()
                top_indices = np.argsort(ch_weights)[::-1][:10]
                for ch_idx in top_indices:
                    top_channel_weights.append({
                        "channel_id": int(ch_idx),
                        "weight": round(float(ch_weights[ch_idx]), 4)
                    })

            inference_time_ms = (time.time() - start_time) * 1000

            return {
                "model": "AdaptiveEfficientNetV2S",
                "version": self.model_version,
                "prediction": {
                    "class_id": idx,
                    "class_name": predicted_class,
                    "confidence": round(float(top_prob[0].item()), 4)
                },
                "attention": {
                    "has_attention": True,
                    "channel_top_weights": top_channel_weights,
                    "spatial_map_dimensions": spatial_dims,
                    "spatial_heatmap": heatmap_b64
                },
                "inference_time_ms": round(inference_time_ms, 2)
            }
        else:
            # If loaded model is standard baseline or pretrained, return mock/fallback notification
            pred_res = self.predict(image_bytes)
            return {
                "model": self.architecture,
                "version": self.model_version,
                "prediction": pred_res["prediction"],
                "attention": {
                    "has_attention": False,
                    "message": "Loaded model is standard baseline without attention module. Switch to MODEL_MODE=attention to generate attention heatmaps."
                },
                "inference_time_ms": pred_res["inference_time_ms"]
            }

    def get_metadata(self):
        return {
            "name": "EfficientNetV2-S",
            "architecture": self.architecture if self.is_ready else "Adaptive Lightweight Attention",
            "mode": self.mode,
            "version": self.model_version,
            "framework": "PyTorch",
            "weights": self.weights_type if self.is_ready else "fine_tuned",
            "num_classes": len(self.categories) if self.categories else 38,
            "total_parameters": self.total_params if self.is_ready else 21458488,
            "trainable_parameters": self.trainable_params if self.is_ready else 21458488,
            "device": str(self.device) if self.device else "cpu",
            "checkpoint": self.checkpoint_name
        }

# Global model instance
ai_model = PlantDiseaseModel()
