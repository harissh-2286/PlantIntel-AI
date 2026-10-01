from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from app.database.database import Base

class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(String(50), primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    image_filename = Column(String(255), nullable=False)
    image_path = Column(String(512), nullable=False)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    model_name = Column(String(100), nullable=False, default="EfficientNetV2-S")
    model_version = Column(String(100), nullable=True)
    model_mode = Column(String(50), nullable=True)
    predicted_class = Column(String(255), nullable=False, index=True)
    predicted_class_id = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False, index=True)
    top_predictions_json = Column(Text, nullable=True)
    severity_percentage = Column(Float, nullable=False, index=True)
    severity_level = Column(String(50), nullable=False, index=True)
    leaf_area_pixels = Column(Integer, nullable=False, default=0)
    affected_area_pixels = Column(Integer, nullable=False, default=0)
    severity_overlay_path = Column(String(512), nullable=True)
    gradcam_heatmap_path = Column(String(512), nullable=True)
    gradcam_overlay_path = Column(String(512), nullable=True)
    attention_heatmap_path = Column(String(512), nullable=True)
    analysis_status = Column(String(50), nullable=False, default="completed", index=True)

    def to_dict(self):
        return {
            "analysis_id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "image_filename": self.image_filename,
            "image_path": self.image_path,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_mode": self.model_mode,
            "predicted_class": self.predicted_class,
            "predicted_class_id": self.predicted_class_id,
            "confidence": round(float(self.confidence), 4),
            "severity_percentage": round(float(self.severity_percentage), 2),
            "severity_level": self.severity_level,
            "leaf_area_pixels": self.leaf_area_pixels,
            "affected_area_pixels": self.affected_area_pixels,
            "analysis_status": self.analysis_status
        }


class PlantModel(Base):
    __tablename__ = "plants"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    crop = Column(String(100), nullable=False, index=True)
    variety = Column(String(100), nullable=True)
    growth_stage = Column(String(100), nullable=True)
    environment = Column(String(100), nullable=True)
    soil_type = Column(String(100), nullable=True)
    irrigation_method = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    last_scan_at = Column(DateTime, nullable=True)
    health_status = Column(String(100), nullable=False, default="Monitor")
    latest_disease = Column(String(255), nullable=True)
    latest_confidence = Column(Float, nullable=True)
    latest_severity = Column(Float, nullable=True)
    analysis_count = Column(Integer, nullable=False, default=0)


class PlantAnalysisLinkModel(Base):
    __tablename__ = "plant_analysis_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(String(50), nullable=False, index=True)
    analysis_id = Column(String(50), nullable=False, index=True)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    notes = Column(Text, nullable=True)

