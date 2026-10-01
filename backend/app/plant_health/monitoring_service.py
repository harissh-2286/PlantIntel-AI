"""
Plant Health Monitoring Service
Handles plant profile management, historical timeline generation, severity trend tracking,
alert calculations, and scan comparison.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.models import PlantModel, PlantAnalysisLinkModel, AnalysisModel
from app.database.repository import get_analysis_by_id
from app.plant_health.schemas import (
    PlantCreateSchema, PlantItemSchema, TimelineEventSchema,
    TrendPointSchema, TrendResponseSchema, ScanComparisonSchema
)


def create_plant_profile(db: Session, schema: PlantCreateSchema) -> PlantItemSchema:
    """Creates a new monitored plant record."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    import uuid
    random_str = uuid.uuid4().hex[:6].upper()
    plant_id = f"PL-{date_str}-{random_str}"

    now_utc = datetime.now(timezone.utc)
    
    plant = PlantModel(
        id=plant_id,
        name=schema.name,
        crop=schema.crop,
        variety=schema.variety,
        growth_stage=schema.growth_stage,
        environment=schema.environment,
        soil_type=schema.soil_type,
        irrigation_method=schema.irrigation_method,
        location=schema.location,
        notes=schema.notes,
        created_at=now_utc,
        last_scan_at=now_utc if schema.initial_analysis_id else None,
        health_status="Monitor",
        analysis_count=0
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)

    # Link initial analysis if provided
    if schema.initial_analysis_id:
        link_analysis_to_plant(db, plant_id, schema.initial_analysis_id)

    return get_plant_item_schema(db, plant)


def link_analysis_to_plant(db: Session, plant_id: str, analysis_id: str, notes: str = None) -> bool:
    """Links an existing analysis record to a plant profile."""
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    analysis = get_analysis_by_id(db, analysis_id)
    
    if not plant or not analysis:
        return False

    # Check if link already exists
    existing = db.query(PlantAnalysisLinkModel).filter(
        PlantAnalysisLinkModel.plant_id == plant_id,
        PlantAnalysisLinkModel.analysis_id == analysis_id
    ).first()

    if not existing:
        link = PlantAnalysisLinkModel(
            plant_id=plant_id,
            analysis_id=analysis_id,
            added_at=datetime.now(timezone.utc),
            notes=notes
        )
        db.add(link)

    # Update plant summary metadata
    plant.last_scan_at = analysis.created_at or datetime.now(timezone.utc)
    plant.latest_disease = analysis.predicted_class
    plant.latest_confidence = float(analysis.confidence)
    plant.latest_severity = float(analysis.severity_percentage)
    
    # Update health status
    if "healthy" in analysis.predicted_class.lower():
        plant.health_status = "Healthy / No supported disease detected"
    elif analysis.severity_percentage >= 30.0 or analysis.confidence < 0.50:
        plant.health_status = "Expert Review Recommended"
    elif analysis.severity_percentage >= 15.0:
        plant.health_status = "Attention Recommended"
    else:
        plant.health_status = "Monitor"

    # Count total linked analyses
    count = db.query(PlantAnalysisLinkModel).filter(PlantAnalysisLinkModel.plant_id == plant_id).count()
    plant.analysis_count = count

    db.commit()
    return True


def list_plant_profiles(db: Session, limit: int = 50, offset: int = 0) -> List[PlantItemSchema]:
    """Lists all monitored plant profiles."""
    plants = db.query(PlantModel).order_by(PlantModel.created_at.desc()).offset(offset).limit(limit).all()
    return [get_plant_item_schema(db, p) for p in plants]


def get_plant_detail(db: Session, plant_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full detail of a plant profile including linked analyses."""
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    if not plant:
        return None

    item = get_plant_item_schema(db, plant).model_dump()
    timeline = get_plant_timeline(db, plant_id)
    trend = get_plant_trend(db, plant_id)
    
    item["timeline"] = [t.model_dump() for t in timeline]
    item["trend"] = trend.model_dump()
    return item


def get_plant_item_schema(db: Session, plant: PlantModel) -> PlantItemSchema:
    """Helper to convert PlantModel to PlantItemSchema."""
    count = db.query(PlantAnalysisLinkModel).filter(PlantAnalysisLinkModel.plant_id == plant.id).count()
    return PlantItemSchema(
        plant_id=plant.id,
        name=plant.name,
        crop=plant.crop,
        variety=plant.variety,
        created_at=plant.created_at.isoformat() if plant.created_at else "",
        last_scan_at=plant.last_scan_at.isoformat() if plant.last_scan_at else None,
        health_status=plant.health_status or "Monitor",
        latest_disease=plant.latest_disease,
        latest_confidence=float(plant.latest_confidence) if plant.latest_confidence is not None else None,
        latest_severity=float(plant.latest_severity) if plant.latest_severity is not None else None,
        analysis_count=count
    )


def get_plant_timeline(db: Session, plant_id: str) -> List[TimelineEventSchema]:
    """Retrieves chronological monitoring timeline for a plant using real stored analyses."""
    links = db.query(PlantAnalysisLinkModel).filter(
        PlantAnalysisLinkModel.plant_id == plant_id
    ).order_by(PlantAnalysisLinkModel.added_at.asc()).all()

    timeline = []
    if not links:
        return timeline

    first_time = links[0].added_at or datetime.now(timezone.utc)

    for idx, link in enumerate(links):
        analysis = get_analysis_by_id(db, link.analysis_id)
        if not analysis:
            continue

        link_time = link.added_at or datetime.now(timezone.utc)
        days_diff = (link_time - first_time).days
        day_label = f"Day {days_diff + 1}" if days_diff >= 0 else f"Scan {idx + 1}"

        timeline.append(TimelineEventSchema(
            timeline_day=day_label,
            timestamp=link_time.isoformat(),
            analysis_id=analysis.id,
            disease=analysis.predicted_class,
            confidence=float(analysis.confidence),
            severity_percentage=float(analysis.severity_percentage),
            severity_level=analysis.severity_level,
            affected_area_pixels=int(analysis.affected_area_pixels),
            image_url=f"/api/uploads/{analysis.image_filename}" if analysis.image_filename else None,
            severity_overlay_url=f"/api/visualizations/{analysis.id}_sev.png" if analysis.severity_overlay_path else None,
            gradcam_overlay_url=f"/api/visualizations/{analysis.id}_gradcam.png" if analysis.gradcam_overlay_path else None
        ))

    return timeline


def get_plant_trend(db: Session, plant_id: str) -> TrendResponseSchema:
    """Generates severity trend data over time for a plant."""
    timeline = get_plant_timeline(db, plant_id)
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    plant_name = plant.name if plant else "Monitored Plant"
    crop = plant.crop if plant else "Crop"

    points = []
    for item in timeline:
        points.append(TrendPointSchema(
            timestamp=item.timestamp,
            label=item.timeline_day,
            severity_percentage=item.severity_percentage,
            confidence=item.confidence,
            disease=item.disease
        ))

    # Evaluate trend direction
    direction = "insufficient_data"
    if len(points) >= 2:
        first_sev = points[0].severity_percentage
        last_sev = points[-1].severity_percentage
        diff = last_sev - first_sev
        if diff <= -3.0:
            direction = "improving"
        elif diff >= 3.0:
            direction = "worsening"
        else:
            direction = "stable"

    return TrendResponseSchema(
        plant_id=plant_id,
        plant_name=plant_name,
        crop=crop,
        trend_label="Observed visual severity trend",
        data_points=points,
        overall_direction=direction,
        disclaimer="This trend represents observed visual affected-area estimates over time and does not imply causal proof."
    )


def compare_scans(db: Session, analysis_id_a: str, analysis_id_b: str) -> ScanComparisonSchema:
    """Compares two analysis scans side-by-side."""
    a = get_analysis_by_id(db, analysis_id_a)
    b = get_analysis_by_id(db, analysis_id_b)

    if not a or not b:
        raise ValueError("One or both analysis IDs were not found.")

    sev_a = float(a.severity_percentage)
    sev_b = float(b.severity_percentage)
    diff = round(sev_b - sev_a, 2)

    if diff > 3.0:
        change_text = f"Observed visible affected area increased by {abs(diff)}% between scans."
    elif diff < -3.0:
        change_text = f"Observed visible affected area decreased by {abs(diff)}% between scans."
    else:
        change_text = f"Observed visible affected area remained virtually stable (difference of {diff}%)."

    time_str = "N/A"
    if a.created_at and b.created_at:
        days = abs((b.created_at - a.created_at).days)
        time_str = f"{days} days apart"

    return ScanComparisonSchema(
        scan_a=a.to_dict(),
        scan_b=b.to_dict(),
        severity_difference=diff,
        severity_change_text=change_text,
        time_between_scans=time_str
    )
