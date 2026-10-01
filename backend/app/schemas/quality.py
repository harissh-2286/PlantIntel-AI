from pydantic import BaseModel
from typing import Dict, List, Any

class Checks(BaseModel):
    format: bool
    resolution: bool
    blur: bool
    brightness: bool
    contrast: bool

class LeafDetection(BaseModel):
    status: str
    message: str

class QualityResponse(BaseModel):
    valid: bool
    quality_score: int
    checks: Checks
    warnings: List[str]
    blur_score: float
    blur_status: str
    brightness_score: float
    brightness_status: str
    contrast_score: float
    contrast_status: str
    leaf_detection: LeafDetection
