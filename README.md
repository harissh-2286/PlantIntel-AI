# PlantIntel AI: Explainable Plant Disease Intelligence & Severity Platform

![PlantIntel AI Architecture Banner](docs/visualizations/architecture_diagram.png)

PlantIntel AI is a production-grade, state-of-the-art agricultural artificial intelligence application designed for automated plant disease diagnosis, disease severity estimation, and dual visual explainability (Grad-CAM++ and Adaptive Attention maps).

---

## 🌟 Key Features
- 🌿 **High-Precision Disease Classification:** Fine-tuned EfficientNetV2-S extended with an Adaptive Lightweight Attention (ALA) module achieving **98.65% Top-1 Accuracy** (+1.34% F1 gain over baseline).
- 👁️ **Dual Visual Explainability (XAI):** Real-time generation of **Grad-CAM++** class activation heatmaps co-registered with **Adaptive Attention spatial maps**.
- 📐 **Automated Severity Estimation:** Affected leaf surface area percentage measurement without requiring pixel-annotated training masks.
- 🛡️ **Automated Quality Control Gate:** Pre-inference image validation screening for resolution, motion blur, brightness/exposure, and non-plant out-of-domain inputs.
- 📊 **Research & Benchmarking Dashboard:** Interactive dashboard visualizing baseline vs. proposed metrics, parameter counts, ablation studies, and class distribution.
- 📝 **Diagnostic Reports & History:** Persistent analysis database with instant downloadable **PDF diagnostic reports** (ReportLab engine) and **CSV exports**.
- ⚙️ **Reproducible Scientific Framework:** Built-in seed configuration (`SEED=42`), data leakage audit scripts, and SHA-256 model checksum verification.

---

## 🏗️ System Pipeline Architecture

```
User (Web Client)
   ↓
Image Upload Gate
   ↓
Image Quality Validation Screening (Blur, Resolution, Exposure, Plant Check)
   ↓
EfficientNetV2-S Feature Extractor
   ↓
Adaptive Lightweight Attention (Dual Channel + Spatial Gating)
   ↓
Multi-Class Disease Classifier
   ↓
Disease Prediction + Confidence + Top-K Classes
   │
   ├──> Disease Severity Estimation Engine (Color Space & Morphological Masks)
   └──> Grad-CAM++ Explanation Engine (Gradient Backpropagation)
   ↓
Persistent Storage (SQLite Database)
   ↓
Interactive UI / PDF Report Generator / Research Dashboard
```

---

## ⚙️ Environment Setup & Installation

### Prerequisites
- **Python:** 3.10+ (Tested on Python 3.13)
- **Node.js:** v18+ & npm
- **Operating System:** Windows, Linux, or macOS

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install
```

---

## 🚀 Running the Application

### Start Backend Server (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Start Frontend Dev Server (React/Vite)
```bash
cd frontend
npm run dev
```
- Web Application UI: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing Suite & Verification

Run the comprehensive test suite from the root directory:

```bash
# 1. Test API Endpoints (Health, Info, Predict, Severity, Explain, History, Exports, Edge Cases)
python tests/test_api_endpoints.py

# 2. Test Adaptive Attention Architecture & Parameter Gating
python tests/test_attention.py

# 3. Test Grad-CAM++ Visual Explanation Engine
python tests/test_gradcam.py

# 4. Test Disease Severity Estimation Engine
python tests/test_severity.py

# 5. Test Persistent SQLite Database & PDF/CSV Exporters
python tests/test_history_db.py

# 6. Test Out-of-Domain (OOD) & Image Quality Screening
python tests/test_ood_and_quality.py
```

---

## 🔬 Benchmark Comparison (Baseline vs. Proposed)

Evaluated on identical held-out test partition (`8,146` samples) under `SEED=42`:

| Metric | Baseline (EfficientNetV2-S) | Proposed (EfficientNetV2-S + ALA) | Difference |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 97.42% | **98.65%** | **+1.23%** |
| **Macro Precision** | 97.10% | **98.52%** | **+1.42%** |
| **Macro Recall** | 97.35% | **98.60%** | **+1.25%** |
| **Macro F1-Score** | 97.22% | **98.56%** | **+1.34%** |
| **Total Parameters** | 21,458,488 | 21,540,921 | **+82,433 (+0.38%)** |
| **CPU Latency** | 48.2 ms | 51.7 ms | **+3.5 ms** |
| **GPU Latency** | 4.8 ms | 5.3 ms | **+0.5 ms** |

---

## 📁 Project Directory Structure

```
PlantIntel AI/
│
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI Endpoint Routers
│   │   ├── ml/             # EfficientNetV2-S, Attention, Grad-CAM++, Severity
│   │   ├── database/       # SQLAlchemy ORM, SQLite DB, Schemas
│   │   ├── reports/        # ReportLab PDF Generator Engine
│   │   ├── services/       # Image Quality Screening Service
│   │   └── main.py         # FastAPI App Entrypoint & Lifespan Handler
│   ├── tests/              # Unit & Integration Test Suites
│   └── requirements.txt    # Backend Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/     # UI Design System & Navigation
│   │   ├── pages/          # Home, Analyze, Explain, Research, History, Detail
│   │   └── services/       # Axios API Connector Services
│   └── package.json
│
├── research/
│   ├── config/             # Experiment & Seed Configurations
│   ├── results/            # Baseline & Proposed Metric Logs (JSON)
│   ├── data_leakage_check.py
│   └── visualizations/     # Grad-CAM++ & Attention Sample Maps
│
├── docs/                   # Complete Capstone Documentation Package
│   ├── model_card.md
│   ├── dataset.md
│   ├── experiment_report.md
│   ├── final_results.md
│   └── capstone_summary.md
│
├── .env.example            # Environment Template
└── README.md               # Project Root Guide
```

---

## 🔒 Security & Safe Operations
- All environment parameters are safely loaded via `.env` (template in `.env.example`).
- Zero API keys or secrets committed to repository code.
- File upload handling enforces extension sanitization, MIME checking, and a strict 10MB memory size limit.

---

## 📄 License & Attribution
PlantIntel AI is developed for research and educational purposes as part of the Advanced Capstone Project.
