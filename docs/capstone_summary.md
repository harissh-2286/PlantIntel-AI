# Capstone Project Summary: PlantIntel AI

## 1. Project Title
**PlantIntel AI:** Explainable AI & Adaptive Attention Platform for Automated Plant Disease Diagnosis and Severity Estimation

## 2. Problem Statement
Plant diseases account for up to 40% of global agricultural crop yield loss annually. Traditional manual inspection by agronomists is slow, labor-intensive, and geographically constrained. Existing automated computer vision prototypes often operate as "black boxes" without explainability or severity quantify metrics, hindering trust and practical adoption by farmers.

## 3. Key Objectives
1. **Accurate Classification:** Fine-tune EfficientNetV2-S with a custom Adaptive Lightweight Attention (ALA) mechanism for high-precision multi-class disease diagnosis.
2. **Explainable AI (XAI):** Provide dual explainability using Grad-CAM++ and attention weight maps.
3. **Severity Quantification:** Estimate percentage of affected leaf tissue without requiring expensive pixel-level segmentation masks.
4. **Full Full-Stack Production System:** Deliver a responsive Web application (React + FastAPI) supporting persistent history, downloadable PDF diagnostic reports, and CSV data exports.

## 4. Proposed Approach & Key Components
- **Architecture:** EfficientNetV2-S backbone extended with Adaptive Lightweight Attention.
- **Explainability:** Grad-CAM++ with pixel-level heatmap overlay.
- **Severity Quantification:** HSV/LAB color space segmentation combined with morphological contour filtering.
- **Backend Stack:** FastAPI, PyTorch, OpenCV, SQLite, ReportLab.
- **Frontend Stack:** React, Vite, Vanilla CSS glassmorphism, Recharts, Lucide Icons.

## 5. System Architecture
`User` -> `Web UI` -> `Quality Gate` -> `EfficientNetV2-S` -> `Adaptive Attention` -> `Classifier` -> `Severity Engine` -> `Grad-CAM++` -> `SQLite History` -> `PDF/CSV Reports`

## 6. Dataset Summary
- Total Images: 54,303 (38 classes)
- Splits: 70% Train (38,012), 15% Val (8,145), 15% Test (8,146)
- Data Leakage Check: Verified 0 duplicate hashes across splits via SHA-256 binary checks.

## 7. Experimental Results
- **Baseline Accuracy / F1:** 97.42% / 97.22%
- **Proposed Accuracy / F1:** 98.65% / 98.56% (+1.34% F1 improvement)
- **Parameters:** Baseline = 21,458,488; Proposed = 21,540,921 (+82,433 params / +0.38%)
- **CPU Latency:** Baseline = 48.2 ms; Proposed = 51.7 ms (+3.5 ms)

## 8. Web Application & Features
- Single and batch leaf upload analysis with automated quality checks.
- Interactive side-by-side XAI visualization (Grad-CAM++ vs. Adaptive Attention).
- Disease severity progress gauge and affected pixel mask overlays.
- Full research dashboard with dataset distribution, ablation comparisons, and ROC/PR curves.
- Instant PDF report download and CSV export.

## 9. Limitations & Future Work
- **Limitations:** Dependent on visible leaf surface symptoms; sensitive to extreme lighting glare; severity estimation is an affected-area metric rather than 3D volumetric depth.
- **Future Work:** Deployment to mobile edge hardware (TFLite / ONNX Runtime), multi-leaf canopy drone integration, and multi-spectral infrared imagery fusion.
