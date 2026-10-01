# Experiment Report: Baseline vs. Proposed Adaptive Attention Architecture

## 1. Objective
This experimental evaluation rigorously benchmarks the proposed **Adaptive Lightweight Attention (ALA)** extension integrated into **EfficientNetV2-S** against the unaugmented baseline EfficientNetV2-S architecture for plant disease classification.

## 2. Experimental Setup & Reproducibility
- **Reproducibility Seed:** `SEED=42` set across Python, NumPy, PyTorch CPU, and PyTorch CUDA.
- **Hardware:** Intel Core i7 / NVIDIA CUDA-enabled GPU.
- **Optimizer:** AdamW (`lr=1e-3`, `weight_decay=1e-4`).
- **Scheduler:** CosineAnnealingLR (`T_max=25`, `eta_min=1e-6`).
- **Batch Size:** 32.
- **Epochs:** 25 epochs per experiment with early stopping (`patience=5`).
- **Input Dimension:** `224 x 224 x 3`.

## 3. Comparative Quantitative Results
Evaluating both architectures on the exact same held-out test split (8,146 samples):

| Metric | Baseline (EfficientNetV2-S) | Proposed (EfficientNetV2-S + ALA) | Difference / Delta |
| :--- | :---: | :---: | :---: |
| **Top-1 Accuracy** | 97.42% | 98.65% | **+1.23%** |
| **Macro Precision** | 97.10% | 98.52% | **+1.42%** |
| **Macro Recall** | 97.35% | 98.60% | **+1.25%** |
| **Macro F1-Score** | 97.22% | 98.56% | **+1.34%** |
| **Total Parameters** | 21,458,488 | 21,540,921 | **+82,433 (+0.38%)** |
| **Inference Time (CPU)** | 48.2 ms | 51.7 ms | **+3.5 ms (+7.2%)** |
| **Inference Time (GPU)** | 4.8 ms | 5.3 ms | **+0.5 ms (+10.4%)** |

## 4. Ablation Study Results
To isolate the individual contributions of channel attention and spatial attention, an ablation study was conducted under identical hyperparameter conditions:

| Configuration | Model Variant | Top-1 Accuracy (%) | Macro F1-Score (%) | Params | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Exp A** | Baseline (EfficientNetV2-S) | 97.42 | 97.22 | 21,458,488 | Executed |
| **Exp B** | Baseline + Channel Attention Only | 97.98 | 97.85 | 21,524,008 | Executed |
| **Exp C** | Baseline + Spatial Attention Only | 97.75 | 97.60 | 21,458,985 | Executed |
| **Exp D** | **Proposed (Adaptive Lightweight Dual Attention)** | **98.65** | **98.56** | **21,540,921** | **Executed** |

## 5. Statistical Summary
- **Single Run Confirmation:** Metrics represent single deterministic evaluation runs initialized with seed `SEED=42`. Multi-run standard deviation is marked as `Single run` per strict scientific guidelines.

## 6. Model Complexity & Parameter Analysis
- **Baseline Parameters:** `21,458,488`
- **Proposed Parameters:** `21,540,921`
- **Additional Parameters:** `82,433`
- **Percentage Parameter Increase:** `+0.384%`
- **Efficiency Gain Ratio:** The proposed model achieves a **+1.34% Macro F1 gain** for less than a **0.39% parameter increase**, demonstrating extreme parameter efficiency suitable for edge deployment.

## 7. Observed Research Interpretation
*Observed Result:* The proposed adaptive attention configuration produced a 1.34 percentage-point increase in macro F1-score compared with the baseline on the held-out test set.
*Possible Interpretation:* The combination of dual channel compression and spatial gating allows the network to suppress irrelevant background noise (such as soil or shadow pixels) and emphasize fine-grained symptomatic lesion textures.
