import os
import sys
import json
import time
import random
import numpy as np
import torch
import torch.nn as nn

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.config import ml_config
from app.ml.adaptive_model import AdaptiveEfficientNetV2S, get_parameter_counts
from torchvision.models import efficientnet_v2_s
from training.dataset import get_dataloaders
from training.inspect_dataset import inspect_dataset

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def train_attention_model():
    set_seed(ml_config.SEED)

    print("==================================================")
    print("  PLANTINTEL AI - ADAPTIVE LIGHTWEIGHT ATTENTION  ")
    print("==================================================")

    # 1. Dataset Inspection
    dataset_valid = inspect_dataset(ml_config.DATASET_PATH)
    if not dataset_valid:
        print("\n[!] TRAINING DATASET NOT PROVIDED.")
        print("Training aborted. Please provide a dataset before running training.")
        print("==================================================")
        sys.exit(1)

    # 2. Device Setup
    if ml_config.DEVICE == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(ml_config.DEVICE)

    print(f"\nUsing device: {device}")

    # 3. Load Dataloaders
    data = get_dataloaders(
        dataset_path=ml_config.DATASET_PATH,
        batch_size=ml_config.BATCH_SIZE,
        image_size=ml_config.IMAGE_SIZE,
        num_workers=ml_config.NUM_WORKERS,
        class_balancing=ml_config.CLASS_BALANCING,
        save_dir=ml_config.MODEL_DIR
    )

    train_loader = data["train_loader"]
    val_loader = data["val_loader"]
    class_to_idx = data["class_to_idx"]
    idx_to_class = data["idx_to_class"]
    num_classes = data["num_classes"]
    class_weights = data["class_weights"].to(device)

    # 4. Instantiate Baseline Model & Proposed Attention Model for Parameter Comparison
    baseline_model = efficientnet_v2_s(weights=None)
    in_features = baseline_model.classifier[1].in_features
    baseline_model.classifier[1] = nn.Linear(in_features, num_classes)
    baseline_param_counts = get_parameter_counts(baseline_model)

    model = AdaptiveEfficientNetV2S(
        num_classes=num_classes,
        reduction_ratio=ml_config.REDUCTION_RATIO,
        use_channel=True,
        use_spatial=True,
        pretrained=True
    )

    # Check if baseline checkpoint exists to initialize backbone weights
    baseline_ckpt_path = ml_config.BASELINE_MODEL_PATH
    if not os.path.exists(baseline_ckpt_path):
        baseline_ckpt_path = os.path.join(ml_config.MODEL_DIR, "plantintel_efficientnetv2s_best.pth")

    if os.path.exists(baseline_ckpt_path):
        print(f"\n[*] Initializing backbone weights from baseline checkpoint: '{baseline_ckpt_path}'")
        ckpt = torch.load(baseline_ckpt_path, map_location="cpu")
        state_dict = ckpt.get("model_state_dict", {})
        
        # Load compatible backbone parameters
        model_state = model.state_dict()
        compatible_state = {}
        for k, v in state_dict.items():
            if k.startswith("features."):
                new_key = "backbone." + k[len("features."):]
                if new_key in model_state and model_state[new_key].shape == v.shape:
                    compatible_state[new_key] = v
        model.load_state_dict(compatible_state, strict=False)
        print(f"    Loaded {len(compatible_state)} layer weights into backbone.")

    model.to(device)
    proposed_param_counts = get_parameter_counts(model)

    total_diff = proposed_param_counts["total_params"] - baseline_param_counts["total_params"]
    param_increase_pct = (total_diff / baseline_param_counts["total_params"]) * 100

    print("\n--- Parameter Count Analysis ---")
    print(f"Baseline Parameters:   {baseline_param_counts['total_params']:,}")
    print(f"Proposed Parameters:   {proposed_param_counts['total_params']:,}")
    print(f"Additional Parameters: +{total_diff:,} (+{param_increase_pct:.2f}%)\n")

    # 5. Loss Function
    if ml_config.CLASS_BALANCING == "weighted_ce":
        criterion = nn.CrossEntropyLoss(weight=class_weights)
    else:
        criterion = nn.CrossEntropyLoss()

    # 6. Optimizer & Scheduler
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=ml_config.LEARNING_RATE,
        weight_decay=ml_config.WEIGHT_DECAY
    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=2
    )

    os.makedirs(ml_config.MODEL_DIR, exist_ok=True)
    best_val_loss = float('inf')
    best_val_acc = 0.0
    patience_counter = 0

    history = {
        "epochs": [],
        "train_loss": [],
        "val_loss": [],
        "train_accuracy": [],
        "val_accuracy": [],
        "learning_rate": []
    }

    checkpoint_save_path = ml_config.ATTENTION_MODEL_PATH

    print(f"Starting Training Loop ({ml_config.NUM_EPOCHS} Epochs)...")

    for epoch in range(1, ml_config.NUM_EPOCHS + 1):
        start_time = time.time()
        
        # Train Pass
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += images.size(0)

        epoch_train_loss = running_loss / total_train
        epoch_train_acc = correct_train / total_train

        # Validation Pass
        model.eval()
        running_val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                running_val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val += images.size(0)

        epoch_val_loss = running_val_loss / total_val
        epoch_val_acc = correct_val / total_val

        current_lr = optimizer.param_groups[0]['lr']
        scheduler.step(epoch_val_loss)

        epoch_time = time.time() - start_time

        history["epochs"].append(epoch)
        history["train_loss"].append(round(epoch_train_loss, 4))
        history["val_loss"].append(round(epoch_val_loss, 4))
        history["train_accuracy"].append(round(epoch_train_acc, 4))
        history["val_accuracy"].append(round(epoch_val_acc, 4))
        history["learning_rate"].append(current_lr)

        print(f"Epoch {epoch}/{ml_config.NUM_EPOCHS} [{epoch_time:.1f}s]")
        print(f"  Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc * 100:.2f}%")
        print(f"  Val Loss:   {epoch_val_loss:.4f} | Val Acc:   {epoch_val_acc * 100:.2f}%")
        print(f"  Learning Rate: {current_lr:.6f}\n")

        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_val_acc = epoch_val_acc
            patience_counter = 0

            checkpoint = {
                "model_version": "efficientnetv2s-adaptive-attention-v1",
                "architecture": "AdaptiveEfficientNetV2S",
                "model_state_dict": model.state_dict(),
                "class_to_idx": class_to_idx,
                "idx_to_class": idx_to_class,
                "epoch": epoch,
                "val_loss": epoch_val_loss,
                "val_accuracy": epoch_val_acc,
                "parameter_counts": proposed_param_counts,
                "config": ml_config.to_dict()
            }

            torch.save(checkpoint, checkpoint_save_path)
            print(f"  [*] Saved best attention model to '{checkpoint_save_path}' (Val Loss: {best_val_loss:.4f}, Val Acc: {best_val_acc*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= ml_config.PATIENCE:
                print(f"\nEarly stopping triggered after epoch {epoch}!")
                break

    # Save History and Config JSONs
    history_path = os.path.join(ml_config.MODEL_DIR, "training_history_attention.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    config_save_path = os.path.join(ml_config.MODEL_DIR, "model_config_attention.json")
    with open(config_save_path, "w") as f:
        json.dump(ml_config.to_dict(), f, indent=2)

    print("==================================================")
    print("       ATTENTION MODEL TRAINING COMPLETED         ")
    print(f"Best Validation Accuracy: {best_val_acc * 100:.2f}%")
    print(f"Best Validation Loss:     {best_val_loss:.4f}")
    print(f"Checkpoint Path:          {checkpoint_save_path}")
    print("==================================================")

if __name__ == "__main__":
    train_attention_model()
