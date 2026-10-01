"""
PlantIntel AI - Disease Knowledge Base & Crop Profiles
Version: v1.0
Contains structured agronomic data, sources, crop profiles, and conditional guidance rules.
"""

KNOWLEDGE_BASE_VERSION = "v1.0"

# --- Supported Crop Profiles ---
SUPPORTED_CROPS = {
    "Tomato": {
        "crop_id": "tomato",
        "crop_name": "Tomato",
        "common_name": "Solanum lycopersicum",
        "growth_stages": ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"],
        "common_diseases": [
            "Tomato Early Blight", "Tomato Late Blight", "Tomato Leaf Mold",
            "Tomato Septoria Leaf Spot", "Tomato Spider Mites", "Tomato Yellow Leaf Curl Virus",
            "Tomato Mosaic Virus", "Tomato Bacterial Spot"
        ],
        "environmental_preferences": "Warm temperatures (20-30°C), well-drained soil, full sun",
        "water_requirements": "Consistent moisture; avoid overhead watering to prevent foliar fungal sporulation"
    },
    "Potato": {
        "crop_id": "potato",
        "crop_name": "Potato",
        "common_name": "Solanum tuberosum",
        "growth_stages": ["Sprout Development", "Vegetative", "Tuber Initiation", "Tuber Bulking", "Maturation"],
        "common_diseases": ["Potato Early Blight", "Potato Late Blight"],
        "environmental_preferences": "Cool to moderate climate (15-22°C), loose aerated soil",
        "water_requirements": "Regular irrigation during tuber bulking; avoid waterlogging"
    },
    "Apple": {
        "crop_id": "apple",
        "crop_name": "Apple",
        "common_name": "Malus domestica",
        "growth_stages": ["Dormant", "Green Tip", "Pink Bud", "Bloom", "Petal Fall", "Fruit Set", "Harvest"],
        "common_diseases": ["Apple Scab", "Apple Black Rot", "Cedar Apple Rust"],
        "environmental_preferences": "Temperate climates, well-drained fertile loam",
        "water_requirements": "Deep moisture during fruit development; dry canopy preferred"
    },
    "Corn": {
        "crop_id": "corn",
        "crop_name": "Corn (Maize)",
        "common_name": "Zea mays",
        "growth_stages": ["Emergence (VE)", "V3-V8 Vegetative", "Tasseling (VT)", "Silking (R1)", "Blister (R2)", "Dough (R3)", "Dent (R5)", "Mature"],
        "common_diseases": ["Corn Common Rust", "Northern Corn Leaf Blight", "Gray Leaf Spot"],
        "environmental_preferences": "Warm weather, fertile nitrogen-rich soil, high light",
        "water_requirements": "Critical moisture during silking and grain filling"
    },
    "Grape": {
        "crop_id": "grape",
        "crop_name": "Grape",
        "common_name": "Vitis vinifera",
        "growth_stages": ["Budburst", "Shoot Growth", "Bloom", "Fruit Set", "Veraison", "Harvest"],
        "common_diseases": ["Grape Black Rot", "Grape Esca", "Grape Powdery Mildew", "Grape Downy Mildew"],
        "environmental_preferences": "Warm sunny summers, dry harvest conditions, permeable soils",
        "water_requirements": "Moderate irrigation; good drainage essential"
    },
    "Pepper": {
        "crop_id": "pepper",
        "crop_name": "Pepper (Bell / Chili)",
        "common_name": "Capsicum annuum",
        "growth_stages": ["Seedling", "Vegetative", "Flowering", "Fruit Formation", "Harvest"],
        "common_diseases": ["Pepper Bacterial Spot", "Pepper Anthracnose"],
        "environmental_preferences": "Warm temperatures (21-29°C), rich organic soil",
        "water_requirements": "Moderate regular moisture; avoid prolonged standing water"
    }
}


# --- Authoritative Sources ---
SOURCE_USDA_EXTENSION = {
    "source_type": "extension_service",
    "source_title": "USDA & University Agricultural Extension Plant Disease Guides",
    "source_url": "https://extension.org/plant-pathology",
    "source_date": "2025"
}

SOURCE_IPM_UC = {
    "source_type": "university",
    "source_title": "University of California Statewide Integrated Pest Management Program (UC IPM)",
    "source_url": "https://ipm.ucanr.edu",
    "source_date": "2024"
}

SOURCE_FAO = {
    "source_type": "government",
    "source_title": "Food and Agriculture Organization (FAO) Plant Health & IPM Manual",
    "source_url": "https://www.fao.org/plant-health",
    "source_date": "2024"
}

SOURCE_EPPO = {
    "source_type": "research_paper",
    "source_title": "European and Mediterranean Plant Protection Organization Diagnostic Standards",
    "source_url": "https://www.eppo.int/RESOURCES/eppo_standards",
    "source_date": "2025"
}


# --- Structured Disease Knowledge Base ---
DISEASE_KNOWLEDGE_BASE = {
    # 1. TOMATO LATE BLIGHT
    "Tomato___Late_blight": {
        "disease_id": "tomato_late_blight",
        "disease_name": "Tomato Late Blight",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "affected_crops": ["Tomato", "Potato"],
        "symptoms": "Large, dark brown, water-soaked spots on leaves and stems with white moldy growth under humid conditions.",
        "risk_factors": "Cool, wet weather (15-22°C) combined with high relative humidity (>90%) and leaf wetness.",
        "favorable_conditions": "Continuous foliage wetness for 10+ hours and fog/rain.",
        "monitoring_interval_days": 3,
        "immediate_actions": [
            {
                "id": "tlb_act_1",
                "title": "Remove and Safely Dispose of Severely Infected Leaves",
                "description": "Prune visibly dark brown or decaying lower leaves during dry daylight hours. Bag infected tissues immediately; do not compost.",
                "why_it_matters": "Late blight produces millions of airborne sporangia rapidly under humid conditions, spreading easily to nearby healthy plants.",
                "priority": "Immediate",
                "applicable_condition": "Visible necrotic lesions or white downy sporulation on foliage.",
                "source": SOURCE_USDA_EXTENSION
            },
            {
                "id": "tlb_act_2",
                "title": "Isolate Affected Plants & Avoid Handling Healthy Foliage",
                "description": "Work with healthy plants first before tending to affected plots to avoid spreading spores on hands or clothing.",
                "why_it_matters": "Spores can easily transfer via contact, tools, and clothing during cultivation.",
                "priority": "Immediate",
                "applicable_condition": "Active outbreak in garden or field.",
                "source": SOURCE_IPM_UC
            }
        ],
        "prevention": [
            {
                "id": "tlb_prev_1",
                "title": "Switch to Drip Irrigation / Avoid Leaf Wetness",
                "description": "Irrigate at ground level early in the morning so foliage dries quickly before nightfall.",
                "why_it_matters": "Leaf wetness duration directly triggers Phytophthora sporangia germination and infection.",
                "priority": "High",
                "applicable_condition": "Foliar irrigation or high humidity environment.",
                "source": SOURCE_IPM_UC
            },
            {
                "id": "tlb_prev_2",
                "title": "Increase Plant Spacing and Airflow",
                "description": "Stake plants upright and prune lower suckers up to 30 cm from the soil surface to promote wind movement.",
                "why_it_matters": "Improved microclimate air circulation accelerates leaf drying and lowers humidity around lower foliage.",
                "priority": "High",
                "applicable_condition": "Dense canopy or tight plant spacing.",
                "source": SOURCE_FAO
            },
            {
                "id": "tlb_prev_3",
                "title": "Sanitation & Clean Crop Rotation",
                "description": "Remove all volunteer tomato and potato plants. Practice a 3-year crop rotation with non-solanaceous crops.",
                "why_it_matters": "Volunteer solanaceous hosts serve as primary overwintering reservoirs for pathogen spores.",
                "priority": "Preventive",
                "applicable_condition": "Field crop planning.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "water_guidance": [
            {
                "id": "tlb_wat_1",
                "title": "Manage Irrigation Timing",
                "description": "Avoid evening overhead watering. Use drip lines or root-zone soaking.",
                "why_it_matters": "Overnight moisture retention on leaves dramatically increases infection rates.",
                "priority": "High",
                "applicable_condition": "All watering practices.",
                "source": SOURCE_IPM_UC
            }
        ],
        "nutrition_guidance": [
            {
                "id": "tlb_nut_1",
                "title": "Avoid Excess Nitrogen Fertilizer",
                "description": "Do not over-apply high-nitrogen fertilizers during active infection outbreaks.",
                "why_it_matters": "Excessive nitrogen creates soft, succulent tissue that is highly susceptible to fast pathogen colonization.",
                "priority": "Medium",
                "applicable_condition": "Fertilizer schedule.",
                "source": SOURCE_USDA_EXTENSION
            },
            {
                "id": "tlb_nut_2",
                "title": "Ensure Calcium & Potassium Balance",
                "description": "Maintain adequate soil calcium and potassium levels supported by soil/tissue testing.",
                "why_it_matters": "Calcium reinforces cell wall structural integrity against enzymatic fungal degradation.",
                "priority": "Informational",
                "applicable_condition": "Routine soil management.",
                "source": SOURCE_FAO
            }
        ],
        "natural_biological_options": [
            {
                "id": "tlb_bio_1",
                "title": "Copper-Based Bio-Fungicide (Preventive Use Only)",
                "description": "Approved organic copper hydroxide/sulfate spray applied before heavy rain cycles according to product label.",
                "why_it_matters": "Copper ions form a protective barrier preventing spore germination on uninfected leaves.",
                "priority": "Preventive",
                "applicable_condition": "Early season preventive application.",
                "source": SOURCE_IPM_UC
            },
            {
                "id": "tlb_bio_2",
                "title": "Bacillus subtilis Biological Controls",
                "description": "Foliar bio-fungicide sprays containing beneficial Bacillus subtilis strain isolates.",
                "why_it_matters": "Beneficial microbes compete for leaf surface area and secrete natural anti-fungal lipopeptides.",
                "priority": "Preventive",
                "applicable_condition": "Organic Integrated Pest Management.",
                "source": SOURCE_EPPO
            }
        ],
        "what_to_avoid": [
            {
                "id": "tlb_avd_1",
                "title": "Do NOT Apply High Nitrogen Fertilizers to 'Cure' Decaying Leaves",
                "description": "Adding extra nitrogen will not restore dark rotting tissue and will weaken healthy foliage resilience.",
                "why_it_matters": "Pathogen lesions are caused by cell breakdown, not nitrogen starvation.",
                "priority": "Immediate",
                "applicable_condition": "Nutrient management.",
                "source": SOURCE_USDA_EXTENSION
            },
            {
                "id": "tlb_avd_2",
                "title": "Do NOT Overhead Sprinkling During High Risk Humidity",
                "description": "Never wet canopy leaves when weather is cloudy, rainy, or cool.",
                "why_it_matters": "Extended free water film allows zoospores to swim into stomata.",
                "priority": "Immediate",
                "applicable_condition": "Watering routine.",
                "source": SOURCE_IPM_UC
            }
        ],
        "chemical_management_reference": "Consult local extension guidelines for registered protective bio-fungicides or copper compounds. Always verify product label for crop compatibility and harvest intervals.",
        "resistance_management_note": "Rotate fungicidal modes of action (FRAC codes) to prevent resistance development in local pathogen populations.",
        "when_to_seek_expert_advice": [
            "Visible lesions spread to more than 25% of the canopy within 48 hours.",
            "Stems develop dark brown galls or collapse.",
            "Adjacent commercial fields report active regional late blight warnings.",
            "Infection persists despite strict sanitation and air movement management."
        ],
        "sources": [SOURCE_USDA_EXTENSION, SOURCE_IPM_UC, SOURCE_FAO, SOURCE_EPPO]
    },

    # 2. TOMATO EARLY BLIGHT
    "Tomato___Early_blight": {
        "disease_id": "tomato_early_blight",
        "disease_name": "Tomato Early Blight",
        "pathogen": "Alternaria solani (Fungus)",
        "affected_crops": ["Tomato", "Potato", "Eggplant"],
        "symptoms": "Concentric rings ('target spots') on older lower leaves, surrounded by yellow halos, progressing upwards.",
        "risk_factors": "Warm temperatures (24-29°C), alternating wet and dry conditions, nutrient-stressed plants.",
        "favorable_conditions": "Frequent dew or splashing rainfall.",
        "monitoring_interval_days": 5,
        "immediate_actions": [
            {
                "id": "teb_act_1",
                "title": "Prune Yellowing Lower Spotted Leaves",
                "description": "Cut off lower foliage displaying target-shaped spots near ground level using disinfected shears.",
                "why_it_matters": "Alternaria spores persist on lower leaves and rain-splash onto higher leaves.",
                "priority": "Immediate",
                "applicable_condition": "Lower leaf concentric target spots.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "prevention": [
            {
                "id": "teb_prev_1",
                "title": "Apply Organic Mulch Layer",
                "description": "Lay down 5-8 cm of clean straw or wood chip mulch beneath plants.",
                "why_it_matters": "Mulch creates a physical barrier that prevents soil-borne fungal spores from splashing onto foliage during rainfall.",
                "priority": "High",
                "applicable_condition": "Bare soil around plants.",
                "source": SOURCE_IPM_UC
            },
            {
                "id": "teb_prev_2",
                "title": "Ensure Balanced Plant Nutrition",
                "description": "Maintain balanced potassium and nitrogen fertility based on soil test recommendations.",
                "why_it_matters": "Early blight targets older, nutrient-stressed foliage far more aggressively.",
                "priority": "Preventive",
                "applicable_condition": "Vegetative & fruiting stages.",
                "source": SOURCE_FAO
            }
        ],
        "water_guidance": [
            {
                "id": "teb_wat_1",
                "title": "Ground-Level Drip Irrigation",
                "description": "Water roots directly via drip tape or targeted hose so leaves stay dry.",
                "why_it_matters": "Drying out leaves stops conidia spore germination.",
                "priority": "High",
                "applicable_condition": "Watering system.",
                "source": SOURCE_IPM_UC
            }
        ],
        "nutrition_guidance": [
            {
                "id": "teb_nut_1",
                "title": "Soil & Tissue Test Before Adjusting Nitrogen",
                "description": "Avoid severe nitrogen deficiency which accelerates lower leaf senescence and Alternaria susceptibility.",
                "why_it_matters": "Weak, yellowing foliage is vulnerable to early blight sporulation.",
                "priority": "Medium",
                "applicable_condition": "Nutrient deficiency symptoms.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "natural_biological_options": [
            {
                "id": "teb_bio_1",
                "title": "Neem Oil Extract / Potassium Bicarbonate",
                "description": "Apply cold-pressed neem oil or potassium bicarbonate spray as an organic foliar protector.",
                "why_it_matters": "Alters leaf pH surface and creates a lipid barrier against fungal hyphae expansion.",
                "priority": "Preventive",
                "applicable_condition": "Early disease onset.",
                "source": SOURCE_IPM_UC
            }
        ],
        "what_to_avoid": [
            {
                "id": "teb_avd_1",
                "title": "Do NOT Leave Crop Residue on Field Surface Post-Harvest",
                "description": "Infected stems and leaves must be cleared or deeply tilled at season end.",
                "why_it_matters": "Alternaria mycelium overwinters in plant debris for over a year.",
                "priority": "High",
                "applicable_condition": "Post-harvest cleanup.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "chemical_management_reference": "Copper bio-fungicides or chlorothalonil alternatives where legally registered.",
        "resistance_management_note": "Rotate foliar spray compounds between different mode-of-action groups.",
        "when_to_seek_expert_advice": [
            "Concentric leaf spots spread to more than 40% of the upper canopy.",
            "Stem lesions ('collar rot') girdle main stem base.",
            "Fruit exhibits dark sunken leathery rot near stem end."
        ],
        "sources": [SOURCE_USDA_EXTENSION, SOURCE_IPM_UC, SOURCE_FAO]
    },

    # 3. TOMATO BACTERIAL SPOT
    "Tomato___Bacterial_spot": {
        "disease_id": "tomato_bacterial_spot",
        "disease_name": "Tomato Bacterial Spot",
        "pathogen": "Xanthomonas species (Bacteria)",
        "affected_crops": ["Tomato", "Pepper"],
        "symptoms": "Small, dark water-soaked spots on leaves that turn greasy/necrotic; scabby spots on fruit.",
        "risk_factors": "Warm, rainy weather (24-30°C) with wind-driven rain and overhead sprinkler irrigation.",
        "favorable_conditions": "High humidity and foliage wetness.",
        "monitoring_interval_days": 4,
        "immediate_actions": [
            {
                "id": "tbs_act_1",
                "title": "Disinfect Tools Between Plants",
                "description": "Sanitize pruning shears with 70% isopropyl alcohol or 10% bleach solution between cuts.",
                "why_it_matters": "Xanthomonas bacteria spread instantaneously via sap and contaminated cutting tools.",
                "priority": "Immediate",
                "applicable_condition": "Pruning or field work.",
                "source": SOURCE_IPM_UC
            }
        ],
        "prevention": [
            {
                "id": "tbs_prev_1",
                "title": "Use Certified Disease-Free Seed & Resistant Cultivars",
                "description": "Plant certified clean seeds and resistant varieties whenever available.",
                "why_it_matters": "Bacterial spot is frequently seed-borne and difficult to eradicate once established in soil.",
                "priority": "High",
                "applicable_condition": "Seed selection.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "water_guidance": [
            {
                "id": "tbs_wat_1",
                "title": "Strictly Eliminate Overhead Water Splashing",
                "description": "Use micro-drip emitters to prevent water droplets splashing from infected leaves.",
                "why_it_matters": "Bacterial cells rely on water droplets to move and enter leaf stomata or wounds.",
                "priority": "Immediate",
                "applicable_condition": "Irrigation choice.",
                "source": SOURCE_IPM_UC
            }
        ],
        "nutrition_guidance": [
            {
                "id": "tbs_nut_1",
                "title": "Balance Micronutrients & Avoid Excess Nitrogen",
                "description": "Provide balanced nutrition without excessive nitrogen to prevent soft succulent growth.",
                "why_it_matters": "Bacterial ingress is easiest through tender, thin-walled leaf epidermal tissue.",
                "priority": "Medium",
                "applicable_condition": "Fertilizer plan.",
                "source": SOURCE_FAO
            }
        ],
        "natural_biological_options": [
            {
                "id": "tbs_bio_1",
                "title": "Copper + Mancozeb / Bacteriophage Spray",
                "description": "Apply protective fixed copper formulations or approved biological bacteriophage sprays.",
                "why_it_matters": "Fixed copper kills free bacterial cells on leaf surfaces before ingress.",
                "priority": "Preventive",
                "applicable_condition": "Early wet season.",
                "source": SOURCE_EPPO
            }
        ],
        "what_to_avoid": [
            {
                "id": "tbs_avd_1",
                "title": "Do NOT Work in Wet Fields",
                "description": "Never prune or harvest plants while foliage is wet from dew or rain.",
                "why_it_matters": "Wet leaves easily transfer bacterial slime across entire rows on clothing.",
                "priority": "Immediate",
                "applicable_condition": "Daily field operations.",
                "source": SOURCE_IPM_UC
            }
        ],
        "chemical_management_reference": "Copper bactericides combined with protective fungicides according to local label guidelines.",
        "resistance_management_note": "Bacterial populations frequently develop copper resistance; combine copper with protective co-factors.",
        "when_to_seek_expert_advice": [
            "Fruit develops severe brown scab-like lesions.",
            "Defoliation exceeds 30% of plant leaves.",
            "Bacterial spot spreads rapidly across commercial greenhouse or field rows."
        ],
        "sources": [SOURCE_USDA_EXTENSION, SOURCE_IPM_UC, SOURCE_EPPO]
    },

    # 4. HEALTHY / NORMAL PLANT
    "Tomato___healthy": {
        "disease_id": "tomato_healthy",
        "disease_name": "Healthy Tomato Foliage",
        "pathogen": "None (Healthy)",
        "affected_crops": ["Tomato"],
        "symptoms": "Vibrant green leaves, uniform texture, normal leaf margin development, no visible lesions or discoloration.",
        "risk_factors": "None detected.",
        "favorable_conditions": "Optimal growing environment maintained.",
        "monitoring_interval_days": 7,
        "immediate_actions": [
            {
                "id": "th_act_1",
                "title": "Maintain Regular Monitoring & Good Cultural Practices",
                "description": "Continue current watering, weed management, and weekly inspection routine.",
                "why_it_matters": "Routine monitoring catches early disease symptoms before visible damage escalates.",
                "priority": "Informational",
                "applicable_condition": "Healthy crop maintenance.",
                "source": SOURCE_FAO
            }
        ],
        "prevention": [
            {
                "id": "th_prev_1",
                "title": "Proactive Sanitation & Airflow Maintenance",
                "description": "Keep weed-free borders around beds and maintain good spacing between plants.",
                "why_it_matters": "Clean surroundings minimize pest vector habitats and fungal spore reservoirs.",
                "priority": "Preventive",
                "applicable_condition": "General crop care.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "water_guidance": [
            {
                "id": "th_wat_1",
                "title": "Consistent Root-Zone Moisture",
                "description": "Maintain even moisture without overwatering or allowing severe dry cycles.",
                "why_it_matters": "Prevents calcium physiological disorders like blossom end rot.",
                "priority": "Informational",
                "applicable_condition": "Routine irrigation.",
                "source": SOURCE_IPM_UC
            }
        ],
        "nutrition_guidance": [
            {
                "id": "th_nut_1",
                "title": "Balanced Fertilizer Schedule Based on Growth Stage",
                "description": "Apply balanced N-P-K nutrient supplements tailored to current stage (vegetative vs flowering/fruiting).",
                "why_it_matters": "Maintains robust natural defense mechanisms without inducing nutrient imbalances.",
                "priority": "Informational",
                "applicable_condition": "Regular feeding.",
                "source": SOURCE_FAO
            }
        ],
        "natural_biological_options": [
            {
                "id": "th_bio_1",
                "title": "Compost Tea & Beneficial Mycorrhizae",
                "description": "Incorporate rich compost or soil mycorrhizal inoculants into root zone.",
                "why_it_matters": "Enhances root nutrient uptake and builds resilient soil biology.",
                "priority": "Preventive",
                "applicable_condition": "Soil conditioning.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "what_to_avoid": [
            {
                "id": "th_avd_1",
                "title": "Do NOT Apply Unnecessary Pesticides to Healthy Plants",
                "description": "Avoid spraying chemical pesticides when no pests or diseases are present.",
                "why_it_matters": "Unnecessary sprays harm beneficial insects like predatory mites and pollinators.",
                "priority": "Preventive",
                "applicable_condition": "Pesticide usage.",
                "source": SOURCE_IPM_UC
            }
        ],
        "chemical_management_reference": "No chemical treatment needed.",
        "resistance_management_note": "N/A",
        "when_to_seek_expert_advice": [
            "Unexpected yellowing or leaf stunting appears in subsequent days.",
            "Weather conditions turn unseasonably cold and wet for extended periods."
        ],
        "sources": [SOURCE_FAO, SOURCE_USDA_EXTENSION, SOURCE_IPM_UC]
    },

    # 5. UNKNOWN / LOW CONFIDENCE
    "Unknown___Low_Confidence": {
        "disease_id": "unknown_low_confidence",
        "disease_name": "Possible Condition (Low Confidence)",
        "pathogen": "Undetermined / Unconfirmed",
        "affected_crops": ["All Crops"],
        "symptoms": "Atypical visual patterns, background interference, non-standard symptoms, or image resolution issues.",
        "risk_factors": "Unclear visual input or non-supported condition.",
        "favorable_conditions": "N/A",
        "monitoring_interval_days": 2,
        "immediate_actions": [
            {
                "id": "unk_act_1",
                "title": "Take Another Clear Image in Bright, Natural Lighting",
                "description": "Capture a close-up photograph of the leaf surface against a clean, uncluttered background in sharp focus.",
                "why_it_matters": "AI visual classification requires sharp, high-resolution detail to distinguish subtle lesions.",
                "priority": "Immediate",
                "applicable_condition": "Low model confidence.",
                "source": SOURCE_USDA_EXTENSION
            },
            {
                "id": "unk_act_2",
                "title": "Inspect Plant Closely for Non-Fungal Causes",
                "description": "Check undersides of leaves for small insects, mites, mechanical tearing, chemical burn, or soil moisture issues.",
                "why_it_matters": "Visual symptoms like yellowing or browning can stem from abiotic stresses (drought, fertilizer burn) rather than infectious disease.",
                "priority": "Immediate",
                "applicable_condition": "Uncertain diagnosis.",
                "source": SOURCE_IPM_UC
            }
        ],
        "prevention": [
            {
                "id": "unk_prev_1",
                "title": "Maintain Baseline Sanitation & Careful Observation",
                "description": "Avoid drastic chemical or heavy fertilizer interventions until the root cause is verified.",
                "why_it_matters": "Applying inappropriate treatments can aggravate stress or damage healthy leaf tissue.",
                "priority": "High",
                "applicable_condition": "Unconfirmed symptoms.",
                "source": SOURCE_FAO
            }
        ],
        "water_guidance": [
            {
                "id": "unk_wat_1",
                "title": "Check Root Zone Moisture",
                "description": "Verify soil moisture 5 cm below surface before adjusting watering.",
                "why_it_matters": "Both underwatering and overwatering cause leaf yellowing and edge necrosis.",
                "priority": "Medium",
                "applicable_condition": "Irrigation check.",
                "source": SOURCE_IPM_UC
            }
        ],
        "nutrition_guidance": [
            {
                "id": "unk_nut_1",
                "title": "Do NOT Automatically Increase Fertilizer",
                "description": "Confirm nutrient status using soil testing or crop-specific symptom guides before adding fertilizer.",
                "why_it_matters": "Nutrient excess can cause root burn and toxicity mimicking disease symptoms.",
                "priority": "Immediate",
                "applicable_condition": "Uncertain symptoms.",
                "source": SOURCE_USDA_EXTENSION
            }
        ],
        "natural_biological_options": [
            {
                "id": "unk_bio_1",
                "title": "General Plant Vigor Support",
                "description": "Ensure adequate sunlight, moderate airflow, and clean organic compost around roots.",
                "why_it_matters": "General vigor helps plants overcome minor environmental stress naturally.",
                "priority": "Preventive",
                "applicable_condition": "General care.",
                "source": SOURCE_FAO
            }
        ],
        "what_to_avoid": [
            {
                "id": "unk_avd_1",
                "title": "Do NOT Treat Unconfirmed Symptoms with Strong Synthetic Chemicals",
                "description": "Never apply broad-spectrum chemical sprays without positive disease identification.",
                "why_it_matters": "Wastes money and can harm natural beneficial predators.",
                "priority": "Immediate",
                "applicable_condition": "Uncertain condition.",
                "source": SOURCE_IPM_UC
            }
        ],
        "chemical_management_reference": "Do not apply chemical sprays without positive diagnosis.",
        "resistance_management_note": "N/A",
        "when_to_seek_expert_advice": [
            "Prediction confidence remains consistently low (< 60%).",
            "Plant shows rapid wilting, dieback, or leaf drop.",
            "Multiple plants display spreading symptoms across the field or garden."
        ],
        "sources": [SOURCE_USDA_EXTENSION, SOURCE_IPM_UC, SOURCE_FAO]
    }
}


# --- Default Generic Fallback Knowledge Base Entry ---
GENERIC_DISEASE_FALLBACK = {
    "disease_id": "generic_condition",
    "disease_name": "Foliar Condition / Disease",
    "pathogen": "Foliar Pathogen or Environmental Factor",
    "affected_crops": ["General Crops"],
    "symptoms": "Visible leaf discoloration, spots, or surface tissue stress.",
    "risk_factors": "High humidity, prolonged leaf wetness, poor ventilation, or nutrient stress.",
    "favorable_conditions": "Foliar wetness and environmental imbalances.",
    "monitoring_interval_days": 4,
    "immediate_actions": [
        {
            "id": "gen_act_1",
            "title": "Isolate Affected Leaves & Improve Air Flow",
            "description": "Prune severely affected foliage during dry daylight hours with clean tools.",
            "why_it_matters": "Reduces local spore density and minimizes spread to surrounding foliage.",
            "priority": "Immediate",
            "applicable_condition": "Visible leaf lesions.",
            "source": SOURCE_USDA_EXTENSION
        }
    ],
    "prevention": [
        {
            "id": "gen_prev_1",
            "title": "Practise Good Sanitation & Proper Spacing",
            "description": "Keep plant beds free of fallen debris and ensure proper spacing between branches.",
            "why_it_matters": "Clean surroundings limit pest and fungal overwintering sites.",
            "priority": "High",
            "applicable_condition": "Routine care.",
            "source": SOURCE_FAO
        }
    ],
    "water_guidance": [
        {
            "id": "gen_wat_1",
            "title": "Irrigate Soil Directly / Keep Foliage Dry",
            "description": "Water roots directly in the morning. Avoid soaking leaves in the evening.",
            "why_it_matters": "Drying foliage deprives fungal spores of the free water needed to germinate.",
            "priority": "High",
            "applicable_condition": "Irrigation routines.",
            "source": SOURCE_IPM_UC
        }
    ],
    "nutrition_guidance": [
        {
            "id": "gen_nut_1",
            "title": "Base Nutrient Application on Soil Testing",
            "description": "Avoid applying excessive fertilizer solely because disease symptoms are present.",
            "why_it_matters": "Fertilizers treat nutrient deficiencies, not infectious diseases.",
            "priority": "Medium",
            "applicable_condition": "Fertility management.",
            "source": SOURCE_USDA_EXTENSION
        }
    ],
    "natural_biological_options": [
        {
            "id": "gen_bio_1",
            "title": "Organic Preventive Bio-Fungicides & Biologicals",
            "description": "Consider approved copper or Bacillus subtilis bio-sprays applied per product label.",
            "why_it_matters": "Forms a biological barrier against airborne spore germination.",
            "priority": "Preventive",
            "applicable_condition": "Preventive IPM.",
            "source": SOURCE_IPM_UC
        }
    ],
    "what_to_avoid": [
        {
            "id": "gen_avd_1",
            "title": "Do NOT Rely Solely on AI Predictions for Critical Management",
            "description": "Always cross-reference visual AI feedback with local extension guidance and physical plant inspection.",
            "why_it_matters": "Visual symptoms can overlap between fungal, bacterial, viral, and nutritional factors.",
            "priority": "Immediate",
            "applicable_condition": "All AI feedback.",
            "source": SOURCE_USDA_EXTENSION
        }
    ],
    "chemical_management_reference": "Follow product labels and local agricultural regulations strictly.",
    "resistance_management_note": "Rotate chemical modes of action to manage pathogen resistance.",
    "when_to_seek_expert_advice": [
        "Visible damage spreads rapidly despite sanitation.",
        "Plant shows severe systemic wilting or stem rot.",
        "Symptoms remain unconfirmed or unusual for the region."
    ],
    "sources": [SOURCE_USDA_EXTENSION, SOURCE_IPM_UC, SOURCE_FAO]
}


def get_disease_knowledge(predicted_class: str) -> dict:
    """
    Retrieves disease knowledge entry from knowledge base with fallback handling.
    """
    if predicted_class in DISEASE_KNOWLEDGE_BASE:
        return DISEASE_KNOWLEDGE_BASE[predicted_class]
    
    # Try case-insensitive or partial match
    class_clean = predicted_class.strip()
    for key, val in DISEASE_KNOWLEDGE_BASE.items():
        if key.lower() == class_clean.lower() or val["disease_name"].lower() in class_clean.lower():
            return val
            
    # Return generic fallback copy with custom disease_name if available
    fallback = GENERIC_DISEASE_FALLBACK.copy()
    display_name = class_clean.replace("___", " - ").replace("_", " ")
    fallback["disease_name"] = display_name
    return fallback
