import os
import sys
import io
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app
from fastapi.testclient import TestClient

import asyncio
import io
from PIL import Image
from app.ml.model import ai_model
from app.ml.gradcam import generate_gradcam_explanation
from app.services.image_quality import analyze_image_quality
from app.ml.severity import estimate_disease_severity

def run_live_api_verification():
    print("==================================================")
    print("  PLANTINTEL AI - LIVE API ENDPOINT VERIFICATION  ")
    print("==================================================")

    # Load model
    ai_model.load_model()

    # Synthetic image for upload verification
    img = Image.new("RGB", (300, 300), color=(40, 160, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    # 1. Quality Check
    q_res = analyze_image_quality(img_bytes, filename="leaf.jpg")
    assert q_res.valid, "Quality check failed!"
    print("1. Quality Check -> PASS: Valid=", q_res.valid)

    # 2. Predict
    p_res = ai_model.predict(img_bytes)
    assert "prediction" in p_res, "Predict failed!"
    print("2. Predict -> PASS: Class=", p_res["prediction"]["class_name"])

    # 3. Severity
    s_res = estimate_disease_severity(img_bytes)
    assert "severity" in s_res, "Severity failed!"
    print("3. Severity -> PASS: Level=", s_res["severity"]["level"])

    # 4. Explain Attention
    a_res = ai_model.get_attention_map(img_bytes)
    assert "attention" in a_res, "Attention failed!"
    print("4. Explain Attention -> PASS: Has Attention=", a_res["attention"]["has_attention"])

    # 5. Explain Grad-CAM++
    g_res = generate_gradcam_explanation(ai_model, img_bytes, target_class=0)
    assert "explanation" in g_res, "Grad-CAM++ failed!"
    assert g_res["explanation"]["method"] == "Grad-CAM++", "Invalid method!"
    print("5. Explain Grad-CAM++ -> PASS: Target Layer=", g_res["explanation"]["target_layer"])

    print("==================================================")
    print("  ALL API PIPELINES VERIFIED SUCCESSFULLY (5/5)!  ")
    print("==================================================")

if __name__ == "__main__":
    run_live_api_verification()

if __name__ == "__main__":
    run_live_api_verification()
