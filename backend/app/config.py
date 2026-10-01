import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "PlantIntel AI"
    PHASE: int = 7
    
    # Model Config
    MODEL_MODE: str = os.getenv("MODEL_MODE", "attention") # "baseline", "attention", "pretrained"
    SEVERITY_MODE: str = os.getenv("SEVERITY_MODE", "prototype") # "prototype", "segmentation"
    GRADCAM_TARGET_LAYER: str = os.getenv("GRADCAM_TARGET_LAYER", "auto")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/adaptive_attention_efficientnetv2s.pth")
    BASELINE_MODEL_PATH: str = os.getenv("BASELINE_MODEL_PATH", "./models/baseline_efficientnetv2s.pth")
    ATTENTION_MODEL_PATH: str = os.getenv("ATTENTION_MODEL_PATH", "./models/adaptive_attention_efficientnetv2s.pth")
    DEVICE: str = os.getenv("DEVICE", "auto")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.50"))
    
    # Image Quality Config
    MIN_RESOLUTION: int = 256
    BLUR_THRESHOLD: float = 80.0
    BRIGHTNESS_LOW_THRESHOLD: float = 40.0
    BRIGHTNESS_HIGH_THRESHOLD: float = 220.0
    CONTRAST_THRESHOLD: float = 30.0

settings = Settings()

