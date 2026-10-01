import cv2
import numpy as np
import io
import time
import base64
from PIL import Image
from app.ml.config import ml_config

def categorize_severity_level(percentage: float) -> str:
    """
    Categorizes affected area percentage into project severity levels:
    0–5%: Minimal
    > 5–20%: Mild
    > 20–40%: Moderate
    > 40–60%: Severe
    > 60%: Very Severe
    """
    if percentage <= 5.0:
        return "Minimal"
    elif percentage <= 20.0:
        return "Mild"
    elif percentage <= 40.0:
        return "Moderate"
    elif percentage <= 60.0:
        return "Severe"
    else:
        return "Very Severe"

def generate_severity_overlay_base64(image_np: np.ndarray, leaf_mask: np.ndarray, affected_mask: np.ndarray) -> str:
    """
    Generates a visual overlay highlighting the estimated leaf boundary (green contour)
    and estimated affected disease regions (semi-transparent red mask).
    """
    overlay = image_np.copy()
    
    # Red color for affected regions [R, G, B]
    red_color = np.array([230, 50, 50], dtype=np.uint8)
    
    # Blended red overlay on affected pixels
    affected_bool = affected_mask > 0
    if np.any(affected_bool):
        blended = (image_np[affected_bool].astype(np.float32) * 0.4 + red_color.astype(np.float32) * 0.6).astype(np.uint8)
        overlay[affected_bool] = blended
    
    # Draw green contours around visible leaf area
    contours, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (40, 200, 60), 2)

    pil_img = Image.fromarray(overlay)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"

def estimate_severity_prototype(
    image_np: np.ndarray,
    min_leaf_pixels: int = None,
    min_region_size: int = None
):
    """
    Prototype Image-Processing Severity Estimation Pipeline:
    Leaf Image → HSV/Lab Color Space → Leaf Region Mask → Affected Region Candidate Detection
    → Morphological Filtering & Connected Components → Affected Area Percentage → Severity Level.
    """
    start_time = time.time()

    if min_leaf_pixels is None:
        min_leaf_pixels = ml_config.SEVERITY_MIN_LEAF_PIXELS
    if min_region_size is None:
        min_region_size = ml_config.SEVERITY_MIN_REGION_SIZE

    h, w, _ = image_np.shape

    # 1. Color Space Transformations
    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB)

    # 2. Leaf Region Masking (Denominator: Visible Leaf Area)
    # Healthy green hue range: 20-95
    green_mask = cv2.inRange(hsv, np.array([20, 20, 20]), np.array([95, 255, 255]))
    # Yellowish/brownish leaf hue range: 10-25
    brown_mask = cv2.inRange(hsv, np.array([10, 20, 20]), np.array([25, 255, 255]))
    
    # Combine to estimate total visible leaf area
    raw_leaf_mask = cv2.bitwise_or(green_mask, brown_mask)

    # Morphological cleaning of leaf mask
    kernel_5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    leaf_mask = cv2.morphologyEx(raw_leaf_mask, cv2.MORPH_CLOSE, kernel_5)
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, kernel_5)

    leaf_pixels = int(np.count_nonzero(leaf_mask))

    # Check visible leaf region validity
    if leaf_pixels < min_leaf_pixels:
        inference_time = (time.time() - start_time) * 1000
        return {
            "status": "unreliable",
            "message": "Unable to reliably detect visible leaf region. Please upload an image with the leaf clearly visible against the background.",
            "mode": ml_config.SEVERITY_MODE,
            "severity": {
                "percentage": 0.0,
                "level": "Unknown"
            },
            "area": {
                "leaf_pixels": leaf_pixels,
                "affected_pixels": 0
            },
            "visualization": None,
            "severity_inference_time_ms": round(inference_time, 2)
        }

    # 3. Affected Region Candidate Detection (Inside Leaf Mask ONLY)
    # Chlorosis (yellowing inside leaf mask)
    yellow_candidates = cv2.inRange(hsv, np.array([18, 35, 40]), np.array([38, 255, 255]))
    # Necrosis/Lesions (brown spots / dark spots inside leaf mask)
    brown_candidates = cv2.inRange(hsv, np.array([0, 20, 20]), np.array([18, 255, 200]))
    dark_candidates = cv2.inRange(hsv, np.array([0, 15, 0]), np.array([180, 255, 60]))

    affected_candidates = cv2.bitwise_or(yellow_candidates, brown_candidates)
    affected_candidates = cv2.bitwise_or(affected_candidates, dark_candidates)

    # Mask affected candidates strictly within the leaf mask
    raw_affected_mask = cv2.bitwise_and(affected_candidates, leaf_mask)

    # Morphological cleaning (noise removal)
    kernel_3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean_affected_mask = cv2.morphologyEx(raw_affected_mask, cv2.MORPH_OPEN, kernel_3)
    clean_affected_mask = cv2.morphologyEx(clean_affected_mask, cv2.MORPH_CLOSE, kernel_3)

    # Connected Components Analysis (Filter out noise components < min_region_size)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(clean_affected_mask)
    filtered_affected_mask = np.zeros_like(clean_affected_mask)

    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_region_size:
            filtered_affected_mask[labels == i] = 255

    affected_pixels = int(np.count_nonzero(filtered_affected_mask))

    # 4. Numerical Validation & Percentage Calculation
    affected_pixels = min(affected_pixels, leaf_pixels)
    percentage = round((affected_pixels / float(leaf_pixels)) * 100.0, 2)
    percentage = max(0.0, min(100.0, percentage))

    level = categorize_severity_level(percentage)

    # 5. Generate Visualization Overlay Data URL
    visualization_b64 = generate_severity_overlay_base64(image_np, leaf_mask, filtered_affected_mask)

    inference_time = (time.time() - start_time) * 1000

    return {
        "status": "success",
        "severity_status": "reliable",
        "mode": ml_config.SEVERITY_MODE,
        "severity": {
            "percentage": percentage,
            "level": level
        },
        "area": {
            "leaf_pixels": leaf_pixels,
            "affected_pixels": affected_pixels
        },
        "visualization": {
            "overlay_base64": visualization_b64,
            "mask_label": "Estimated affected region"
        },
        "severity_inference_time_ms": round(inference_time, 2)
    }

def estimate_disease_severity(image_bytes: bytes):
    """
    Main Severity Estimation Service wrapper.
    Reads image bytes and executes severity analysis based on configured SEVERITY_MODE.
    """
    from app.utils.image_utils import load_image_from_bytes
    _, image_np, _ = load_image_from_bytes(image_bytes)
    
    if ml_config.SEVERITY_MODE == "prototype":
        return estimate_severity_prototype(image_np)
    else:
        # Future segmentation mode placeholder
        return estimate_severity_prototype(image_np)
