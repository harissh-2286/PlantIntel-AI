import os
import sys
import json
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.ml.config import ml_config

def calculate_file_hash(filepath: str) -> str:
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            md5.update(chunk)
    return md5.hexdigest()

def run_data_leakage_and_distribution_checks():
    print("==================================================")
    print("  PLANTINTEL AI - DATASET & LEAKAGE VALIDATION   ")
    print("==================================================")

    dataset_path = ml_config.DATASET_PATH
    results_dir = ml_config.RESEARCH_DIR
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(os.path.join(results_dir, "results"), exist_ok=True)

    if not os.path.exists(dataset_path):
        print(f"[NOTE] Dataset directory '{dataset_path}' not found on disk.")
        print("  -> Generating benchmark schema templates with real non-fabricated status.")
        
        leakage_report = {
            "status": "dataset_not_downloaded",
            "message": "Local benchmark dataset files not extracted. Data leakage check skipped.",
            "duplicate_count": 0,
            "train_val_leakage_count": 0,
            "train_test_leakage_count": 0
        }
        with open(os.path.join(results_dir, "results", "data_leakage_report.json"), "w") as f:
            json.dump(leakage_report, f, indent=2)

        class_dist = {
            "status": "dataset_not_downloaded",
            "number_of_classes": 38,
            "sample_distribution": "N/A"
        }
        with open(os.path.join(results_dir, "results", "class_distribution.json"), "w") as f:
            json.dump(class_dist, f, indent=2)

        print("  -> Data leakage check template saved cleanly.")
        return

    # If dataset exists, calculate real hashes
    hashes = {}
    duplicates = []
    leakage = []
    class_counts = {"train": {}, "val": {}, "test": {}}

    for split in ["train", "val", "test"]:
        split_dir = os.path.join(dataset_path, split)
        if not os.path.exists(split_dir):
            continue
        for root, dirs, files in os.walk(split_dir):
            cls_name = os.path.basename(root)
            for f in files:
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    fp = os.path.join(root, f)
                    h = calculate_file_hash(fp)
                    class_counts[split][cls_name] = class_counts[split].get(cls_name, 0) + 1
                    
                    if h in hashes:
                        duplicates.append((fp, hashes[h]["path"]))
                        if hashes[h]["split"] != split:
                            leakage.append((fp, hashes[h]["path"]))
                    else:
                        hashes[h] = {"path": fp, "split": split}

    leakage_report = {
        "status": "completed",
        "total_files_scanned": len(hashes),
        "duplicate_count": len(duplicates),
        "data_leakage_count": len(leakage),
        "leakage_details": leakage[:10]
    }

    with open(os.path.join(results_dir, "results", "data_leakage_report.json"), "w") as f:
        json.dump(leakage_report, f, indent=2)

    with open(os.path.join(results_dir, "results", "class_distribution.json"), "w") as f:
        json.dump({"status": "completed", "class_counts": class_counts}, f, indent=2)

    print(f"  -> Scanned {len(hashes)} dataset files. Duplicates: {len(duplicates)}, Leakage: {len(leakage)}")

if __name__ == "__main__":
    run_data_leakage_and_distribution_checks()
