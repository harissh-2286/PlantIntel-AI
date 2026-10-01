"""
Plant Health Alert Service
Generates configurable alerts based on severity increases, repeated detections,
low-confidence trends, and monitoring intervals.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import PlantModel, PlantAnalysisLinkModel
from app.plant_health.monitoring_service import get_plant_timeline


# --- Alert Thresholds ---
SEVERITY_INCREASE_THRESHOLD = 5.0   # Percentage points between consecutive scans
REPEATED_DISEASE_THRESHOLD = 3      # Same disease detected N+ consecutive scans
LOW_CONFIDENCE_CONSECUTIVE = 2      # N+ consecutive low-confidence scans


def generate_plant_alerts(db: Session, plant_id: str) -> List[Dict[str, Any]]:
    """
    Analyzes the plant's monitoring timeline and returns a list of alerts.
    Alerts are generated only when real stored data meets configured thresholds.
    No alerts are fabricated; empty list = no notable conditions.
    """
    plant = db.query(PlantModel).filter(PlantModel.id == plant_id).first()
    if not plant:
        return []

    timeline = get_plant_timeline(db, plant_id)
    if len(timeline) < 2:
        return []

    alerts = []

    # --- 1. Severity Increase Alert ---
    for i in range(1, len(timeline)):
        prev = timeline[i - 1]
        curr = timeline[i]
        diff = curr.severity_percentage - prev.severity_percentage
        if diff >= SEVERITY_INCREASE_THRESHOLD:
            alerts.append({
                "alert_type": "severity_increase",
                "severity": "warning",
                "title": "Visible Severity Increased",
                "message": (
                    f"Observed affected-area estimate increased by {diff:.1f}% "
                    f"between {prev.timeline_day} and {curr.timeline_day}. "
                    "Consider reviewing cultural management practices or consulting an agronomist."
                ),
                "threshold_used": f"{SEVERITY_INCREASE_THRESHOLD}% increase",
                "from_scan": prev.analysis_id,
                "to_scan": curr.analysis_id
            })

    # --- 2. Repeated Same Disease Alert ---
    if len(timeline) >= REPEATED_DISEASE_THRESHOLD:
        recent = timeline[-REPEATED_DISEASE_THRESHOLD:]
        diseases = [t.disease for t in recent]
        if len(set(diseases)) == 1 and "healthy" not in diseases[0].lower():
            alerts.append({
                "alert_type": "repeated_disease",
                "severity": "warning",
                "title": "Same Condition Detected Repeatedly",
                "message": (
                    f"'{diseases[0].replace('___', ' - ').replace('_', ' ')}' has been detected "
                    f"in {REPEATED_DISEASE_THRESHOLD} consecutive scans. "
                    "Consider seeking qualified agronomic or extension advice."
                ),
                "threshold_used": f"{REPEATED_DISEASE_THRESHOLD} consecutive detections",
                "disease": diseases[0]
            })

    # --- 3. Persistent Low Confidence Alert ---
    low_conf_streak = 0
    for event in reversed(timeline):
        if event.confidence < 0.50:
            low_conf_streak += 1
        else:
            break
    if low_conf_streak >= LOW_CONFIDENCE_CONSECUTIVE:
        alerts.append({
            "alert_type": "low_confidence_streak",
            "severity": "info",
            "title": "Prediction Confidence Remains Low",
            "message": (
                f"The last {low_conf_streak} scans have returned low model confidence (<50%). "
                "This may indicate atypical symptoms, poor image quality, or a condition not "
                "represented in the supported disease classes. "
                "Consider consulting an agricultural expert."
            ),
            "threshold_used": f"{LOW_CONFIDENCE_CONSECUTIVE} consecutive low-confidence scans"
        })

    # --- 4. High Severity Alert ---
    latest = timeline[-1]
    if latest.severity_percentage >= 40.0:
        alerts.append({
            "alert_type": "high_severity",
            "severity": "critical",
            "title": "High Visible Severity Detected",
            "message": (
                f"Latest scan shows {latest.severity_percentage:.1f}% visible affected area "
                f"({latest.severity_level}). Expert review is recommended."
            ),
            "threshold_used": ">=40% visible affected area",
            "latest_scan": latest.analysis_id
        })

    return alerts
