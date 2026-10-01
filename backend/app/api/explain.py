from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.ml.classifier import Classifier
from app.ml.model import ai_model
from app.ml.gradcam import generate_gradcam_explanation

router = APIRouter()

@router.post("/explain/attention")
async def explain_attention(file: UploadFile = File(...)):
    if not Classifier.is_ready():
        raise HTTPException(status_code=503, detail="AI model is unavailable.")
        
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to read image file.")

    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
    try:
        attention_result = ai_model.get_attention_map(contents)
        return attention_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate attention heatmap: {str(e)}")

@router.post("/explain/gradcam")
async def explain_gradcam(
    file: UploadFile = File(...),
    target_class: Optional[int] = Form(None)
):
    if not Classifier.is_ready():
        raise HTTPException(status_code=503, detail="AI model is unavailable.")

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to read image file.")

    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    try:
        result = generate_gradcam_explanation(ai_model, contents, target_class=target_class)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to generate Grad-CAM++ explanation: {str(e)}")

@router.post("/explain")
async def combined_explain(
    file: UploadFile = File(...),
    target_class: Optional[int] = Form(None)
):
    """
    Combined explanation endpoint returning Prediction, Attention Map, and Grad-CAM++ Explanation.
    """
    if not Classifier.is_ready():
        raise HTTPException(status_code=503, detail="AI model is unavailable.")

    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to read image file.")

    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    try:
        gradcam_res = generate_gradcam_explanation(ai_model, contents, target_class=target_class)
        attn_res = ai_model.get_attention_map(contents)

        return {
            "model": gradcam_res["model"],
            "prediction": gradcam_res["prediction"],
            "top_predictions": gradcam_res.get("top_predictions", []),
            "attention": attn_res.get("attention", {}),
            "gradcam": gradcam_res["explanation"],
            "explanation_time_ms": gradcam_res.get("explanation_time_ms", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to generate combined explanation: {str(e)}")

