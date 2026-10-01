import os
import sys

# Add backend directory to sys.path to allow app imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.config import ml_config

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff')

def count_images_in_dir(path):
    if not os.path.exists(path) or not os.path.isdir(path):
        return 0
    count = 0
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(IMAGE_EXTENSIONS):
                count += 1
    return count

def inspect_dataset(dataset_path=None):
    if dataset_path is None:
        dataset_path = ml_config.DATASET_PATH

    dataset_path = os.path.abspath(dataset_path)

    print("==================================================")
    print("           PLANTINTEL AI DATASET INSPECTION       ")
    print("==================================================")
    print(f"Target Directory: {dataset_path}")

    train_dir = os.path.join(dataset_path, "train")
    val_dir = os.path.join(dataset_path, "val")
    test_dir = os.path.join(dataset_path, "test")

    # Check if dataset split structure exists
    has_splits = os.path.exists(train_dir) or os.path.exists(val_dir) or os.path.exists(test_dir)

    if not os.path.exists(dataset_path) or not os.path.isdir(dataset_path):
        print("\n[!] TRAINING DATASET NOT PROVIDED.")
        print(f"Directory '{dataset_path}' does not exist.")
        print("Please create the directory and populate it with train/val/test split folders.")
        print("==================================================")
        return False

    if not has_splits:
        # Check if raw class subdirectories exist directly under dataset_path
        subdirs = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
        if not subdirs:
            print("\n[!] TRAINING DATASET NOT PROVIDED.")
            print(f"Directory '{dataset_path}' is empty.")
            print("==================================================")
            return False
        else:
            print("\n[!] Un-split dataset detected.")
            print("Run 'python training/split_dataset.py' to automatically create train/val/test splits.")
            print("Subdirectories found:", subdirs)
            return False

    # Collect class names from train, val, and test
    classes = set()
    for d in [train_dir, val_dir, test_dir]:
        if os.path.exists(d):
            for cls in os.listdir(d):
                if os.path.isdir(os.path.join(d, cls)):
                    classes.add(cls)

    classes = sorted(list(classes))

    if not classes:
        print("\n[!] TRAINING DATASET NOT PROVIDED.")
        print("No class subdirectories found in train/val/test.")
        print("==================================================")
        return False

    total_train = 0
    total_val = 0
    total_test = 0
    class_stats = {}

    print(f"\nDataset Summary")
    print(f"Total Classes: {len(classes)}\n")

    for cls in classes:
        t_count = count_images_in_dir(os.path.join(train_dir, cls))
        v_count = count_images_in_dir(os.path.join(val_dir, cls))
        test_count = count_images_in_dir(os.path.join(test_dir, cls))

        total_train += t_count
        total_val += v_count
        total_test += test_count

        class_stats[cls] = {
            "train": t_count,
            "val": v_count,
            "test": test_count,
            "total": t_count + v_count + test_count
        }

        print(f"Class: {cls}")
        print(f"  Train:      {t_count}")
        print(f"  Validation: {v_count}")
        print(f"  Test:       {test_count}")
        print(f"  Total:      {t_count + v_count + test_count}\n")

    total_images = total_train + total_val + total_test

    if total_images == 0:
        print("\n[!] TRAINING DATASET NOT PROVIDED.")
        print("No images found inside class directories.")
        print("==================================================")
        return False

    print("--------------------------------------------------")
    print(f"Total Images:      {total_images}")
    print(f"Total Train:       {total_train}")
    print(f"Total Validation:  {total_val}")
    print(f"Total Test:        {total_test}")

    # Calculate class imbalance
    train_counts = [stats["train"] for stats in class_stats.values() if stats["train"] > 0]
    if train_counts:
        min_c = min(train_counts)
        max_c = max(train_counts)
        ratio = max_c / min_c if min_c > 0 else float('inf')
        print(f"Class Imbalance Ratio (Max/Min train count): {ratio:.2f} (Min: {min_c}, Max: {max_c})")
        if ratio > 2.0:
            print("Notice: Significant class imbalance detected. Consider setting CLASS_BALANCING=weighted_ce")
        else:
            print("Class distribution is relatively balanced.")

    print("==================================================")
    return True

if __name__ == "__main__":
    inspect_dataset()
