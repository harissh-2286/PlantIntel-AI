from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repository import get_analysis_by_id
from app.plant_health.schemas import GuidanceRequest, GuidanceResponse
from app.plant_health.recommendation_engine import generate_plant_guidance
from app.plant_health.knowledge_base import (
    KNOWLEDGE_BASE_VERSION, SUPPORTED_CROPS, DISEASE_KNOWLEDGE_BASE
)

router = APIRouter()

@router.post("/guidance", response_model=GuidanceResponse)
async def get_plant_guidance_endpoint(
    req: GuidanceRequest,
    db: Session = Depends(get_db)
):
    """
    Generates structured, confidence-aware Plant Health Guidance for a given analysis_id.
    """
    analysis = get_analysis_by_id(db, req.analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis ID '{req.analysis_id}' not found.")

    analysis_dict = analysis.to_dict()
    guidance = generate_plant_guidance(
        analysis_dict=analysis_dict,
        crop=req.crop,
        growth_stage=req.growth_stage,
        environment=req.environment
    )
    return guidance


@router.get("/guidance/crops")
async def get_supported_crops():
    """
    Returns supported crop profiles and knowledge base version.
    """
    crops_list = []
    for key, val in SUPPORTED_CROPS.items():
        crops_list.append({
            "crop_id": val["crop_id"],
            "crop_name": val["crop_name"],
            "common_name": val["common_name"],
            "growth_stages": val["growth_stages"],
            "water_requirements": val["water_requirements"]
        })
    return {
        "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
        "supported_crops": crops_list,
        "note": "Supported crops. Additional crops can be added to the knowledge base."
    }


@router.get("/guidance/diseases")
async def get_supported_diseases():
    """
    Returns list of supported disease knowledge base entries.
    """
    diseases = []
    for key, val in DISEASE_KNOWLEDGE_BASE.items():
        diseases.append({
            "predicted_class": key,
            "disease_id": val.get("disease_id"),
            "disease_name": val.get("disease_name"),
            "affected_crops": val.get("affected_crops"),
            "monitoring_interval_days": val.get("monitoring_interval_days")
        })
    return {
        "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
        "total_diseases": len(diseases),
        "diseases": diseases
    }
