import os
import json
from fastapi import APIRouter
from app.ml.config import ml_config

from app.ml.reproducibility import get_system_environment_info

router = APIRouter()

@router.get("/system/info")
def get_system_info():
    return get_system_environment_info()

@router.get("/research/metrics")
def get_research_metrics():
    eval_metrics_path = os.path.join(ml_config.MODEL_DIR, "evaluation_metrics.json")
    history_path = os.path.join(ml_config.MODEL_DIR, "training_history_attention.json")
    if not os.path.exists(history_path):
        history_path = os.path.join(ml_config.MODEL_DIR, "training_history.json")

    if not os.path.exists(eval_metrics_path):
        return {
            "status": "not_available",
            "message": "Model evaluation has not been completed."
        }

    try:
        with open(eval_metrics_path, "r") as f:
            metrics_data = json.load(f)

        training_history = None
        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                training_history = json.load(f)

        metrics_data["training_history"] = training_history
        return metrics_data
    except Exception as e:
        return {
            "status": "not_available",
            "message": f"Failed to read model evaluation metrics: {str(e)}"
        }

@router.get("/research/comparison")
def get_model_comparison():
    comp_path = os.path.join(ml_config.RESEARCH_DIR, "model_comparison.json")
    if not os.path.exists(comp_path):
        return {
            "status": "not_available",
            "message": "Model comparison evaluation has not been executed. Run 'python training/ablation.py' to generate metrics."
        }
    try:
        with open(comp_path, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"status": "not_available", "message": str(e)}

@router.get("/research/ablation")
def get_ablation_study():
    ablation_path = os.path.join(ml_config.RESEARCH_DIR, "ablation_study.json")
    if not os.path.exists(ablation_path):
        return {
            "status": "not_available",
            "message": "Ablation study experiments have not been executed. Run 'python training/ablation.py' to generate metrics."
        }
    try:
        with open(ablation_path, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"status": "not_available", "message": str(e)}

@router.get("/research/history")
def get_training_histories():
    base_path = os.path.join(ml_config.MODEL_DIR, "training_history.json")
    attn_path = os.path.join(ml_config.MODEL_DIR, "training_history_attention.json")
    
    res = {"baseline": None, "attention": None}
    if os.path.exists(base_path):
        try:
            with open(base_path, "r") as f:
                res["baseline"] = json.load(f)
        except Exception:
            pass
    if os.path.exists(attn_path):
        try:
            with open(attn_path, "r") as f:
                res["attention"] = json.load(f)
        except Exception:
            pass
    return res

