"""
Plant Health Rules & Thresholds Engine
Defines confidence bounds, status label rules, priorities, and agronomic disclaimers.
"""

CONFIDENCE_HIGH_THRESHOLD = 0.80
CONFIDENCE_MEDIUM_THRESHOLD = 0.50

AGRONOMIC_DISCLAIMER = (
    "Disclaimer: Agricultural recommendations depend on crop, cultivar, growth stage, soil, climate, "
    "irrigation, and local regulations. The system does not guarantee disease cure or universal treatment efficacy. "
    "Always follow product labels, consult soil/tissue test results, and seek qualified agronomist advice for serious crop management decisions."
)

DISEASE_VS_NUTRIENT_NOTE = (
    "Educational Note: Visual leaf symptoms such as yellowing (chlorosis), necrotic brown spots, and wilting "
    "can be caused by fungal pathogens, bacterial infections, viral agents, insect damage, or abiotic factors "
    "(such as nitrogen/potassium deficiencies, drought, or soil salinity). Visual symptoms alone may not uniquely identify the root cause. "
    "Soil or plant tissue analysis is recommended prior to major fertilizer or chemical applications."
)

INTEGRATED_PEST_MANAGEMENT_NOTE = (
    "Integrated Plant Health Strategy (IPM): 1. Prevention (sanitation, rotation) -> 2. Monitoring (regular field scans) -> "
    "3. Cultural Control (irrigation/airflow management) -> 4. Biological Control (beneficial microbes/predators) -> "
    "5. Chemical Control (targeted, labeled applications as last resort)."
)

RESISTANCE_MANAGEMENT_NOTE = (
    "Resistance Management: To prevent pathogen resistance buildup, avoid repeated sequential application of chemicals "
    "with the same mode of action (FRAC/IRAC codes). Rotate active ingredients and combine cultural sanitation practices."
)

def interpret_confidence(confidence: float) -> tuple[str, bool, str]:
    """
    Returns (confidence_level, is_confirmed, status_label):
    - High (>= 0.80): ("high", True, "Confirmed disease")
    - Medium (0.50 to 0.79): ("medium", False, "Possible condition")
    - Low (< 0.50): ("low", False, "Unconfirmed condition (Low Confidence)")
    """
    if confidence >= CONFIDENCE_HIGH_THRESHOLD:
        return "high", True, "Confirmed disease"
    elif confidence >= CONFIDENCE_MEDIUM_THRESHOLD:
        return "medium", False, "Possible condition"
    else:
        return "low", False, "Unconfirmed condition (Low Confidence)"
