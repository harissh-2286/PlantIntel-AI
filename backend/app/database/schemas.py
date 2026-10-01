from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class AnalysisCreateSchema(BaseModel):
    id: str = Field(..., description="Unique Analysis ID e.g. PI-20261001-A1B2C3")
    image_filename: str
    image_path: str
    image_width: Optional[int] = Field(default=None, ge=0)
    image_height: Optional[int] = Field(default=None, ge=0)
    model_name: str = "EfficientNetV2-S"
    model_version: Optional[str] = None
    model_mode: Optional[str] = None
    predicted_class: str
    predicted_class_id: int = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    top_predictions_json: Optional[str] = None
    severity_percentage: float = Field(..., ge=0.0, le=100.0)
    severity_level: str
    leaf_area_pixels: int = Field(..., ge=0)
    affected_area_pixels: int = Field(..., ge=0)
    severity_overlay_path: Optional[str] = None
    gradcam_heatmap_path: Optional[str] = None
    gradcam_overlay_path: Optional[str] = None
    attention_heatmap_path: Optional[str] = None
    analysis_status: str = "completed"

    @field_validator("affected_area_pixels")
    @classmethod
    def check_area_pixels(cls, affected_pixels: int, values):
        leaf_pixels = values.data.get("leaf_area_pixels", 0)
        if affected_pixels > leaf_pixels and leaf_pixels > 0:
            raise ValueError(f"Affected area pixels ({affected_pixels}) cannot exceed total leaf area pixels ({leaf_pixels}).")
        return affected_pixels

class AnalysisItemSchema(BaseModel):
    analysis_id: str
    created_at: str
    predicted_class: str
    predicted_class_id: int
    confidence: float
    severity_percentage: float
    severity_level: str
    analysis_status: str
    image_url: Optional[str] = None

class HistoryResponseSchema(BaseModel):
    items: List[AnalysisItemSchema]
    total: int
    limit: int
    offset: int

class HistoryStatsSchema(BaseModel):
    total_analyses: int
    diseases_detected_count: int
    average_severity_percentage: float
    severity_distribution: Dict[str, int]
    disease_distribution: Dict[str, int]
