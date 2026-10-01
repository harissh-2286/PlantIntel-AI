import os
import sys
import io
import requests
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def run_live_api_verification():
    print("==================================================")
    print("  PLANTINTEL AI - LIVE API ENDPOINT VERIFICATION  ")
    print("==================================================")

    # 1. Health
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print("1. GET /api/health -> PASS 200 OK:", r.json())

    # 2. Model Info
    r = client.get("/api/model/info")
    assert r.status_code == 200, f"Model info failed: {r.status_code}"
    print("2. GET /api/model/info -> PASS 200 OK:", r.json()["architecture"])

    # Synthetic image for multipart upload
    img = Image.new("RGB", (300, 300), color=(40, 160, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    # 3. Quality Check
    r = client.post("/api/quality-check", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
    assert r.status_code == 200, f"Quality check failed: {r.status_code}"
    print("3. POST /api/quality-check -> PASS 200 OK: Valid=", r.json()["valid"])

    # 4. Predict
    r = client.post("/api/predict", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
    assert r.status_code == 200, f"Predict failed: {r.status_code}"
    print("4. POST /api/predict -> PASS 200 OK: Prediction=", r.json()["prediction"]["class_name"])

    # 5. Severity
    r = client.post("/api/severity", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
    assert r.status_code == 200, f"Severity failed: {r.status_code}"
    print("5. POST /api/severity -> PASS 200 OK: Severity=", r.json()["severity"]["level"])

    # 6. Analyze (Combined full pipeline)
    r = client.post("/api/analyze", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
    assert r.status_code == 200, f"Analyze failed: {r.status_code}"
    print("6. POST /api/analyze -> PASS 200 OK: Class=", r.json()["prediction"]["class_name"])

    # 7. Explain Attention
    r = client.post("/api/explain/attention", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
    assert r.status_code == 200, f"Attention explain failed: {r.status_code}"
    print("7. POST /api/explain/attention -> PASS 200 OK: Has Attention=", r.json()["attention"]["has_attention"])

    # 8. Explain Grad-CAM++
    r = client.post("/api/explain/gradcam", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}, data={"target_class": 0})
    assert r.status_code == 200, f"Grad-CAM++ explain failed: {r.status_code}"
    print("8. POST /api/explain/gradcam -> PASS 200 OK: Target Layer=", r.json()["explanation"]["target_layer"])

    # 9. Combined Explanation
    r = client.post("/api/explain", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
    assert r.status_code == 200, f"Combined explain failed: {r.status_code}"
    print("9. POST /api/explain -> PASS 200 OK: Combined method=", r.json()["gradcam"]["method"])

    print("==================================================")
    print("  ALL API ENDPOINTS VERIFIED SUCCESSFULLY (9/9)!  ")
    print("==================================================")

if __name__ == "__main__":
    run_live_api_verification()
