from pydantic import BaseModel
from typing import List, Optional

class Prediction(BaseModel):
    class_name: str
    confidence: float

class Severity(BaseModel):
    label: str
    affected_area: float

class Explainability(BaseModel):
    gradcam: Optional[str]
    attention_map: Optional[str]
    segmentation: Optional[str]
    iou: Optional[float]
    dice: Optional[float]

class ModelInfo(BaseModel):
    name: str
    version: str

class AnalysisResponse(BaseModel):
    mode: str
    prediction: Prediction
    top_predictions: List[Prediction]
    severity: Severity
    explainability: Explainability
    model: ModelInfo
