import os
import sys
import shutil
import random

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.config import ml_config

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff')

def split_dataset(
    source_dir=None,
    target_dir=None,
    train_ratio=0.70,
    val_ratio=0.15,
    test_ratio=0.15,
    seed=None
):
    if source_dir is None:
        source_dir = os.path.join(ml_config.DATASET_PATH, "raw")
        if not os.path.exists(source_dir):
            source_dir = ml_config.DATASET_PATH

    if target_dir is None:
        target_dir = ml_config.DATASET_PATH

    if seed is None:
        seed = ml_config.SEED

    random.seed(seed)

    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)

    print(f"Splitting dataset from '{source_dir}' into '{target_dir}'...")
    print(f"Ratios -> Train: {train_ratio*100:.0f}%, Val: {val_ratio*100:.0f}%, Test: {test_ratio*100:.0f}% (Seed: {seed})")

    if not os.path.exists(source_dir):
        print(f"[!] Source directory '{source_dir}' does not exist.")
        print("TRAINING DATASET NOT PROVIDED.")
        return False

    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d)) and d not in ['train', 'val', 'test', 'raw']]

    if not subdirs:
        print("[!] No class subdirectories found in source directory.")
        print("TRAINING DATASET NOT PROVIDED.")
        return False

    for cls in subdirs:
        cls_path = os.path.join(source_dir, cls)
        images = [f for f in os.listdir(cls_path) if f.lower().endswith(IMAGE_EXTENSIONS)]
        
        if not images:
            continue

        images.sort() # Deterministic ordering before shuffle
        random.shuffle(images)

        n_total = len(images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train + n_val]
        test_imgs = images[n_train + n_val:]

        splits = {
            "train": train_imgs,
            "val": val_imgs,
            "test": test_imgs
        }

        for split_name, split_files in splits.items():
            dest_cls_dir = os.path.join(target_dir, split_name, cls)
            os.makedirs(dest_cls_dir, exist_ok=True)
            for fname in split_files:
                src_file = os.path.join(cls_path, fname)
                dest_file = os.path.join(dest_cls_dir, fname)
                shutil.copy2(src_file, dest_file)

        print(f"Class '{cls}': {len(train_imgs)} train, {len(val_imgs)} val, {len(test_imgs)} test (Total: {n_total})")

    print("\nDataset split complete.")
    return True

if __name__ == "__main__":
    split_dataset()
