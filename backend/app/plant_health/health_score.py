"""
Plant Health Indicator Calculation Module
Transparent, documented formula for calculating the Plant Health Indicator (0-100).
Formula:
Plant Health Indicator = max(0, min(100, round(
    100 
    - (visible_severity_percentage * 0.75) 
    - (20 * (1 - confidence) if confidence < 0.80 else 0)
)))
"""

def calculate_plant_health_indicator(
    severity_percentage: float,
    confidence: float,
    predicted_class: str
) -> int:
    """
    Computes a transparent 0-100 Plant Health Indicator score based on
    visible severity percentage and confidence rating.
    """
    # Healthy class base score is 100
    if "healthy" in predicted_class.lower():
        indicator = 100 - (severity_percentage * 0.5)
        return int(max(0, min(100, round(indicator))))

    # Visible severity impact (0 to 75 points reduction)
    severity_component = severity_percentage * 0.75
    
    # Low confidence penalty (0 to 10 points)
    confidence_penalty = 0.0
    if confidence < 0.80:
        confidence_penalty = (0.80 - confidence) * 25.0

    raw_score = 100.0 - severity_component - confidence_penalty
    indicator_score = int(max(0, min(100, round(raw_score))))
    return indicator_score


def determine_health_status(
    predicted_class: str,
    confidence: float,
    severity_percentage: float
) -> str:
    """
    Determines system guidance state label:
    - "Healthy / No supported disease detected"
    - "Monitor"
    - "Attention Recommended"
    - "Expert Review Recommended"
    """
    if "healthy" in predicted_class.lower() and confidence >= 0.70:
        return "Healthy / No supported disease detected"
        
    if confidence < 0.50 or severity_percentage >= 40.0:
        return "Expert Review Recommended"
        
    if severity_percentage >= 20.0 or confidence < 0.75:
        return "Attention Recommended"
        
    return "Monitor"
