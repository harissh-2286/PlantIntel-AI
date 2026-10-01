from fastapi import APIRouter, File, UploadFile, HTTPException
from app.ml.classifier import Classifier
from app.services.image_quality import analyze_image_quality
from app.ml.severity import estimate_disease_severity

router = APIRouter()

@router.get("/model/info")
async def model_info():
    if not Classifier.is_ready():
        raise HTTPException(status_code=503, detail="AI model dependencies are not installed or model is unavailable.")
    return Classifier.get_metadata()

@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    if not Classifier.is_ready():
        raise HTTPException(status_code=503, detail="Unable to load EfficientNetV2-S.")
        
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to process image.")
        
    try:
        result = Classifier.predict(contents)
        
        return {
            "model": {
                "name": "EfficientNetV2-S",
                "architecture": Classifier.get_metadata().get("architecture", "EfficientNetV2-S"),
                "mode": Classifier.get_metadata().get("mode", "attention"),
                "version": Classifier.get_metadata().get("version", "v1")
            },
            "prediction": result["prediction"],
            "top_predictions": result["top_predictions"],
            "inference_time_ms": result["inference_time_ms"],
            "confidence_warning": result.get("confidence_warning")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

import os
import uuid
import json
import base64
from datetime import datetime, timezone
from PIL import Image
import io
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db, UPLOADS_DIR, VISUALIZATIONS_DIR
from app.database.schemas import AnalysisCreateSchema
from app.database.repository import create_analysis
from app.ml.gradcam import generate_gradcam_explanation

def save_base64_png(b64_str: str, output_path: str):
    try:
        if not b64_str:
            return None
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        data = base64.b64decode(b64_str)
        with open(output_path, "wb") as f:
            f.write(data)
        return output_path
    except Exception:
        return None

@router.post("/analyze")
async def analyze_full_pipeline(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not Classifier.is_ready():
        raise HTTPException(status_code=503, detail="Unable to load AI model.")
        
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read uploaded file.")

    MAX_SIZE = 10 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    # 1. Quality Check
    quality_result = analyze_image_quality(contents, file.filename)
    
    # 2. Disease Classification
    predict_result = Classifier.predict(contents)
    
    # 3. Severity Estimation
    severity_result = estimate_disease_severity(contents)

    # 4. Grad-CAM++ Explanation Generation
    gradcam_result = None
    try:
        gradcam_result = generate_gradcam_explanation(Classifier.model_instance if hasattr(Classifier, 'model_instance') else None, contents)
    except Exception:
        pass

    # Generate unique Analysis ID (PI-YYYYMMDD-XXXXXX)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    analysis_id = f"PI-{date_str}-{random_str}"

    # Get image dimensions
    w, h = None, None
    try:
        pil_img = Image.open(io.BytesIO(contents))
        w, h = pil_img.width, pil_img.height
    except Exception:
        pass

    # 5. Store File Artifacts
    safe_filename = f"{analysis_id}_orig.jpg"
    orig_path = os.path.join(UPLOADS_DIR, safe_filename)
    with open(orig_path, "wb") as f:
        f.write(contents)

    sev_overlay_b64 = severity_result.get("visualization", {}).get("overlay_base64") if severity_result.get("visualization") else None
    sev_overlay_path = save_base64_png(sev_overlay_b64, os.path.join(VISUALIZATIONS_DIR, f"{analysis_id}_sev.png"))

    gradcam_overlay_b64 = gradcam_result.get("explanation", {}).get("overlay_base64") if gradcam_result else None
    gradcam_overlay_path = save_base64_png(gradcam_overlay_b64, os.path.join(VISUALIZATIONS_DIR, f"{analysis_id}_gradcam.png"))

    pred = predict_result["prediction"]
    sev = severity_result["severity"]
    area = severity_result["area"]

    # 6. Create Database Record
    schema = AnalysisCreateSchema(
        id=analysis_id,
        image_filename=file.filename or safe_filename,
        image_path=orig_path,
        image_width=w,
        image_height=h,
        model_name="EfficientNetV2-S",
        model_version=Classifier.get_metadata().get("version", "v1"),
        model_mode=Classifier.get_metadata().get("mode", "attention"),
        predicted_class=pred["class_name"],
        predicted_class_id=pred["class_id"],
        confidence=float(pred["confidence"]),
        top_predictions_json=json.dumps(predict_result["top_predictions"]),
        severity_percentage=float(sev["percentage"]),
        severity_level=sev["level"],
        leaf_area_pixels=int(area["leaf_pixels"]),
        affected_area_pixels=int(area["affected_pixels"]),
        severity_overlay_path=sev_overlay_path,
        gradcam_overlay_path=gradcam_overlay_path,
        analysis_status="completed"
    )

    try:
        create_analysis(db, schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {str(e)}")

    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "quality": quality_result,
        "model": {
            "name": "EfficientNetV2-S",
            "architecture": Classifier.get_metadata().get("architecture", "Adaptive Lightweight Attention"),
            "mode": Classifier.get_metadata().get("mode", "attention"),
            "version": Classifier.get_metadata().get("version", "v1")
        },
        "prediction": predict_result["prediction"],
        "top_predictions": predict_result["top_predictions"],
        "confidence_warning": predict_result.get("confidence_warning"),
        "severity": severity_result["severity"],
        "area": severity_result["area"],
        "severity_status": severity_result.get("severity_status", "reliable"),
        "severity_message": severity_result.get("message"),
        "severity_visualization": sev_overlay_b64,
        "inference_time_ms": round(predict_result["inference_time_ms"] + severity_result.get("severity_inference_time_ms", 0), 2)
    }

