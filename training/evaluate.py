import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from torchvision.models import efficientnet_v2_s
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.config import ml_config
from training.dataset import get_transforms, datasets, DataLoader

def evaluate_model():
    print("==================================================")
    print("      PLANTINTEL AI EFFICIENTNETV2-S EVALUATION   ")
    print("==================================================")

    checkpoint_path = os.path.abspath(ml_config.MODEL_PATH)
    test_dir = os.path.abspath(os.path.join(ml_config.DATASET_PATH, "test"))

    if not os.path.exists(checkpoint_path):
        print(f"\n[!] CHECKPOINT NOT AVAILABLE.")
        print(f"Checkpoint file '{checkpoint_path}' does not exist.")
        print("Please train the model first before running evaluation.")
        print("==================================================")
        return False

    if not os.path.exists(test_dir) or not os.path.isdir(test_dir):
        print(f"\n[!] TEST DATASET NOT AVAILABLE.")
        print(f"Test directory '{test_dir}' does not exist.")
        print("Please provide a dataset with a 'test' directory.")
        print("==================================================")
        return False

    # 1. Device Setup
    device = torch.device("cuda" if torch.cuda.is_available() and ml_config.DEVICE == "auto" else "cpu")
    if ml_config.DEVICE != "auto":
        device = torch.device(ml_config.DEVICE)

    print(f"Using device: {device}")
    print(f"Loading checkpoint from: '{checkpoint_path}'...")

    # 2. Load Checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_to_idx = checkpoint.get("class_to_idx", {})
    idx_to_class = checkpoint.get("idx_to_class", {})
    
    if isinstance(idx_to_class, dict):
        idx_to_class = {int(k): v for k, v in idx_to_class.items()}

    num_classes = len(class_to_idx)
    class_names = [idx_to_class[i] for i in range(num_classes)]

    # 3. Reconstruct Model Architecture
    model = efficientnet_v2_s(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(in_features, num_classes)
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    # 4. Load Test Dataset
    _, val_tf = get_transforms(ml_config.IMAGE_SIZE)
    test_dataset = datasets.ImageFolder(root=test_dir, transform=val_tf)

    if len(test_dataset) == 0:
        print("[!] Test dataset contains 0 images.")
        return False

    test_loader = DataLoader(
        test_dataset,
        batch_size=ml_config.BATCH_SIZE,
        shuffle=False,
        num_workers=ml_config.NUM_WORKERS
    )

    print(f"Test images count: {len(test_dataset)} across {num_classes} classes.")

    # 5. Run Evaluation Pass
    y_true = []
    y_pred = []
    y_probs = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            y_true.extend(labels.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
            y_probs.extend(probs.cpu().numpy())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_probs = np.array(y_probs)

    # 6. Calculate Metrics
    acc = accuracy_score(y_true, y_pred)
    macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    weighted_prec, weighted_rec, weighted_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)

    print("\n--- Test Set Evaluation Results ---")
    print(f"Overall Accuracy:  {acc * 100:.2f}%")
    print(f"Macro Precision:   {macro_prec:.4f}")
    print(f"Macro Recall:      {macro_rec:.4f}")
    print(f"Macro F1-Score:    {macro_f1:.4f}")
    print(f"Weighted F1-Score: {weighted_f1:.4f}\n")

    # Per-class metrics
    report_dict = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)

    # 7. Generate & Save Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Save Confusion Matrix JSON
    cm_json_path = os.path.join(ml_config.MODEL_DIR, "confusion_matrix.json")
    with open(cm_json_path, "w") as f:
        json.dump({
            "classes": class_names,
            "matrix": cm.tolist()
        }, f, indent=2)

    # Save Confusion Matrix Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(cm, cmap=plt.cm.Blues)
    fig.colorbar(cax)

    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="left")
    ax.set_yticklabels(class_names)

    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Test Set Confusion Matrix')

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black" if cm[i, j] < (cm.max() / 2) else "white")

    plt.tight_layout()
    cm_img_path = os.path.join(ml_config.MODEL_DIR, "confusion_matrix.png")
    plt.savefig(cm_img_path, dpi=150)
    plt.close()

    # Save Classification Report JSON
    report_path = os.path.join(ml_config.MODEL_DIR, "classification_report.json")
    with open(report_path, "w") as f:
        json.dump(report_dict, f, indent=2)

    # Save Overall Evaluation Metrics JSON for API
    eval_metrics = {
        "status": "available",
        "checkpoint": ml_config.MODEL_PATH,
        "test_images": len(test_dataset),
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(macro_prec), 4),
        "macro_recall": round(float(macro_rec), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_precision": round(float(weighted_prec), 4),
        "weighted_recall": round(float(weighted_rec), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "confusion_matrix_path": cm_img_path,
        "classification_report": report_dict
    }

    eval_metrics_path = os.path.join(ml_config.MODEL_DIR, "evaluation_metrics.json")
    with open(eval_metrics_path, "w") as f:
        json.dump(eval_metrics, f, indent=2)

    print(f"Saved evaluation metrics to:  '{eval_metrics_path}'")
    print(f"Saved classification report to: '{report_path}'")
    print(f"Saved confusion matrix image to:'{cm_img_path}'")
    print("==================================================")
    return True

if __name__ == "__main__":
    evaluate_model()
