import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db, UPLOADS_DIR, VISUALIZATIONS_DIR
from app.database import repository
from app.database.schemas import AnalysisCreateSchema
from app.reports.report_service import generate_pdf_report, generate_history_csv_string

router = APIRouter()

def sanitize_filename(filename: str) -> str:
    """
    Prevents directory traversal attacks by stripping path components.
    """
    basename = os.path.basename(filename)
    clean = "".join(c for c in basename if c.isalnum() or c in (".", "_", "-"))
    return clean if clean else "image.jpg"

@router.get("/history")
def get_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    disease: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: str = Query("newest"),
    db: Session = Depends(get_db)
):
    items, total = repository.get_history_paginated(
        db, limit=limit, offset=offset, search=search, disease=disease, severity=severity, status=status, sort_by=sort_by
    )

    formatted_items = []
    for item in items:
        img_url = f"/api/media/uploads/{os.path.basename(item.image_path)}" if item.image_path and os.path.exists(item.image_path) else None
        formatted_items.append({
            "analysis_id": item.id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "predicted_class": item.predicted_class,
            "predicted_class_id": item.predicted_class_id,
            "confidence": round(float(item.confidence), 4),
            "severity_percentage": round(float(item.severity_percentage), 2),
            "severity_level": item.severity_level,
            "analysis_status": item.analysis_status,
            "image_url": img_url
        })

    return {
        "items": formatted_items,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/history/stats")
def get_history_stats(db: Session = Depends(get_db)):
    return repository.get_history_statistics(db)

@router.get("/history/export/csv")
def export_history_csv(db: Session = Depends(get_db)):
    items, _ = repository.get_history_paginated(db, limit=10000, offset=0)
    csv_str = generate_history_csv_string(items)
    filename = f"PlantIntel_History_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/history/{analysis_id}")
def get_single_analysis(analysis_id: str, db: Session = Depends(get_db)):
    # Validate format to prevent SQL / path injection
    if not analysis_id or ".." in analysis_id or "/" in analysis_id or "\\" in analysis_id:
        raise HTTPException(status_code=400, detail="Invalid Analysis ID format.")

    item = repository.get_analysis_by_id(db, analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    top_preds = []
    if item.top_predictions_json:
        try:
            top_preds = json.loads(item.top_predictions_json)
        except Exception:
            pass

    img_url = f"/api/media/uploads/{os.path.basename(item.image_path)}" if item.image_path and os.path.exists(item.image_path) else None
    sev_overlay_url = f"/api/media/visualizations/{os.path.basename(item.severity_overlay_path)}" if item.severity_overlay_path and os.path.exists(item.severity_overlay_path) else None
    gradcam_url = f"/api/media/visualizations/{os.path.basename(item.gradcam_overlay_path)}" if item.gradcam_overlay_path and os.path.exists(item.gradcam_overlay_path) else None

    return {
        "analysis_id": item.id,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "image_filename": item.image_filename,
        "image_url": img_url,
        "image_width": item.image_width,
        "image_height": item.image_height,
        "model": {
            "name": item.model_name,
            "version": item.model_version,
            "mode": item.model_mode
        },
        "prediction": {
            "class_id": item.predicted_class_id,
            "class_name": item.predicted_class,
            "confidence": round(float(item.confidence), 4)
        },
        "top_predictions": top_preds,
        "severity": {
            "percentage": round(float(item.severity_percentage), 2),
            "level": item.severity_level
        },
        "area": {
            "leaf_pixels": item.leaf_area_pixels,
            "affected_pixels": item.affected_area_pixels
        },
        "visualizations": {
            "severity_overlay": sev_overlay_url,
            "gradcam_overlay": gradcam_url
        },
        "analysis_status": item.analysis_status
    }

@router.delete("/history/{analysis_id}")
def delete_single_analysis(analysis_id: str, db: Session = Depends(get_db)):
    if not analysis_id or ".." in analysis_id or "/" in analysis_id or "\\" in analysis_id:
        raise HTTPException(status_code=400, detail="Invalid Analysis ID format.")

    success = repository.delete_analysis(db, analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    return {"status": "success", "message": f"Analysis {analysis_id} deleted successfully."}

@router.get("/report/{analysis_id}/pdf")
def get_pdf_report(analysis_id: str, db: Session = Depends(get_db)):
    analysis_data = get_single_analysis(analysis_id, db)
    try:
        pdf_bytes = generate_pdf_report(analysis_data)
        filename = f"{analysis_id}_Report.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

@router.get("/report/{analysis_id}/json")
def get_json_report(analysis_id: str, db: Session = Depends(get_db)):
    return get_single_analysis(analysis_id, db)

# Safe Media File Serving Endpoints
@router.get("/media/uploads/{filename}")
def serve_upload_media(filename: str):
    clean = sanitize_filename(filename)
    path = os.path.join(UPLOADS_DIR, clean)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File unavailable.")
    return FileResponse(path)

@router.get("/media/visualizations/{filename}")
def serve_visualization_media(filename: str):
    clean = sanitize_filename(filename)
    path = os.path.join(VISUALIZATIONS_DIR, clean)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Visualization unavailable.")
    return FileResponse(path)
