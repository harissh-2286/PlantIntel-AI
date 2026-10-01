import os
from dotenv import load_dotenv

load_dotenv()

class MLConfig:
    DATASET_PATH: str = os.getenv("DATASET_PATH", "./dataset")
    IMAGE_SIZE: int = int(os.getenv("IMAGE_SIZE", "384"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "16"))
    NUM_EPOCHS: int = int(os.getenv("NUM_EPOCHS", "10"))
    LEARNING_RATE: float = float(os.getenv("LEARNING_RATE", "0.0001"))
    WEIGHT_DECAY: float = float(os.getenv("WEIGHT_DECAY", "0.0001"))
    NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", "0"))
    SEED: int = int(os.getenv("SEED", "42"))
    
    # Phase 5 Model Paths & Modes
    MODEL_MODE: str = os.getenv("MODEL_MODE", "attention")  # "baseline", "attention", "pretrained"
    BASELINE_MODEL_PATH: str = os.getenv("BASELINE_MODEL_PATH", "./models/baseline_efficientnetv2s.pth")
    ATTENTION_MODEL_PATH: str = os.getenv("ATTENTION_MODEL_PATH", "./models/adaptive_attention_efficientnetv2s.pth")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/adaptive_attention_efficientnetv2s.pth")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "./models")
    RESEARCH_DIR: str = os.getenv("RESEARCH_DIR", "./research")
    
    # Phase 6 Severity Config
    SEVERITY_MODE: str = os.getenv("SEVERITY_MODE", "prototype")  # "prototype", "segmentation"
    SEVERITY_MIN_LEAF_PIXELS: int = int(os.getenv("SEVERITY_MIN_LEAF_PIXELS", "500"))
    SEVERITY_MIN_REGION_SIZE: int = int(os.getenv("SEVERITY_MIN_REGION_SIZE", "5"))

    # Phase 7 Grad-CAM++ Config
    GRADCAM_TARGET_LAYER: str = os.getenv("GRADCAM_TARGET_LAYER", "auto")
    GRADCAM_COLORMAP: str = os.getenv("GRADCAM_COLORMAP", "JET")

    DEVICE: str = os.getenv("DEVICE", "auto")
    PATIENCE: int = int(os.getenv("PATIENCE", "3"))
    REDUCTION_RATIO: int = int(os.getenv("REDUCTION_RATIO", "8"))
    CLASS_BALANCING: str = os.getenv("CLASS_BALANCING", "weighted_ce")  # "none", "weighted_ce", "weighted_sampler"
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.50"))

    def to_dict(self):
        return {
            "DATASET_PATH": self.DATASET_PATH,
            "IMAGE_SIZE": self.IMAGE_SIZE,
            "BATCH_SIZE": self.BATCH_SIZE,
            "NUM_EPOCHS": self.NUM_EPOCHS,
            "LEARNING_RATE": self.LEARNING_RATE,
            "WEIGHT_DECAY": self.WEIGHT_DECAY,
            "NUM_WORKERS": self.NUM_WORKERS,
            "SEED": self.SEED,
            "MODEL_MODE": self.MODEL_MODE,
            "BASELINE_MODEL_PATH": self.BASELINE_MODEL_PATH,
            "ATTENTION_MODEL_PATH": self.ATTENTION_MODEL_PATH,
            "MODEL_PATH": self.MODEL_PATH,
            "MODEL_DIR": self.MODEL_DIR,
            "RESEARCH_DIR": self.RESEARCH_DIR,
            "SEVERITY_MODE": self.SEVERITY_MODE,
            "SEVERITY_MIN_LEAF_PIXELS": self.SEVERITY_MIN_LEAF_PIXELS,
            "SEVERITY_MIN_REGION_SIZE": self.SEVERITY_MIN_REGION_SIZE,
            "GRADCAM_TARGET_LAYER": self.GRADCAM_TARGET_LAYER,
            "GRADCAM_COLORMAP": self.GRADCAM_COLORMAP,
            "DEVICE": self.DEVICE,
            "PATIENCE": self.PATIENCE,
            "REDUCTION_RATIO": self.REDUCTION_RATIO,
            "CLASS_BALANCING": self.CLASS_BALANCING,
            "CONFIDENCE_THRESHOLD": self.CONFIDENCE_THRESHOLD
        }

ml_config = MLConfig()
