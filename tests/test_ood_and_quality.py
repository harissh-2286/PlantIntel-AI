import os
import sys
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.image_quality import analyze_image_quality
from app.ml.model import ai_model

def create_synthetic_image(mode="blank", color=(255, 255, 255), size=(300, 300)):
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    if mode == "text":
        draw.text((20, 50), "PLANTINTEL AI DOCUMENT TEST", fill=(0, 0, 0))
        draw.text((20, 100), "Sample out-of-domain text input", fill=(0, 0, 0))
    elif mode == "building":
        draw.rectangle([50, 50, 250, 250], fill=(120, 120, 120), outline=(0, 0, 0))
        for x in range(70, 230, 30):
            for y in range(70, 230, 30):
                draw.rectangle([x, y, x+15, y+15], fill=(200, 200, 255))
    elif mode == "noise":
        arr = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
        img = Image.fromarray(arr)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_out_of_domain_inputs():
    print("[TEST 1/2] Testing Out-of-Domain (OOD) Non-Leaf Inputs...")
    
    # 1. Blank image
    blank_bytes = create_synthetic_image("blank", color=(240, 240, 240))
    q_blank = analyze_image_quality(blank_bytes, "blank.jpg")
    assert not q_blank.valid or len(q_blank.warnings) > 0, "Blank image should trigger low contrast/blur warning!"
    print("  -> Blank image handled cleanly (Quality score:", q_blank.quality_score, ").")

    # 2. Text Document
    text_bytes = create_synthetic_image("text", color=(255, 255, 255))
    q_text = analyze_image_quality(text_bytes, "document.jpg")
    print("  -> Text document image quality check executed (Score:", q_text.quality_score, ").")

    # 3. Building Simulation
    building_bytes = create_synthetic_image("building")
    q_build = analyze_image_quality(building_bytes, "building.jpg")
    print("  -> Building simulation image handled cleanly.")

    # 4. Random Noise
    noise_bytes = create_synthetic_image("noise")
    q_noise = analyze_image_quality(noise_bytes, "noise.jpg")
    print("  -> Random noise image handled cleanly.")

def test_quality_degradation_robustness():
    print("[TEST 2/2] Testing Image Quality Degradation (Blur, Dark, Bright)...")
    
    # 1. Dark Image
    dark_bytes = create_synthetic_image("blank", color=(10, 10, 10))
    q_dark = analyze_image_quality(dark_bytes, "dark.jpg")
    assert q_dark.brightness_status in ["warning", "poor"], "Dark image did not trigger brightness warning!"
    print("  -> Dark image triggered low brightness warning correctly.")

    # 2. Overexposed Bright Image
    bright_bytes = create_synthetic_image("blank", color=(250, 250, 250))
    q_bright = analyze_image_quality(bright_bytes, "bright.jpg")
    assert q_bright.brightness_status in ["warning", "poor"], "Overexposed image did not trigger brightness warning!"
    print("  -> Overexposed image triggered brightness warning correctly.")

    # 3. Blurred Image
    img = Image.new("RGB", (300, 300), color=(50, 180, 50))
    blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
    buf = io.BytesIO()
    blurred.save(buf, format="JPEG")
    blur_bytes = buf.getvalue()
    
    q_blur = analyze_image_quality(blur_bytes, "blur.jpg")
    assert q_blur.blur_status in ["warning", "poor"], "Blurred image did not trigger sharpness warning!"
    print("  -> Blurred image triggered sharpness warning correctly.")

def run_all_ood_tests():
    print("==================================================")
    print("  PLANTINTEL AI - OOD & QUALITY ROBUSTNESS TESTS  ")
    print("==================================================")
    test_out_of_domain_inputs()
    test_quality_degradation_robustness()
    print("==================================================")
    print("  ALL OOD & QUALITY ROBUSTNESS TESTS PASSED (2/2)! ")
    print("==================================================")

if __name__ == "__main__":
    run_all_ood_tests()
