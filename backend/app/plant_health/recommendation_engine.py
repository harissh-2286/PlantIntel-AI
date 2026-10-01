"""
Plant Health Recommendation Engine
Generates comprehensive, safe, conditional, confidence-aware agronomic guidance.
"""

from typing import Dict, Any, List
from app.plant_health.knowledge_base import (
    KNOWLEDGE_BASE_VERSION, get_disease_knowledge, SUPPORTED_CROPS
)
from app.plant_health.health_score import (
    calculate_plant_health_indicator, determine_health_status
)
from app.plant_health.rules import (
    interpret_confidence, AGRONOMIC_DISCLAIMER, DISEASE_VS_NUTRIENT_NOTE,
    INTEGRATED_PEST_MANAGEMENT_NOTE, RESISTANCE_MANAGEMENT_NOTE
)
from app.plant_health.schemas import (
    GuidanceResponse, RecommendationCard, SourceInfo
)


def generate_plant_guidance(
    analysis_dict: Dict[str, Any],
    crop: str = None,
    growth_stage: str = "unspecified",
    environment: str = "unspecified"
) -> GuidanceResponse:
    """
    Generates tailored, confidence-aware plant health guidance for an analysis record.
    """
    analysis_id = analysis_dict.get("analysis_id") or analysis_dict.get("id") or "PI-UNKNOWN"
    predicted_class = analysis_dict.get("predicted_class", "Unknown___Low_Confidence")
    confidence = float(analysis_dict.get("confidence", 0.0))
    severity_pct = float(analysis_dict.get("severity_percentage", 0.0))
    severity_lvl = analysis_dict.get("severity_level", "Minimal")

    # Crop auto-detection or fallback
    if not crop or crop.lower() == "unspecified":
        if "___" in predicted_class:
            detected_crop = predicted_class.split("___")[0].replace("_", " ")
            crop = detected_crop
        else:
            crop = "Tomato"  # Default fallback crop

    # Evaluate confidence level
    conf_level, is_confirmed, status_label = interpret_confidence(confidence)

    # Handle low confidence or unknown condition
    if conf_level == "low":
        kb_entry = get_disease_knowledge("Unknown___Low_Confidence")
        status_label = "Unconfirmed condition (Low Confidence)"
        display_class = "Possible condition / Unconfirmed"
    else:
        kb_entry = get_disease_knowledge(predicted_class)
        display_class = kb_entry.get("disease_name", predicted_class.replace("___", " - ").replace("_", " "))

    # Calculate Plant Health Indicator & Status
    health_indicator = calculate_plant_health_indicator(severity_pct, confidence, predicted_class)
    health_status = determine_health_status(predicted_class, confidence, severity_pct)

    # Build Recommendation Cards from KB
    def build_cards(card_list: List[Dict[str, Any]]) -> List[RecommendationCard]:
        cards = []
        for item in card_list:
            src_raw = item.get("source")
            src_obj = SourceInfo(**src_raw) if src_raw else None
            cards.append(RecommendationCard(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                why_it_matters=item["why_it_matters"],
                priority=item.get("priority", "Medium"),
                applicable_condition=item.get("applicable_condition", "General"),
                source=src_obj
            ))
        return cards

    immediate_actions = build_cards(kb_entry.get("immediate_actions", []))
    prevention = build_cards(kb_entry.get("prevention", []))
    water_and_env = build_cards(kb_entry.get("water_guidance", []))
    nutrition_cards = build_cards(kb_entry.get("nutrition_guidance", []))
    natural_bio_cards = build_cards(kb_entry.get("natural_biological_options", []))
    what_to_avoid = build_cards(kb_entry.get("what_to_avoid", []))

    # Low-confidence custom warning if needed
    if conf_level == "low":
        immediate_actions.insert(0, RecommendationCard(
            id="low_conf_warn",
            title="Prediction Confidence is Low",
            description="The image may not match supported disease classes. Please provide another clear image or consult an agricultural expert.",
            why_it_matters="AI visual classifier could not confirm disease identity with high certainty.",
            priority="Immediate",
            applicable_condition="Low model confidence (< 50%)"
        ))

    # Sources extraction
    sources_raw = kb_entry.get("sources", [])
    sources_objs = [SourceInfo(**s) for s in sources_raw] if sources_raw else []

    # Severity Interpretation Text
    sev_text = f"Visible affected area is estimated at {severity_pct:.1f}% ({severity_lvl})."
    if severity_pct < 10.0:
        sev_text += " Symptoms are localized to minor areas."
    elif severity_pct < 30.0:
        sev_text += " Symptoms affect a moderate portion of visible leaf surface."
    else:
        sev_text += " High visible foliage damage detected; prompt isolation and sanitation recommended."

    # Monitoring interval & Next check recommendation
    monitoring_days = kb_entry.get("monitoring_interval_days", 4)
    next_check_text = f"Recheck plant in {monitoring_days} days or sooner if symptoms worsen."

    return GuidanceResponse(
        analysis_id=analysis_id,
        knowledge_base_version=KNOWLEDGE_BASE_VERSION,
        crop=crop,
        growth_stage=growth_stage,
        environment=environment,
        predicted_class=display_class,
        confidence=confidence,
        confidence_level=conf_level,
        is_confirmed=is_confirmed,
        status_label=status_label,
        health_status=health_status,
        health_indicator_score=health_indicator,
        severity_percentage=severity_pct,
        severity_level=severity_lvl,
        severity_interpretation=sev_text,
        immediate_actions=immediate_actions,
        prevention=prevention,
        water_and_environment=water_and_env,
        nutrition_guidance=nutrition_cards,
        natural_and_biological_options=natural_bio_cards,
        what_to_avoid=what_to_avoid,
        disease_vs_nutrient_note=DISEASE_VS_NUTRIENT_NOTE,
        chemical_management_reference=kb_entry.get("chemical_management_reference"),
        resistance_management_note=kb_entry.get("resistance_management_note") or RESISTANCE_MANAGEMENT_NOTE,
        integrated_pest_management_note=INTEGRATED_PEST_MANAGEMENT_NOTE,
        monitoring_interval_days=monitoring_days,
        recommended_next_check=next_check_text,
        when_to_seek_expert_advice=kb_entry.get("when_to_seek_expert_advice", [
            "Symptoms spread rapidly across multiple plants.",
            "Prediction confidence remains consistently low.",
            "Plant shows severe systemic wilting or root rot."
        ]),
        sources=sources_objs,
        disclaimer=AGRONOMIC_DISCLAIMER
    )
