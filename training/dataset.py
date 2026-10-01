import os
import sys
import json
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import transforms, datasets
from PIL import Image

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.config import ml_config

def get_transforms(image_size=384):
    """
    Returns data transforms for EfficientNetV2-S.
    Training uses standard mild augmentations.
    Val/Test uses deterministic resizing and normalization.
    """
    # Standard ImageNet normalization used by EfficientNetV2-S
    norm_mean = [0.485, 0.456, 0.406]
    norm_std = [0.229, 0.224, 0.225]

    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=norm_mean, std=norm_std),
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=norm_mean, std=norm_std),
    ])

    return train_transforms, val_transforms

def create_class_mappings(classes, save_dir=None):
    """
    Creates deterministic class_to_idx and idx_to_class mappings.
    Classes are sorted alphabetically to ensure determinism.
    """
    sorted_classes = sorted(list(classes))
    class_to_idx = {cls_name: idx for idx, cls_name in enumerate(sorted_classes)}
    idx_to_class = {idx: cls_name for idx, cls_name in enumerate(sorted_classes)}

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "class_to_idx.json"), "w") as f:
            json.dump(class_to_idx, f, indent=2)
        with open(os.path.join(save_dir, "idx_to_class.json"), "w") as f:
            json.dump(idx_to_class, f, indent=2)

    return class_to_idx, idx_to_class

def get_dataloaders(dataset_path=None, batch_size=None, image_size=None, num_workers=None, class_balancing=None, save_dir=None):
    if dataset_path is None:
        dataset_path = ml_config.DATASET_PATH
    if batch_size is None:
        batch_size = ml_config.BATCH_SIZE
    if image_size is None:
        image_size = ml_config.IMAGE_SIZE
    if num_workers is None:
        num_workers = ml_config.NUM_WORKERS
    if class_balancing is None:
        class_balancing = ml_config.CLASS_BALANCING
    if save_dir is None:
        save_dir = ml_config.MODEL_DIR

    train_dir = os.path.join(dataset_path, "train")
    val_dir = os.path.join(dataset_path, "val")
    test_dir = os.path.join(dataset_path, "test")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        raise FileNotFoundError(f"Dataset splits missing in '{dataset_path}'. Run dataset inspection or split script.")

    train_tf, val_tf = get_transforms(image_size)

    # Load dataset structures
    raw_train_ds = datasets.ImageFolder(root=train_dir)
    classes = raw_train_ds.classes
    class_to_idx, idx_to_class = create_class_mappings(classes, save_dir=save_dir)

    train_dataset = datasets.ImageFolder(root=train_dir, transform=train_tf)
    val_dataset = datasets.ImageFolder(root=val_dir, transform=val_tf)

    test_dataset = None
    if os.path.exists(test_dir):
        test_dataset = datasets.ImageFolder(root=test_dir, transform=val_tf)

    # Calculate class counts and weights for class imbalance handling
    targets = [sample[1] for sample in train_dataset.samples]
    class_counts = [0] * len(classes)
    for t in targets:
        class_counts[t] += 1

    total_samples = len(targets)
    num_classes = len(classes)

    # Calculate balanced weights: w_c = N_total / (N_classes * N_c)
    class_weights = []
    for count in class_counts:
        if count > 0:
            class_weights.append(total_samples / (num_classes * count))
        else:
            class_weights.append(1.0)

    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)

    sampler = None
    shuffle = True

    if class_balancing == "weighted_sampler":
        sample_weights = [class_weights[t] for t in targets]
        sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)
        shuffle = False # Sampler and shuffle are mutually exclusive

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )

    test_loader = None
    if test_dataset is not None:
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True if torch.cuda.is_available() else False
        )

    return {
        "train_loader": train_loader,
        "val_loader": val_loader,
        "test_loader": test_loader,
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "class_counts": class_counts,
        "class_weights": class_weights_tensor,
        "num_classes": num_classes
    }
