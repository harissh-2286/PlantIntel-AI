# Chapter 2: System Architecture

## 2.1 Complete End-to-End Pipeline
The system operates through a sequential multi-stage processing pipeline:

```
User (Web Client)
   ↓
Image Upload & Quality Gate (Blur / Exposure / Resolution Check)
   ↓
EfficientNetV2-S Feature Extractor
   ↓
Adaptive Lightweight Attention Module (Channel + Spatial Gating)
   ↓
Refined Feature Representation
   ↓
Multi-Class Disease Classifier
   ↓
Parallel Execution:
   ├── Disease Prediction & Top-K Confidence Scores
   ├── Severity Estimation Engine (Color Space & Mask Contours)
   └── Grad-CAM++ Explanation Engine (Gradient Backprop)
   ↓
Persistent Storage (SQLite Database)
   ↓
Web Interface / Research Dashboard / Downloadable PDF & CSV Reports
```

## 2.2 Software Stack
- **Backend Framework:** FastAPI 0.110 (Python 3.13)
- **Deep Learning Framework:** PyTorch 2.14 / Torchvision 0.29
- **Computer Vision:** OpenCV 5.0 / Pillow 12.3
- **Database ORM:** SQLAlchemy 2.1 / SQLite3
- **Document Rendering:** ReportLab 5.0 (PDF Engine)
- **Frontend Framework:** React 18 / Vite 5 / TailwindCSS / Lucide Icons
