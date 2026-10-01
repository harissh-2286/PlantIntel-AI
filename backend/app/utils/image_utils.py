import cv2
import numpy as np
from PIL import Image
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def calculate_blur(image_np: np.ndarray) -> float:
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def calculate_brightness(image_np: np.ndarray) -> float:
    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
    return hsv[..., 2].mean()

def calculate_contrast(image_np: np.ndarray) -> float:
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    return gray.std()

def load_image_from_bytes(data: bytes, filename: str = "") -> tuple[Image.Image, np.ndarray, str]:
    img_format = ""
    if filename and "." in filename:
        img_format = filename.rsplit(".", 1)[-1].upper()

    try:
        raw_pil = Image.open(io.BytesIO(data))
        orig_format = raw_pil.format or ""
        
        # Reopen because verify/inspect messes with file pointer
        pil_image = Image.open(io.BytesIO(data))
        
        # Convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            
        final_format = orig_format or img_format or pil_image.format or "PNG"
        img_np = np.array(pil_image)
        return pil_image, img_np, final_format
    except Exception as e:
        # Fallback to OpenCV decoding if PIL fails
        try:
            nparr = np.frombuffer(data, np.uint8)
            bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if bgr is not None and bgr.size > 0:
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb)
                final_format = img_format or "IMAGE"
                return pil_image, rgb, final_format
        except Exception:
            pass
        raise ValueError(f"Unable to read image: {e}")


def heatmap_to_base64(heatmap_np: np.ndarray, target_size=(384, 384)) -> str:
    """
    Converts a normalized [H, W] float heatmap numpy array into a base64 encoded PNG data URL.
    Applies Jet colormap for visualization.
    """
    # Normalize 0..1
    h_min, h_max = heatmap_np.min(), heatmap_np.max()
    norm_heatmap = (heatmap_np - h_min) / (h_max - h_min + 1e-8)
    
    # Resize to target size
    resized = cv2.resize(norm_heatmap, target_size, interpolation=cv2.INTER_CUBIC)
    
    # Apply colormap (Jet)
    uint8_map = np.uint8(255 * resized)
    color_map = cv2.applyColorMap(uint8_map, cv2.COLORMAP_JET)
    color_map_rgb = cv2.cvtColor(color_map, cv2.COLOR_BGR2RGB)
    
    pil_img = Image.fromarray(color_map_rgb)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"
