# Dataset Documentation: PlantIntel AI Benchmark Corpus

## Dataset Overview
The PlantIntel AI project utilizes a standardized benchmark plant disease corpus derived from curated agricultural diagnostic datasets (including PlantVillage and field-collected extension samples). The dataset consists of high-resolution RGB photographs of healthy and diseased plant leaves across multiple crop species.

## Split Statistics & Data Partitioning
To prevent data leakage and ensure rigorous generalization benchmarking, the dataset is strictly partitioned into three disjoint splits using stratified sampling:

| Partition | Percentage | Sample Count | Duplicate Hashes Detected |
| :--- | :---: | :---: | :---: |
| **Training Set** | 70.0% | 38,012 | 0 |
| **Validation Set** | 15.0% | 8,145 | 0 |
| **Test Set (Held-Out)** | 15.0% | 8,146 | 0 |
| **Total Corpus** | **100.0%** | **54,303** | **0** |

## Data Leakage Verification
- **Exact File Hashing:** Executed SHA-256 binary hash comparison across all split directories using `research/data_leakage_check.py`. Zero exact duplicate image files were detected across train, validation, and test partitions.
- **Augmentation Isolation:** Data augmentations (Random Crop, Horizontal Flip, Color Jitter, Rotation) are strictly applied *on-the-fly* during training epoch iterations. No augmented images are saved to disk or exposed to evaluation splits.

## Image Preprocessing Pipeline
1. **Input Resizing:** Standardized bilinear interpolation to `224 x 224` resolution.
2. **Color Normalization:** Subtraction of ImageNet RGB channel means `[0.485, 0.456, 0.406]` and division by standard deviations `[0.229, 0.224, 0.225]`.
3. **Quality Screening:** Pre-inference automated validation screening for minimum resolution (128px), blur index (Laplacian variance > 50.0), over/underexposure (mean intensity between 25 and 230), and leaf surface presence.

## Class Distribution Summary
The corpus spans 38 distinct crop-disease paired classes across 14 major agricultural host species (e.g., Apple, Tomato, Potato, Corn, Grape, Pepper).
- **Most Represented Class:** Soybean Healthy (5,090 samples)
- **Least Represented Class:** Potato Early Blight (1,000 samples)
- **Imbalance Ratio:** ~5.09:1 max-to-min class imbalance ratio.

## Known Dataset Limitations
1. **Controlled Lighting Bias:** A subset of benchmark images was captured under laboratory studio lighting with plain background cardboard, which differs from outdoor canopy occlusion.
2. **Single-Leaf Focus:** The standard split focuses primarily on isolated leaf specimens rather than full crop canopy drone imagery.
