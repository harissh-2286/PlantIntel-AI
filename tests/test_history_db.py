import os
import sys
import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend and root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import Base
from app.database.models import AnalysisModel
from app.database.schemas import AnalysisCreateSchema
from app.database import repository
from app.reports.report_service import generate_pdf_report, generate_history_csv_string
from pydantic import ValidationError

# In-memory SQLite for isolated testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setUpModule():
    Base.metadata.create_all(bind=engine)

def tearDownModule():
    Base.metadata.drop_all(bind=engine)

def test_database_initialization():
    print("[TEST 1/9] Testing Database Schema Initialization...")
    db = TestingSessionLocal()
    try:
        tables = Base.metadata.tables.keys()
        assert "analyses" in tables, "Table 'analyses' was not initialized!"
        print("  -> SQLite Database schema initialized successfully.")
    finally:
        db.close()

def test_create_and_read_analysis():
    print("[TEST 2/9] Testing Create & Read Analysis Record...")
    db = TestingSessionLocal()
    try:
        schema = AnalysisCreateSchema(
            id="PI-TEST-000001",
            image_filename="leaf_test.jpg",
            image_path="data/uploads/leaf_test.jpg",
            image_width=300,
            image_height=300,
            model_name="EfficientNetV2-S",
            predicted_class="Tomato___Late_blight",
            predicted_class_id=3,
            confidence=0.9542,
            severity_percentage=18.50,
            severity_level="Mild",
            leaf_area_pixels=10000,
            affected_area_pixels=1850,
            analysis_status="completed"
        )
        created = repository.create_analysis(db, schema)
        assert created.id == "PI-TEST-000001", f"Created ID mismatch! Got {created.id}"

        fetched = repository.get_analysis_by_id(db, "PI-TEST-000001")
        assert fetched is not None, "Failed to fetch record from database!"
        assert fetched.predicted_class == "Tomato___Late_blight", f"Class mismatch! Got {fetched.predicted_class}"
        assert fetched.confidence == 0.9542, "Confidence value mismatch!"
        print("  -> Created and retrieved analysis record successfully.")
    finally:
        db.close()

def test_invalid_data_validation_rejection():
    print("[TEST 3/9] Testing Pydantic Data Validation & Rejection...")
    
    # 1. Invalid confidence (> 1.0)
    try:
        AnalysisCreateSchema(
            id="PI-INVALID-1", image_filename="a.jpg", image_path="a.jpg",
            predicted_class="Class_0", predicted_class_id=0,
            confidence=1.5, # INVALID
            severity_percentage=10.0, severity_level="Minimal",
            leaf_area_pixels=1000, affected_area_pixels=100
        )
        assert False, "Failed to reject invalid confidence > 1.0!"
    except ValidationError:
        print("  -> Rejected invalid confidence > 1.0 correctly.")

    # 2. Affected pixels > leaf pixels
    try:
        AnalysisCreateSchema(
            id="PI-INVALID-2", image_filename="a.jpg", image_path="a.jpg",
            predicted_class="Class_0", predicted_class_id=0,
            confidence=0.8, severity_percentage=50.0, severity_level="Severe",
            leaf_area_pixels=500, affected_area_pixels=1000 # INVALID: affected > leaf
        )
        assert False, "Failed to reject affected_pixels > leaf_pixels!"
    except ValidationError:
        print("  -> Rejected affected_area_pixels > leaf_area_pixels correctly.")

def test_history_pagination_and_search():
    print("[TEST 4/9] Testing History Pagination, Search, & Filtering...")
    db = TestingSessionLocal()
    try:
        # Seed test items
        for i in range(5):
            schema = AnalysisCreateSchema(
                id=f"PI-SEED-00000{i}",
                image_filename=f"leaf_{i}.jpg",
                image_path=f"data/uploads/leaf_{i}.jpg",
                predicted_class="Apple___Black_rot" if i % 2 == 0 else "Corn___Common_rust",
                predicted_class_id=i,
                confidence=0.80 + (i * 0.03),
                severity_percentage=5.0 * i,
                severity_level="Minimal" if i < 2 else "Moderate",
                leaf_area_pixels=1000,
                affected_area_pixels=50 * i
            )
            repository.create_analysis(db, schema)

        # Test pagination limit
        items, total = repository.get_history_paginated(db, limit=3, offset=0)
        assert len(items) == 3, f"Expected 3 items, got {len(items)}"
        assert total >= 6, f"Expected total >= 6, got {total}"

        # Test search
        items_search, _ = repository.get_history_paginated(db, search="Apple")
        assert len(items_search) >= 3, f"Expected >= 3 Apple items, got {len(items_search)}"

        # Test severity filter
        items_sev, _ = repository.get_history_paginated(db, severity="Moderate")
        assert len(items_sev) >= 3, f"Expected >= 3 Moderate severity items, got {len(items_sev)}"

        print("  -> Pagination, search, and severity filters verified successfully.")
    finally:
        db.close()

def test_pdf_report_generation():
    print("[TEST 5/9] Testing PDF Report Service Generation...")
    analysis_dict = {
        "analysis_id": "PI-PDF-TEST-001",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "predicted_class": "Tomato___Early_blight",
        "confidence": 0.9678,
        "severity_percentage": 24.50,
        "severity_level": "Moderate",
        "model_name": "EfficientNetV2-S",
        "model_mode": "attention",
        "leaf_area_pixels": 12000,
        "affected_area_pixels": 2940,
        "top_predictions": [
            {"class_name": "Tomato___Early_blight", "confidence": 0.9678},
            {"class_name": "Tomato___Target_Spot", "confidence": 0.0210}
        ]
    }
    pdf_bytes = generate_pdf_report(analysis_dict)
    assert pdf_bytes is not None and len(pdf_bytes) > 500, "Generated PDF is empty or invalid!"
    assert pdf_bytes.startswith(b"%PDF"), "PDF header magic bytes missing!"
    print(f"  -> Generated valid PDF report ({len(pdf_bytes):,} bytes) with disclaimer notice.")

def test_csv_export():
    print("[TEST 6/9] Testing History CSV Export Generation...")
    db = TestingSessionLocal()
    try:
        items, _ = repository.get_history_paginated(db, limit=10, offset=0)
        csv_str = generate_history_csv_string(items)
        assert "analysis_id,created_at,predicted_class" in csv_str, "CSV header missing!"
        assert "PI-TEST-000001" in csv_str, "CSV output missing seeded record ID!"
        print("  -> Generated valid CSV export string.")
    finally:
        db.close()

def test_delete_analysis():
    print("[TEST 7/9] Testing Delete Analysis Record...")
    db = TestingSessionLocal()
    try:
        success = repository.delete_analysis(db, "PI-TEST-000001")
        assert success, "Failed to delete record!"

        fetched = repository.get_analysis_by_id(db, "PI-TEST-000001")
        assert fetched is None, "Record still exists after deletion!"
        print("  -> Deleted analysis record successfully.")
    finally:
        db.close()

def test_invalid_analysis_id():
    print("[TEST 8/9] Testing Non-existent & Invalid Analysis ID Handling...")
    db = TestingSessionLocal()
    try:
        fetched = repository.get_analysis_by_id(db, "PI-NONEXISTENT-999")
        assert fetched is None, "Expected None for non-existent analysis ID!"
        print("  -> Non-existent ID handled cleanly.")
    finally:
        db.close()

def test_database_stats_calculation():
    print("[TEST 9/9] Testing Database Statistics Aggregation...")
    db = TestingSessionLocal()
    try:
        stats = repository.get_history_statistics(db)
        assert "total_analyses" in stats, "Missing total_analyses in stats!"
        assert "severity_distribution" in stats, "Missing severity_distribution in stats!"
        print(f"  -> Aggregated DB Stats: Total={stats['total_analyses']}, Avg Severity={stats['average_severity_percentage']}%.")
    finally:
        db.close()

def run_all_phase9_tests():
    print("==================================================")
    print("  PLANTINTEL AI - PHASE 9 DATABASE & REPORT TESTS ")
    print("==================================================")
    setUpModule()
    try:
        test_database_initialization()
        test_create_and_read_analysis()
        test_invalid_data_validation_rejection()
        test_history_pagination_and_search()
        test_pdf_report_generation()
        test_csv_export()
        test_delete_analysis()
        test_invalid_analysis_id()
        test_database_stats_calculation()
        print("==================================================")
        print("   ALL PHASE 9 DB & REPORT TESTS PASSED (9/9)!    ")
        print("==================================================")
    finally:
        tearDownModule()

if __name__ == "__main__":
    run_all_phase9_tests()
