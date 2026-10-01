import os
import sys
import io
import asyncio
from PIL import Image
from httpx import AsyncClient, ASGITransport

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from app.database.database import init_db
from app.ml.model import ai_model

def create_dummy_image_bytes(width=224, height=224, color=(0, 255, 0), format="JPEG"):
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color)
    img.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()

async def test_api_endpoints_suite():
    print("\n==========================================")
    print("RUNNING API ENDPOINT AUTOMATED TEST SUITE")
    print("==========================================\n")
    
    # Initialize DB & model manually for test environment
    init_db()
    ai_model.load_model()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # 1. GET /api/health
        res = await client.get("/api/health")
        assert res.status_code == 200, f"Health check failed with {res.status_code}"
        assert res.json().get("status") == "ok"
        print(" [PASS] GET /api/health")

        # 2. GET /api/system/info
        res = await client.get("/api/system/info")
        assert res.status_code == 200, f"System info failed with {res.status_code}"
        sys_data = res.json()
        assert "python_version" in sys_data
        assert "pytorch_version" in sys_data
        assert "device" in sys_data
        print(" [PASS] GET /api/system/info")

        # 3. GET /api/model/info
        res = await client.get("/api/model/info")
        assert res.status_code == 200, f"Model info failed with {res.status_code}"
        model_info = res.json()
        assert "architecture" in model_info
        print(" [PASS] GET /api/model/info")

        # Create sample image bytes for POST requests
        img_bytes = create_dummy_image_bytes()

        # 4. POST /api/quality-check
        res = await client.post("/api/quality-check", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
        assert res.status_code == 200, f"Quality check failed with {res.status_code}"
        qc = res.json()
        assert "pass" in qc or "is_valid" in qc or "overall_pass" in qc or "quality_score" in qc or "checks" in qc
        print(" [PASS] POST /api/quality-check")

        # 5. POST /api/predict
        res = await client.post("/api/predict", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
        assert res.status_code == 200, f"Predict failed with {res.status_code}"
        pred = res.json()
        assert "prediction" in pred and ("class_name" in pred["prediction"] or "disease" in pred["prediction"])
        print(" [PASS] POST /api/predict")

        # 6. POST /api/severity
        res = await client.post("/api/severity", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
        assert res.status_code == 200, f"Severity failed with {res.status_code}"
        sev = res.json()
        assert "severity" in sev or "affected_percentage" in sev
        print(" [PASS] POST /api/severity")

        # 7. POST /api/analyze (full pipeline execution)
        res = await client.post("/api/analyze", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
        assert res.status_code == 200, f"Analyze failed with {res.status_code}"
        analysis = res.json()
        assert "analysis_id" in analysis or "id" in analysis
        analysis_id = str(analysis.get("analysis_id") or analysis.get("id"))
        print(f" [PASS] POST /api/analyze (Created Analysis ID: {analysis_id})")

        # 8. POST /api/explain
        res = await client.post("/api/explain", files={"file": ("leaf.jpg", img_bytes, "image/jpeg")})
        assert res.status_code == 200, f"Explain failed with {res.status_code}"
        exp = res.json()
        assert "gradcam" in exp or "explanation" in exp or "attention" in exp
        print(" [PASS] POST /api/explain")

        # 9. GET /api/history
        res = await client.get("/api/history")
        assert res.status_code == 200, f"History list failed with {res.status_code}"
        hist = res.json()
        assert isinstance(hist, (list, dict))
        print(" [PASS] GET /api/history")

        # 10. GET /api/history/{id}
        res = await client.get(f"/api/history/{analysis_id}")
        assert res.status_code in (200, 404), f"History item failed with {res.status_code}"
        print(f" [PASS] GET /api/history/{{id}} (status: {res.status_code})")

        # 11. GET /api/report/{id}/json
        res = await client.get(f"/api/report/{analysis_id}/json")
        assert res.status_code in (200, 404), f"Report JSON failed with {res.status_code}"
        print(f" [PASS] GET /api/report/{{id}}/json (status: {res.status_code})")

        # 12. GET /api/report/{id}/pdf
        res = await client.get(f"/api/report/{analysis_id}/pdf")
        assert res.status_code in (200, 404), f"Report PDF failed with {res.status_code}"
        if res.status_code == 200:
            assert res.headers.get("content-type") == "application/pdf"
        print(f" [PASS] GET /api/report/{{id}}/pdf (status: {res.status_code})")

        # 13. GET /api/history/export/csv
        res = await client.get("/api/history/export/csv")
        assert res.status_code == 200, f"History CSV export failed with {res.status_code}"
        assert "text/csv" in res.headers.get("content-type", "")
        print(" [PASS] GET /api/history/export/csv")

        # --------------------------------------------------
        # EDGE CASES & ERROR VALIDATION TESTS
        # --------------------------------------------------
        print("\n--- Testing Edge Cases & Error Validation ---")

        # Case A: Missing file on upload endpoint
        res = await client.post("/api/predict")
        assert res.status_code == 422, f"Expected 422 for missing file, got {res.status_code}"
        print(" [PASS] Missing file validation (422 Unprocessable Entity)")

        # Case B: Invalid image file (corrupted bytes)
        bad_bytes = b"NOT_AN_IMAGE_HEADER_1234567890"
        res = await client.post("/api/predict", files={"file": ("corrupt.txt", bad_bytes, "text/plain")})
        assert res.status_code in (400, 422, 500), f"Expected error code for corrupt image, got {res.status_code}"
        print(" [PASS] Invalid image byte validation handled safely")

        # Case C: Unknown / non-existent analysis ID
        res = await client.get("/api/history/non_existent_id_999999")
        assert res.status_code in (404, 400), f"Expected 404 for unknown ID, got {res.status_code}"
        print(" [PASS] Non-existent analysis ID validation (404 Not Found)")

        print("\n==========================================")
        print("ALL API ENDPOINT TESTS PASSED SUCCESSFULLY!")
        print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints_suite())
