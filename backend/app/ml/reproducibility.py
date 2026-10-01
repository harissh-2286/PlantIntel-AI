import os
import sys
import random
import platform
import hashlib
import numpy as np
import torch
import cv2
import torchvision
from app.config import settings

def set_seed(seed: int = 42):
    """
    Sets global random seeds for Python, NumPy, and PyTorch for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def get_system_environment_info():
    """
    Returns system software versions, device info, and hardware configuration.
    """
    device_name = "CPU"
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
        except Exception:
            device_name = "CUDA GPU"

    return {
        "python_version": sys.version.split()[0],
        "pytorch_version": torch.__version__,
        "torchvision_version": torchvision.__version__,
        "opencv_version": cv2.__version__,
        "backend_version": "1.0.0",
        "frontend_version": "1.0.0",
        "device": str(settings.DEVICE),
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": device_name if torch.cuda.is_available() else None,
        "operating_system": f"{platform.system()} {platform.release()}"
    }

def compute_file_sha256(filepath: str) -> str:
    """
    Computes cryptographic SHA-256 checksum of a file.
    """
    if not os.path.exists(filepath):
        return "N/A (File not found)"
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
