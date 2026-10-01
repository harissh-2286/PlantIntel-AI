import numpy as np
from app.schemas.quality import QualityResponse, Checks, LeafDetection
from app.utils.image_utils import load_image_from_bytes, calculate_blur, calculate_brightness, calculate_contrast
from app.config import settings

def analyze_image_quality(file_bytes: bytes, filename: str) -> QualityResponse:
    warnings = []
    
    try:
        pil_image, img_np, img_format = load_image_from_bytes(file_bytes, filename)
    except ValueError:
        return QualityResponse(
            valid=False, quality_score=0,
            checks=Checks(format=False, resolution=False, blur=False, brightness=False, contrast=False),
            warnings=["Unable to read this image. Please upload another image."],
            blur_score=0, blur_status="poor",
            brightness_score=0, brightness_status="poor",
            contrast_score=0, contrast_status="poor",
            leaf_detection=LeafDetection(status="not_implemented", message="Leaf detection will be added with the AI model.")
        )
        
    width, height = pil_image.size
    
    # Check Format: Accept all image formats (PNG, JPG, JPEG, WEBP, BMP, TIFF, GIF, HEIC, AVIF, SVG, ICO, etc.)
    format_pass = (
        isinstance(img_np, np.ndarray) 
        and img_np.size > 0
    )
    if not format_pass:
        warnings.append("Unsupported or corrupted file format.")

        
    # Check Resolution
    resolution_pass = width >= settings.MIN_RESOLUTION and height >= settings.MIN_RESOLUTION
    if not resolution_pass:
        warnings.append("Image resolution is too low for reliable analysis.")
        
    # Check Blur
    blur_score = calculate_blur(img_np)
    blur_pass = blur_score >= settings.BLUR_THRESHOLD
    blur_status = "good" if blur_pass else "poor"
    if not blur_pass:
        warnings.append("Image appears too blurry.")
        
    # Check Brightness
    brightness_score = calculate_brightness(img_np)
    brightness_pass = settings.BRIGHTNESS_LOW_THRESHOLD <= brightness_score <= settings.BRIGHTNESS_HIGH_THRESHOLD
    brightness_status = "good"
    if brightness_score < settings.BRIGHTNESS_LOW_THRESHOLD:
        brightness_status = "poor"
        warnings.append("Image appears too dark.")
    elif brightness_score > settings.BRIGHTNESS_HIGH_THRESHOLD:
        brightness_status = "poor"
        warnings.append("Image appears overexposed.")
        
    # Check Contrast
    contrast_score = calculate_contrast(img_np)
    contrast_pass = contrast_score >= settings.CONTRAST_THRESHOLD
    contrast_status = "good" if contrast_pass else "warning"
    if not contrast_pass:
        warnings.append("Image contrast is low.")
        
    # Calculate overall score
    score = 0
    if format_pass: score += 20
    if resolution_pass: score += 20
    if blur_pass: score += 20
    if brightness_pass: score += 20
    if contrast_pass: score += 20
    
    # If the format or resolution is extremely bad, or couldn't decode
    valid = format_pass and resolution_pass
    
    return QualityResponse(
        valid=valid,
        quality_score=score,
        checks=Checks(
            format=format_pass,
            resolution=resolution_pass,
            blur=blur_pass,
            brightness=brightness_pass,
            contrast=contrast_pass
        ),
        warnings=warnings,
        blur_score=blur_score,
        blur_status=blur_status,
        brightness_score=brightness_score,
        brightness_status=brightness_status,
        contrast_score=contrast_score,
        contrast_status=contrast_status,
        leaf_detection=LeafDetection(
            status="not_implemented", 
            message="Leaf detection will be added with the AI model."
        )
    )
