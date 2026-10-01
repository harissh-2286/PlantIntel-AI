import os
import sys
import numpy as np

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.severity import categorize_severity_level, estimate_severity_prototype

def test_categorize_severity_thresholds():
    print("[TEST 1/5] Testing Severity Level Threshold Boundaries...")
    assert categorize_severity_level(0.0) == "Minimal", "Boundary 0.0 failed!"
    assert categorize_severity_level(5.0) == "Minimal", "Boundary 5.0 failed!"
    assert categorize_severity_level(5.01) == "Mild", "Boundary 5.01 failed!"
    assert categorize_severity_level(20.0) == "Mild", "Boundary 20.0 failed!"
    assert categorize_severity_level(20.01) == "Moderate", "Boundary 20.01 failed!"
    assert categorize_severity_level(40.0) == "Moderate", "Boundary 40.0 failed!"
    assert categorize_severity_level(40.01) == "Severe", "Boundary 40.01 failed!"
    assert categorize_severity_level(60.0) == "Severe", "Boundary 60.0 failed!"
    assert categorize_severity_level(60.01) == "Very Severe", "Boundary 60.01 failed!"
    assert categorize_severity_level(95.5) == "Very Severe", "Boundary 95.5 failed!"
    print("  -> Severity threshold boundaries verified successfully.")

def test_synthetic_leaf_severity_calculation():
    print("[TEST 2/5] Testing Severity Area & Percentage Calculation on Synthetic Image...")
    # Create a 200x200 image with a green leaf square (100x100 = 10,000 px)
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[50:150, 50:150] = [40, 160, 50] # Green leaf area
    
    # Add a brown diseased lesion square (20x20 = 400 px inside the leaf)
    img[70:90, 70:90] = [180, 80, 30] # Brown lesion

    res = estimate_severity_prototype(img, min_leaf_pixels=100)
    assert res["status"] == "success", "Expected success status!"
    assert res["severity_status"] == "reliable", "Expected reliable severity status!"
    
    area = res["area"]
    leaf_px = area["leaf_pixels"]
    aff_px = area["affected_pixels"]
    pct = res["severity"]["percentage"]

    assert leaf_px >= 9000, f"Leaf pixels count too low: {leaf_px}"
    assert aff_px > 0, f"Affected pixels count zero!"
    assert aff_px <= leaf_px, f"Numerical violation: affected_pixels ({aff_px}) > leaf_pixels ({leaf_px})"
    assert 0.0 <= pct <= 100.0, f"Numerical violation: percentage ({pct}) out of range [0, 100]"
    assert res["severity"]["level"] in ["Minimal", "Mild", "Moderate", "Severe", "Very Severe"]
    assert res["visualization"]["overlay_base64"].startswith("data:image/png;base64,"), "Invalid overlay base64 string!"

    print(f"  -> Synthetic leaf calculated: Leaf={leaf_px}px, Affected={aff_px}px, Pct={pct}%, Level={res['severity']['level']}")

def test_non_leaf_image_handling():
    print("[TEST 3/5] Testing Non-Leaf Image / Background-Only Image Handling...")
    # Black/blank image with 0 green/leaf pixels
    blank_img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    res = estimate_severity_prototype(blank_img, min_leaf_pixels=500)
    assert res["status"] == "unreliable", f"Expected unreliable status for non-leaf image, got {res['status']}"
    assert res["severity"]["percentage"] == 0.0, "Expected 0.0 percentage for non-leaf image"
    assert "Unable to reliably detect visible leaf region" in res["message"]
    print("  -> Non-leaf image handled cleanly with 'unreliable' status.")

def test_numerical_bounds_validation():
    print("[TEST 4/5] Testing Numerical Bounds Validation...")
    # Generate random noise image
    np.random.seed(42)
    noise_img = np.random.randint(0, 256, (150, 150, 3), dtype=np.uint8)
    
    res = estimate_severity_prototype(noise_img, min_leaf_pixels=10)
    pct = res["severity"]["percentage"]
    leaf_px = res["area"]["leaf_pixels"]
    aff_px = res["area"]["affected_pixels"]
    
    assert 0.0 <= pct <= 100.0, f"Percentage out of bounds: {pct}"
    assert aff_px <= leaf_px, f"Affected pixels exceed leaf pixels: {aff_px} > {leaf_px}"
    print("  -> Numerical bounds 0 <= % <= 100 verified.")

def test_severity_timing_measurement():
    print("[TEST 5/5] Testing Severity Inference Latency Measurement...")
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[20:80, 20:80] = [50, 170, 50]
    
    res = estimate_severity_prototype(img, min_leaf_pixels=50)
    assert "severity_inference_time_ms" in res, "Missing severity_inference_time_ms in result!"
    assert res["severity_inference_time_ms"] >= 0.0
    print(f"  -> Severity processing time: {res['severity_inference_time_ms']} ms")

def run_all_severity_tests():
    print("==================================================")
    print("      PLANTINTEL AI - PHASE 6 SEVERITY UNIT TESTS ")
    print("==================================================")
    test_categorize_severity_thresholds()
    test_synthetic_leaf_severity_calculation()
    test_non_leaf_image_handling()
    test_numerical_bounds_validation()
    test_severity_timing_measurement()
    print("==================================================")
    print("      ALL PHASE 6 UNIT TESTS PASSED (5/5)!        ")
    print("==================================================")

if __name__ == "__main__":
    run_all_severity_tests()
