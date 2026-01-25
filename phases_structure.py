"""
Professional Construction Phase Structure - 5 Phase Hierarchy
Maps work items to Sub-Structure → Super-Structure → Finishing
"""

PHASES = {
    "PHASE_1_SUBSTRUCTURE": {
        "name": "1️⃣ Sub-Structure (Below Ground)",
        "description": "Site clearance, excavation, footings, backfilling",
        "wbs_code": "SS",
        "items": [
            "Site Clearance", "Dismantling", "Earthwork Excavation", 
            "PCC Foundation Bed", "RCC Footing", "Backfilling",
            "Dewatering"
        ]
    },
    "PHASE_2_PLINTH": {
        "name": "2️⃣ Plinth Level (Transition)",
        "description": "Plinth beams, walls, DPC, plinth filling", 
        "wbs_code": "PL",
        "items": [
            "Plinth Wall Masonry", "Plinth Beam RCC", "Damp Proof Course",
            "Plinth Filling Sand"
        ]
    },
    "PHASE_3_SUPERSTRUCTURE": {
        "name": "3️⃣ Super-Structure (Above Ground)",
        "description": "Columns, beams, slabs, walls, lintels",
        "wbs_code": "SU", 
        "items": [
            "RCC Column", "RCC Beam", "RCC Slab", "Brick Masonry",
            "Lintels Chajjas"
        ]
    },
    "PHASE_4_FINISHING": {
        "name": "4️⃣ Finishing & Services",
        "description": "Plaster, flooring, painting, E&M services",
        "wbs_code": "FN",
        "items": [
            "Plastering", "Flooring", "Painting", "Electrification Lumpsum",
            "Sanitary Lumpsum", "Doors Windows"
        ]
    },
    "PHASE_5_ABSTRACT": {
        "name": "5️⃣ Abstract & Summary",
        "description": "Cost rollup, contingency, GST",
        "wbs_code": "AB",
        "items": []
    }
}

# Work Type → Phase Mapping (for auto-classification)
WORKTYPE_TO_PHASE = {
    # Phase 1: Sub-structure
    "Site Clearance": "PHASE_1_SUBSTRUCTURE",
    "Dismantling": "PHASE_1_SUBSTRUCTURE", 
    "Earthwork Excavation": "PHASE_1_SUBSTRUCTURE",
    "PCC Foundation Bed": "PHASE_1_SUBSTRUCTURE",
    "RCC Footing": "PHASE_1_SUBSTRUCTURE",
    "Backfilling": "PHASE_1_SUBSTRUCTURE",
    
    # Phase 2: Plinth
    "Plinth Wall Masonry": "PHASE_2_PLINTH",
    "Plinth Beam RCC": "PHASE_2_PLINTH",
    "Damp Proof Course": "PHASE_2_PLINTH",
    "Plinth Filling Sand": "PHASE_2_PLINTH",
    
    # Phase 3: Super-structure  
    "RCC Column": "PHASE_3_SUPERSTRUCTURE",
    "RCC Beam": "PHASE_3_SUPERSTRUCTURE",
    "RCC Slab": "PHASE_3_SUPERSTRUCTURE",
    "Brick Masonry": "PHASE_3_SUPERSTRUCTURE",
    
    # Phase 4: Finishing
    "Plastering": "PHASE_4_FINISHING",
    "Flooring": "PHASE_4_FINISHING",
    "Painting": "PHASE_4_FINISHING",
    
    # Default fallback
    "default": "PHASE_3_SUPERSTRUCTURE"
}

def classify_worktype_to_phase(worktype_name: str) -> str:
    """Auto-classify work item to phase based on name"""
    worktype_lower = worktype_name.lower()
    
    if any(keyword in worktype_lower for keyword in ["clearance", "dismantling", "excavation", "footing", "backfill"]):
        return "PHASE_1_SUBSTRUCTURE"
    elif any(keyword in worktype_lower for keyword in ["plinth", "dpc"]):
        return "PHASE_2_PLINTH"
    elif any(keyword in worktype_lower for keyword in ["column", "beam", "slab", "masonry"]):
        return "PHASE_3_SUPERSTRUCTURE"
    elif any(keyword in worktype_lower for keyword in ["plaster", "floor", "paint"]):
        return "PHASE_4_FINISHING"
    
    return WORKTYPE_TO_PHASE.get(worktype_name, WORKTYPE_TO_PHASE["default"])

def get_phase_items(phase_key: str):
    """Get all work items belonging to a phase"""
    return PHASES[phase_key]["items"]

def get_phase_name(phase_key: str):
    """Get display name for phase"""
    return PHASES[phase_key]["name"]

def get_phase_wbs(phase_key: str):
    """Get WBS code for phase"""
    return PHASES[phase_key]["wbs_code"]
