import os
import sys
import json
import time
import numpy as np
import torch
import torch.nn as nn
from torchvision.models import efficientnet_v2_s
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.config import ml_config
from app.ml.adaptive_model import AdaptiveEfficientNetV2S, get_parameter_counts
from training.dataset import get_transforms, datasets, DataLoader

def measure_model_performance(model, test_loader, device, num_warmup=2, num_runs=5):
    model.eval()
    model.to(device)

    y_true = []
    y_pred = []

    # Measure inference time
    start_time = time.time()
    total_samples = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)

            y_true.extend(labels.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
            total_samples += images.size(0)

    elapsed_ms = (time.time() - start_time) * 1000
    mean_inference_time_ms = round(elapsed_ms / max(1, total_samples), 2)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    acc = float(accuracy_score(y_true, y_pred))
    macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    weighted_prec, weighted_rec, weighted_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)

    params_info = get_parameter_counts(model)

    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(float(macro_prec), 4),
        "recall_macro": round(float(macro_rec), 4),
        "f1_macro": round(float(macro_f1), 4),
        "precision_weighted": round(float(weighted_prec), 4),
        "recall_weighted": round(float(weighted_rec), 4),
        "f1_weighted": round(float(weighted_f1), 4),
        "total_parameters": params_info["total_params"],
        "inference_time_ms_per_image": mean_inference_time_ms
    }

def run_ablation_study():
    print("==================================================")
    print("      PLANTINTEL AI - ABLATION STUDY EXPERIMENTS   ")
    print("==================================================")

    test_dir = os.path.abspath(os.path.join(ml_config.DATASET_PATH, "test"))

    if not os.path.exists(test_dir) or not os.path.isdir(test_dir):
        print("\n[!] TEST DATASET NOT AVAILABLE.")
        print(f"Test directory '{test_dir}' does not exist.")
        print("Please provide a dataset with a 'test' directory to execute evaluation and ablation experiments.")
        print("==================================================")
        return False

    device = torch.device("cuda" if torch.cuda.is_available() and ml_config.DEVICE == "auto" else "cpu")
    if ml_config.DEVICE != "auto":
        device = torch.device(ml_config.DEVICE)

    # 1. Load Test Dataset
    _, val_tf = get_transforms(ml_config.IMAGE_SIZE)
    test_dataset = datasets.ImageFolder(root=test_dir, transform=val_tf)

    if len(test_dataset) == 0:
        print("[!] Test dataset is empty.")
        return False

    test_loader = DataLoader(
        test_dataset,
        batch_size=ml_config.BATCH_SIZE,
        shuffle=False,
        num_workers=ml_config.NUM_WORKERS
    )

    num_classes = len(test_dataset.classes)
    print(f"Test set loaded: {len(test_dataset)} images across {num_classes} classes.")

    experiments = {}

    # --- Experiment A: Baseline EfficientNetV2-S ---
    print("\nEvaluating Experiment A: EfficientNetV2-S Baseline...")
    baseline = efficientnet_v2_s(weights=None)
    in_features = baseline.classifier[1].in_features
    baseline.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(in_features, num_classes)
    )
    
    baseline_ckpt = ml_config.BASELINE_MODEL_PATH
    if not os.path.exists(baseline_ckpt):
        baseline_ckpt = os.path.join(ml_config.MODEL_DIR, "plantintel_efficientnetv2s_best.pth")

    if os.path.exists(baseline_ckpt):
        ckpt = torch.load(baseline_ckpt, map_location=device)
        baseline.load_state_dict(ckpt["model_state_dict"])
        print(f"  Loaded baseline checkpoint: '{baseline_ckpt}'")

    experiments["baseline"] = measure_model_performance(baseline, test_loader, device)
    experiments["baseline"]["model_name"] = "EfficientNetV2-S Baseline"

    # --- Experiment B: EfficientNetV2-S + Channel Attention ---
    print("Evaluating Experiment B: EfficientNetV2-S + Channel Attention...")
    model_channel = AdaptiveEfficientNetV2S(num_classes=num_classes, reduction_ratio=8, use_channel=True, use_spatial=False, pretrained=False)
    experiments["channel_attention"] = measure_model_performance(model_channel, test_loader, device)
    experiments["channel_attention"]["model_name"] = "EfficientNetV2-S + Channel Attention"

    # --- Experiment C: EfficientNetV2-S + Spatial Attention ---
    print("Evaluating Experiment C: EfficientNetV2-S + Spatial Attention...")
    model_spatial = AdaptiveEfficientNetV2S(num_classes=num_classes, reduction_ratio=8, use_channel=False, use_spatial=True, pretrained=False)
    experiments["spatial_attention"] = measure_model_performance(model_spatial, test_loader, device)
    experiments["spatial_attention"]["model_name"] = "EfficientNetV2-S + Spatial Attention"

    # --- Experiment D: EfficientNetV2-S + Adaptive Lightweight Attention ---
    print("Evaluating Experiment D: EfficientNetV2-S + Adaptive Lightweight Attention...")
    model_adaptive = AdaptiveEfficientNetV2S(num_classes=num_classes, reduction_ratio=8, use_channel=True, use_spatial=True, pretrained=False)
    
    attn_ckpt = ml_config.ATTENTION_MODEL_PATH
    if os.path.exists(attn_ckpt):
        ckpt = torch.load(attn_ckpt, map_location=device)
        model_adaptive.load_state_dict(ckpt["model_state_dict"])
        print(f"  Loaded attention model checkpoint: '{attn_ckpt}'")

    experiments["adaptive_attention"] = measure_model_performance(model_adaptive, test_loader, device)
    experiments["adaptive_attention"]["model_name"] = "EfficientNetV2-S + Adaptive Lightweight Attention"

    # Save Results
    research_dir = os.path.abspath(ml_config.RESEARCH_DIR)
    os.makedirs(research_dir, exist_ok=True)
    os.makedirs(ml_config.MODEL_DIR, exist_ok=True)

    # Save model_comparison.json
    comparison_data = {
        "status": "available",
        "baseline": experiments["baseline"],
        "attention": experiments["adaptive_attention"]
    }
    comparison_path = os.path.join(research_dir, "model_comparison.json")
    with open(comparison_path, "w") as f:
        json.dump(comparison_data, f, indent=2)

    # Save ablation_study.json
    ablation_path = os.path.join(research_dir, "ablation_study.json")
    with open(ablation_path, "w") as f:
        json.dump({
            "status": "available",
            "experiments": experiments
        }, f, indent=2)

    print("\n--- Ablation Study Results Summary ---")
    print(f"{'Model':<45} | {'Accuracy':<8} | {'Macro F1':<8} | {'Params':<10} | {'Latency (ms)'}")
    print("-" * 90)
    for exp_key, exp in experiments.items():
        print(f"{exp['model_name']:<45} | {exp['accuracy']*100:6.2f}%  | {exp['f1_macro']:8.4f} | {exp['total_parameters']:<10,} | {exp['inference_time_ms_per_image']} ms")

    print(f"\nSaved model comparison to: '{comparison_path}'")
    print(f"Saved ablation study to:    '{ablation_path}'")
    print("==================================================")
    return True

if __name__ == "__main__":
    run_ablation_study()
