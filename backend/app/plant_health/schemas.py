from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Source Info ---
class SourceInfo(BaseModel):
    source_type: str = Field(..., description="e.g. extension_service, university, government, research_paper, product_label")
    source_title: str
    source_url: str
    source_date: Optional[str] = None

# --- Recommendation Card ---
class RecommendationCard(BaseModel):
    id: str
    title: str
    description: str
    why_it_matters: str
    priority: str = Field(..., description="Immediate, High, Medium, Preventive, Informational")
    applicable_condition: str
    source: Optional[SourceInfo] = None

# --- Section Guidance ---
class GuidanceResponse(BaseModel):
    analysis_id: str
    knowledge_base_version: str = "v1.0"
    crop: str
    growth_stage: Optional[str] = "unspecified"
    environment: Optional[str] = "unspecified"
    
    # Diagnosis & Confidence
    predicted_class: str
    confidence: float
    confidence_level: str  # high, medium, low
    is_confirmed: bool
    status_label: str  # e.g. "Possible condition" or "Confirmed disease"
    health_status: str  # "Healthy", "Monitor", "Attention Recommended", "Expert Review Recommended"
    health_indicator_score: int  # 0 to 100 Plant Health Indicator
    
    # Severity
    severity_percentage: float
    severity_level: str
    severity_interpretation: str
    
    # Guidance Sections
    immediate_actions: List[RecommendationCard]
    prevention: List[RecommendationCard]
    water_and_environment: List[RecommendationCard]
    nutrition_guidance: List[RecommendationCard]
    natural_and_biological_options: List[RecommendationCard]
    what_to_avoid: List[RecommendationCard]
    
    # Comparisons & Educational Notes
    disease_vs_nutrient_note: str
    chemical_management_reference: Optional[str] = None
    resistance_management_note: Optional[str] = None
    integrated_pest_management_note: str
    
    # Monitoring & Escalation
    monitoring_interval_days: int
    recommended_next_check: str
    when_to_seek_expert_advice: List[str]
    
    # Sources
    sources: List[SourceInfo]
    disclaimer: str

# --- Guidance Request Input ---
class GuidanceRequest(BaseModel):
    analysis_id: str
    crop: Optional[str] = None
    variety: Optional[str] = None
    growth_stage: Optional[str] = "unspecified"
    environment: Optional[str] = "unspecified"  # indoor, outdoor, greenhouse, field
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None

# --- Plant Profile Schemas ---
class PlantCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Friendly plant or field identifier")
    crop: str
    variety: Optional[str] = None
    growth_stage: Optional[str] = "unspecified"
    environment: Optional[str] = "unspecified"
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    initial_analysis_id: Optional[str] = None

class PlantAnalysisLinkSchema(BaseModel):
    analysis_id: str
    notes: Optional[str] = None

class PlantItemSchema(BaseModel):
    plant_id: str
    name: str
    crop: str
    variety: Optional[str] = None
    created_at: str
    last_scan_at: Optional[str] = None
    health_status: str
    latest_disease: Optional[str] = None
    latest_confidence: Optional[float] = None
    latest_severity: Optional[float] = None
    analysis_count: int = 0

class TimelineEventSchema(BaseModel):
    timeline_day: str  # e.g. "Day 1", "Day 4"
    timestamp: str
    analysis_id: str
    disease: str
    confidence: float
    severity_percentage: float
    severity_level: str
    affected_area_pixels: int
    image_url: Optional[str] = None
    severity_overlay_url: Optional[str] = None
    gradcam_overlay_url: Optional[str] = None

class TrendPointSchema(BaseModel):
    timestamp: str
    label: str  # e.g. "Day 1"
    severity_percentage: float
    confidence: float
    disease: str

class TrendResponseSchema(BaseModel):
    plant_id: str
    plant_name: str
    crop: str
    trend_label: str = "Observed visual severity trend"
    data_points: List[TrendPointSchema]
    overall_direction: str  # "improving", "worsening", "stable", "insufficient_data"
    disclaimer: str = "This trend represents observed visual affected-area estimates over time and does not imply causal proof."

class ScanComparisonSchema(BaseModel):
    scan_a: Dict[str, Any]
    scan_b: Dict[str, Any]
    severity_difference: float
    severity_change_text: str
    time_between_scans: str
