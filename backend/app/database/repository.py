import os
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, or_
from app.database.models import AnalysisModel
from app.database.schemas import AnalysisCreateSchema

def create_analysis(db: Session, schema: AnalysisCreateSchema) -> AnalysisModel:
    db_item = AnalysisModel(
        id=schema.id,
        created_at=datetime.now(timezone.utc),
        image_filename=schema.image_filename,
        image_path=schema.image_path,
        image_width=schema.image_width,
        image_height=schema.image_height,
        model_name=schema.model_name,
        model_version=schema.model_version,
        model_mode=schema.model_mode,
        predicted_class=schema.predicted_class,
        predicted_class_id=schema.predicted_class_id,
        confidence=schema.confidence,
        top_predictions_json=schema.top_predictions_json,
        severity_percentage=schema.severity_percentage,
        severity_level=schema.severity_level,
        leaf_area_pixels=schema.leaf_area_pixels,
        affected_area_pixels=schema.affected_area_pixels,
        severity_overlay_path=schema.severity_overlay_path,
        gradcam_heatmap_path=schema.gradcam_heatmap_path,
        gradcam_overlay_path=schema.gradcam_overlay_path,
        attention_heatmap_path=schema.attention_heatmap_path,
        analysis_status=schema.analysis_status
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_analysis_by_id(db: Session, analysis_id: str) -> AnalysisModel:
    return db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()

def get_history_paginated(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    search: str = None,
    disease: str = None,
    severity: str = None,
    status: str = None,
    sort_by: str = "newest"
):
    query = db.query(AnalysisModel)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                AnalysisModel.id.ilike(search_pattern),
                AnalysisModel.predicted_class.ilike(search_pattern)
            )
        )

    if disease:
        query = query.filter(AnalysisModel.predicted_class == disease)

    if severity:
        query = query.filter(AnalysisModel.severity_level == severity)

    if status:
        query = query.filter(AnalysisModel.analysis_status == status)

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(asc(AnalysisModel.created_at))
    elif sort_by == "confidence":
        query = query.order_by(desc(AnalysisModel.confidence))
    elif sort_by == "severity":
        query = query.order_by(desc(AnalysisModel.severity_percentage))
    else: # newest
        query = query.order_by(desc(AnalysisModel.created_at))

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return items, total

def delete_analysis(db: Session, analysis_id: str) -> bool:
    item = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()
    if not item:
        return False

    # Safely remove local image files if they exist
    for path_attr in [item.image_path, item.severity_overlay_path, item.gradcam_heatmap_path, item.gradcam_overlay_path, item.attention_heatmap_path]:
        if path_attr and os.path.exists(path_attr):
            try:
                os.remove(path_attr)
            except Exception:
                pass

    db.delete(item)
    db.commit()
    return True

def get_history_statistics(db: Session):
    total_analyses = db.query(func.count(AnalysisModel.id)).scalar() or 0
    diseases_count = db.query(func.count(func.distinct(AnalysisModel.predicted_class))).scalar() or 0
    avg_severity = db.query(func.avg(AnalysisModel.severity_percentage)).scalar() or 0.0

    # Severity distribution
    severity_counts = db.query(AnalysisModel.severity_level, func.count(AnalysisModel.id)).group_by(AnalysisModel.severity_level).all()
    severity_dist = {level: count for level, count in severity_counts}
    
    # Disease distribution (top 10)
    disease_counts = db.query(AnalysisModel.predicted_class, func.count(AnalysisModel.id)).group_by(AnalysisModel.predicted_class).order_by(desc(func.count(AnalysisModel.id))).limit(10).all()
    disease_dist = {disease: count for disease, count in disease_counts}

    return {
        "total_analyses": total_analyses,
        "diseases_detected_count": diseases_count,
        "average_severity_percentage": round(float(avg_severity), 2),
        "severity_distribution": severity_dist,
        "disease_distribution": disease_dist
    }
