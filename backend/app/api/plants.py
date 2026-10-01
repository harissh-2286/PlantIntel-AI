"""
Plant Health Monitoring API Endpoints
POST   /api/plants                     - Create plant profile
GET    /api/plants                     - List all plant profiles
GET    /api/plants/{plant_id}          - Get plant detail + timeline + trend
POST   /api/plants/{plant_id}/analysis - Link an analysis to a plant
GET    /api/plants/{plant_id}/timeline - Get chronological monitoring timeline
GET    /api/plants/{plant_id}/trend    - Get severity trend chart data
GET    /api/plants/{plant_id}/compare  - Compare two scans side-by-side
GET    /api/plants/dashboard           - Monitoring dashboard summary
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.plant_health.schemas import (
    PlantCreateSchema,
    PlantAnalysisLinkSchema,
    PlantItemSchema,
)
from app.plant_health.monitoring_service import (
    create_plant_profile,
    link_analysis_to_plant,
    list_plant_profiles,
    get_plant_detail,
    get_plant_timeline,
    get_plant_trend,
    compare_scans,
)
from app.plant_health.alert_service import generate_plant_alerts
from app.database.models import PlantModel, PlantAnalysisLinkModel

router = APIRouter()


# ─────────────────────────────────────────────
# POST /api/plants — Create a monitored plant profile
# ─────────────────────────────────────────────
@router.post("/plants", response_model=PlantItemSchema, status_code=201)
async def create_plant(schema: PlantCreateSchema, db: Session = Depends(get_db)):
    """
    Creates a new monitored plant/field record.
    Optionally links an existing analysis as the first scan.
    """
    try:
        plant = create_plant_profile(db, schema)
        return plant
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plant profile: {str(e)}")


# ─────────────────────────────────────────────
# GET /api/plants — List all plant profiles
# ─────────────────────────────────────────────
@router.get("/plants")
async def list_plants(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns a paginated list of all monitored plant profiles.
    """
    plants = list_plant_profiles(db, limit=limit, offset=offset)
    total = db.query(PlantModel).count()
    return {
        "plants": [p.model_dump() for p in plants],
        "total": total,
        "limit": limit,
        "offset": offset
    }


# ─────────────────────────────────────────────
# GET /api/plants/dashboard — Monitoring Dashboard Summary
# ─────────────────────────────────────────────
@router.get("/plants/dashboard")
async def get_monitoring_dashboard(db: Session = Depends(get_db)):
    """
    Returns aggregated monitoring dashboard statistics including:
    plants monitored, recently analyzed, repeated conditions, low-confidence cases.
    """
    total_plants = db.query(PlantModel).count()

    plants = db.query(PlantModel).order_by(PlantModel.last_scan_at.desc()).limit(5).all()
    recently_analyzed = []
    for p in plants:
        if p.last_scan_at:
            recently_analyzed.append({
                "plant_id": p.id,
                "name": p.name,
                "crop": p.crop,
                "last_scan_at": p.last_scan_at.isoformat(),
                "health_status": p.health_status,
                "latest_disease": p.latest_disease,
                "latest_severity": float(p.latest_severity) if p.latest_severity is not None else None,
                "latest_confidence": float(p.latest_confidence) if p.latest_confidence is not None else None,
            })

    # Count by health status
    health_counts = {}
    all_plants = db.query(PlantModel).all()
    for p in all_plants:
        status = p.health_status or "Monitor"
        health_counts[status] = health_counts.get(status, 0) + 1

    # Low-confidence cases (latest_confidence < 0.60)
    low_conf_plants = db.query(PlantModel).filter(
        PlantModel.latest_confidence < 0.60,
        PlantModel.latest_confidence.isnot(None)
    ).count()

    # Expert review needed
    expert_review_count = db.query(PlantModel).filter(
        PlantModel.health_status == "Expert Review Recommended"
    ).count()

    # Attention needed
    attention_count = db.query(PlantModel).filter(
        PlantModel.health_status == "Attention Recommended"
    ).count()

    return {
        "total_plants_monitored": total_plants,
        "recently_analyzed": recently_analyzed,
        "health_status_distribution": health_counts,
        "low_confidence_cases": low_conf_plants,
        "expert_review_recommended_count": expert_review_count,
        "attention_recommended_count": attention_count,
        "note": "Dashboard shows real monitored plant data. No fabricated records are generated."
    }


# ─────────────────────────────────────────────
# GET /api/plants/{plant_id} — Get full plant detail
# ─────────────────────────────────────────────
@router.get("/plants/{plant_id}")
async def get_plant(plant_id: str, db: Session = Depends(get_db)):
    """
    Returns full plant profile including timeline, trend data, and active alerts.
    """
    _validate_plant_id(plant_id)
    detail = get_plant_detail(db, plant_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Plant profile '{plant_id}' not found.")

    # Attach alert data
    try:
        alerts = generate_plant_alerts(db, plant_id)
        detail["alerts"] = alerts
    except Exception:
        detail["alerts"] = []

    return detail


# ─────────────────────────────────────────────
# POST /api/plants/{plant_id}/analysis — Link analysis to plant
# ─────────────────────────────────────────────
@router.post("/plants/{plant_id}/analysis")
async def add_analysis_to_plant(
    plant_id: str,
    schema: PlantAnalysisLinkSchema,
    db: Session = Depends(get_db)
):
    """
    Links an existing analysis record to a monitored plant profile.
    Updates the plant's health status and latest scan metadata.
    """
    _validate_plant_id(plant_id)
    success = link_analysis_to_plant(db, plant_id, schema.analysis_id, schema.notes)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Plant '{plant_id}' or Analysis '{schema.analysis_id}' not found."
        )

    # Return updated plant profile
    detail = get_plant_detail(db, plant_id)
    return {
        "status": "success",
        "message": f"Analysis {schema.analysis_id} linked to plant {plant_id}.",
        "plant": detail
    }


# ─────────────────────────────────────────────
# GET /api/plants/{plant_id}/timeline — Chronological timeline
# ─────────────────────────────────────────────
@router.get("/plants/{plant_id}/timeline")
async def get_timeline(plant_id: str, db: Session = Depends(get_db)):
    """
    Returns the chronological monitoring timeline for a plant.
    Each event is a real stored analysis — no fabricated records.
    """
    _validate_plant_id(plant_id)
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant '{plant_id}' not found.")

    timeline = get_plant_timeline(db, plant_id)
    return {
        "plant_id": plant_id,
        "plant_name": plant.name,
        "crop": plant.crop,
        "timeline": [t.model_dump() for t in timeline],
        "total_scans": len(timeline),
        "disclaimer": "Timeline uses only real stored analyses. No synthetic data is generated."
    }


# ─────────────────────────────────────────────
# GET /api/plants/{plant_id}/trend — Severity trend data
# ─────────────────────────────────────────────
@router.get("/plants/{plant_id}/trend")
async def get_trend(plant_id: str, db: Session = Depends(get_db)):
    """
    Returns severity trend chart data over time.
    Labeled as 'Observed visual severity trend' — not treatment effectiveness.
    """
    _validate_plant_id(plant_id)
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant '{plant_id}' not found.")

    trend = get_plant_trend(db, plant_id)
    return trend.model_dump()


# ─────────────────────────────────────────────
# GET /api/plants/{plant_id}/compare — Compare two scans
# ─────────────────────────────────────────────
@router.get("/plants/{plant_id}/compare")
async def compare_plant_scans(
    plant_id: str,
    scan_a: str = Query(..., description="Analysis ID of the first scan"),
    scan_b: str = Query(..., description="Analysis ID of the second scan"),
    db: Session = Depends(get_db)
):
    """
    Compares two scans side-by-side for the same plant.
    Shows severity difference without implying causality.
    """
    _validate_plant_id(plant_id)
    try:
        comparison = compare_scans(db, scan_a, scan_b)
        return comparison.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# ─────────────────────────────────────────────
# DELETE /api/plants/{plant_id} — Remove plant profile
# ─────────────────────────────────────────────
@router.delete("/plants/{plant_id}")
async def delete_plant(plant_id: str, db: Session = Depends(get_db)):
    """
    Removes a plant profile and all its analysis links.
    Does NOT delete the underlying analysis records.
    """
    _validate_plant_id(plant_id)
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant '{plant_id}' not found.")

    # Remove all links
    db.query(PlantAnalysisLinkModel).filter(PlantAnalysisLinkModel.plant_id == plant_id).delete()
    db.delete(plant)
    db.commit()

    return {"status": "success", "message": f"Plant profile '{plant_id}' and its analysis links removed."}


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────
def _validate_plant_id(plant_id: str):
    if not plant_id or ".." in plant_id or "/" in plant_id or "\\" in plant_id:
        raise HTTPException(status_code=400, detail="Invalid Plant ID format.")
