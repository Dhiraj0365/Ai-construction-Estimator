"""
🏗️ AI Construction Estimator PRO - DSR DESCRIPTIONS
✅ 5-Phase + Professional DSR Item Descriptions
✅ ROAD-NO.-1 Style Output with DSR Specifications
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================================
# DSR STANDARD DESCRIPTIONS (Professional Format)
# =============================================================================
DSR_DESCRIPTIONS = {
    # PHASE 1: SUB-STRUCTURE
    "Site Clearance": "Clearing jungle including cutting bushes, shrubs, undergrowth etc., removing & stacking serviceable materials and disposing unserviceable material outside premises up to 50m lead.",
    "Earthwork Excavation": "Earth work in excavation by mechanical means (Hydraulic excavator) / manual means over areas (exceeding 30 cm in depth, 1.5 m in width as well as 10 sqm on plan) including dressing of sides & ramming of bottoms, lift upto 1.5 m, including getting out the excavated material.",
    "PCC Foundation Bed": "Providing & laying in position cement concrete of grade M15 (1:2:4) nominal size 40mm excluding cost of centering & shuttering - All work up to plinth level.",
    "RCC Footing": "Providing & laying in position reinforced cement concrete M25 grade excluding cost of centering, shuttering, finishing & reinforcement - All work up to plinth level.",
    "Backfilling": "Backfilling in trenches with excavated earth in proper stages with ramming & watering including necessary compaction by mechanical means.",
    
    # PHASE 2: PLINTH LEVEL
    "Plinth Wall Masonry": "Brick work with F.P.S. bricks of class designation 7.5 in foundation & plinth in cement mortar 1:6 (1 cement : 6 coarse sand) including marking boundaries.",
    "Plinth Beam RCC": "Reinforced cement concrete work in beams above plinth level up to floor five level excluding the cost of centering, shuttering, finishing & reinforcement M25 grade.",
    "Damp Proof Course": "Providing & laying damp proof course 50mm thick with cement concrete 1:2:4 (1 cement: 2 coarse sand: 4 stone aggregate 20mm nominal size) including 2mm bitumen layer.",
    "Plinth Filling": "Filling in plinth with sand under floors including watering, ramming & consolidating in layers not exceeding 20cm thick.",
    
    # PHASE 3: SUPER-STRUCTURE
    "RCC Column (300×300)": "Providing & laying in position reinforced cement concrete M25 grade for columns excluding cost of centering, shuttering, finishing & reinforcement - All work above plinth level.",
    "RCC Beam (230×450)": "Providing & laying in position reinforced cement concrete M25 grade for beams excluding cost of centering, shuttering, finishing & reinforcement - All work above plinth level.",
    "RCC Slab (150mm)": "Reinforced cement concrete work in slabs, roofs having slope up to 15° landings, balconies, shelves, chajjas, lintels etc. M25 grade excluding cost of centering, shuttering & reinforcement.",
    "Brick Masonry (230mm)": "Brick work with F.P.S. bricks of class designation 7.5 in superstructure above plinth level up to floor V level in all positions in cement mortar 1:6 (1 cement : 6 coarse sand).",
    
    # PHASE 4: FINISHING
    "Plastering 12mm (Both Faces)": "12mm cement plaster of mix 1:6 (1 cement: 6 fine sand) on walls both faces or one face as specified including raking out joints.",
    "Vitrified Tile Flooring": "Providing & laying vitrified floor tiles 600×600mm size, thickness >8mm of 1st quality in required design & shade over 25mm thick cement mortar 1:4 (1 cement: 4 coarse sand).",
    "Acrylic Painting (2 Coats)": "Finishing walls with Premium Acrylic Smooth exterior paint of required shade - New work (Two or more coats applied @ 1.43 ltr/10 sqm over & including priming coat of exterior primer applied @ 0.90 ltr/10 sqm.",
    "Electrification Lumpsum": "Lumpsum provision for internal electrification (wiring, fixtures, switch boards, MCBs etc.) @ 8% of total civil cost as per CPWD norms."
}

# =============================================================================
# 5-PHASE STRUCTURE (Unchanged)
# =============================================================================
PHASES = {
    "PHASE_1_SUBSTRUCTURE": {
        "name": "1️⃣ Sub-Structure", 
        "description": "Site clearance, excavation, PCC bed, RCC footings, backfilling", 
        "wbs_code": "SS",
        "avg_rate": 4500
    },
    "PHASE_2_PLINTH": {
        "name": "2️⃣ Plinth Level", 
        "description": "Plinth beams, masonry walls, DPC, plinth filling", 
        "wbs_code": "PL",
        "avg_rate": 5200
    },
    "PHASE_3_SUPERSTRUCTURE": {
        "name": "3️⃣ Super-Structure", 
        "description": "RCC columns, beams, slabs + brick/block masonry", 
        "wbs_code": "SU",
        "avg_rate": 8500
    },
    "PHASE_4_FINISHING": {
        "name": "4️⃣ Finishing & Services", 
        "description": "Plastering, flooring, painting, E&M lumpsum", 
        "wbs_code": "FN",
        "avg_rate": 2500
    }
}

def classify_worktype_to_phase(worktype_name: str) -> str:
    worktype_lower = worktype_name.lower()
    if any(kw in worktype_lower for kw in ["clearance", "dismantling", "excavation", "footing", "backfill", "pcc"]):
        return "PHASE_1_SUBSTRUCTURE"
    elif any(kw in worktype_lower for kw in ["plinth", "dpc"]):
        return "PHASE_2_PLINTH"
    elif any(kw in worktype_lower for kw in ["column", "beam", "slab", "masonry"]):
        return "PHASE_3_SUPERSTRUCTURE"
    elif any(kw in worktype_lower for kw in ["plaster", "floor", "paint", "tile"]):
        return "PHASE_4_FINISHING"
    return "PHASE_3_SUPERSTRUCTURE"

def get_phase_name(phase_key: str):
    return PHASES.get(phase_key, PHASES["PHASE_3_SUPERSTRUCTURE"])["name"]

def get_phase_rate(phase_key: str):
    return PHASES.get(phase_key, PHASES["PHASE_3_SUPERSTRUCTURE"])["avg_rate"]

def get_dsr_description(work_item: str):
    """Get DSR standard description for work item"""
    return DSR_DESCRIPTIONS.get(work_item, f"Standard DSR item: {work_item}")

# =============================================================================
# APP CONFIGURATION (Unchanged)
# =============================================================================
st.set_page_config(page_title="AI Construction Estimator PRO", page_icon="🏗️", layout="wide")

if "qto_items" not in st.session_state:
    st.session_state.qto_items = []
if "project_name" not in st.session_state:
    st.session_state.project_name = "G+1 Residential Building"

# =============================================================================
# SIDEBAR (Unchanged)
# =============================================================================
with st.sidebar:
    st.header("🏗️ Project Details")
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
    location = st.text_input("Location", "Ghaziabad, UP")
    cost_index = st.number_input("Cost Index (%)", value=107.0, min_value=50.0, max_value=200.0, step=1.0)

# =============================================================================
# MAIN HEADER
# =============================================================================
st.title("🏗️ AI Construction Estimator **PRO**")
st.markdown("**✅ NEW: DSR Standard Descriptions in All Reports**")

tab_qto, tab_abstract, tab_export = st.tabs(["📏 Quantity Take-Off", "📊 Project Abstract", "📥 Reports & Export"])

# =============================================================================
# TAB 1: QTO (Updated with DSR Preview)
# =============================================================================
with tab_qto:
    st.header("📏 Quantity Take-Off (DSR Items)")
    
    col_phase, col_worktype = st.columns([1, 2])
    with col_phase:
        selected_phase = st.selectbox(
            "🎯 Construction Phase",
            list(PHASES.keys()),
            format_func=lambda x: PHASES[x]["name"]
        )
    
    with col_worktype:
        phase_worktypes = {
            "PHASE_1_SUBSTRUCTURE": ["Site Clearance", "Earthwork Excavation", "PCC Foundation Bed", "RCC Footing", "Backfilling"],
            "PHASE_2_PLINTH": ["Plinth Wall Masonry", "Plinth Beam RCC", "Damp Proof Course", "Plinth Filling"],
            "PHASE_3_SUPERSTRUCTURE": ["RCC Column (300×300)", "RCC Beam (230×450)", "RCC Slab (150mm)", "Brick Masonry (230mm)"],
            "PHASE_4_FINISHING": ["Plastering 12mm (Both Faces)", "Vitrified Tile Flooring", "Acrylic Painting (2 Coats)", "Electrification Lumpsum"]
        }
        qto_type = st.selectbox("DSR Work Item", phase_worktypes.get(selected_phase, ["RCC Slab (150mm)"]))
    
    # DSR DESCRIPTION PREVIEW (NEW)
    st.markdown("### 📄 **DSR Description**")
    dsr_desc = get_dsr_description(qto_type)
    with st.expander(f"**{qto_type}**", expanded=True):
        st.write(dsr_desc)
    
    # Dimensions
    col1, col2, col3 = st.columns(3)
    with col1: length = st.number_input("📏 Length (m)", value=5.0, min_value=0.1, step=0.1)
    with col2: width = st.number_input("📐 Width (m)", value=3.0, min_value=0.1, step=0.1)
    with col3: thickness = st.number_input("📦 Thickness/Depth (m)", value=0.15, min_value=0.01, step=0.01)
    
    preview_qty = length * width * thickness
    st.metric("📊 Calculated Quantity", f"{preview_qty:.2f} Cum")
    
    if st.button("➕ ADD DSR ITEM", use_container_width=True, type="primary"):
        rate = get_phase_rate(selected_phase) * (cost_index / 100.0)
        item = type('Item', (), {
            'id': len(st.session_state.qto_items) + 1,
            'description': qto_type,
            'dsr_specification': dsr_desc,  # NEW: DSR Description
            'quantity': preview_qty,
            'unit': 'Cum',
            'phase': selected_phase,
            'rate': rate,
            'amount': preview_qty * rate
        })()
        
        st.session_state.qto_items.append(item)
        st.success(f"✅ **DSR Item Added**: {preview_qty:.2f} Cum | ₹{item.amount:,.0f}")
    
    # QTO Table with DSR Preview
    if st.session_state.qto_items:
        st.markdown("### 📋 **QTO Items with DSR Specifications**")
        for item in st.session_state.qto_items[-3:]:  # Show last 3
            with st.expander(f"{item.description} ({item.quantity:.2f} {item.unit})"):
                st.write(item.dsr_specification)

# =============================================================================
# TAB 2: ABSTRACT (Unchanged)
# =============================================================================
with tab_abstract:
    st.header("📊 Professional Project Abstract")
    
    if not st.session_state.qto_items:
        st.warning("👆 **Complete QTO first**")
        st.stop()
    
    # [Previous abstract code unchanged...]
    phase_totals = {}
    base_total = 0
    
    for item in st.session_state.qto_items:
        phase_key = item.phase
        if phase_key not in phase_totals:
            phase_totals[phase_key] = {"qty": 0, "items": 0, "amount": 0}
        phase_totals[phase_key]["qty"] += item.quantity
        phase_totals[phase_key]["items"] += 1
        phase_totals[phase_key]["amount"] += item.amount
        base_total += item.amount
    
    abstract_data = []
    for i, (phase_key, data) in enumerate(phase_totals.items()):
        abstract_data.append({
            "S.No": i+1,
            "Section": PHASES[phase_key]["name"],
            "Items": data["items"],
            "Quantity": f"{data['qty']:.2f} Cum",
            "Amount (₹ Lacs)": f"{data['amount']/100000:.2f}"
        })
    
    abstract_df = pd.DataFrame(abstract_data)
    st.markdown("### 📋 **ABSTRACT OF COST**")
    st.dataframe(abstract_df, use_container_width=True)
    
    # Metrics (unchanged)
    maintenance = base_total * 0.025
    subtotal = base_total + maintenance
    st.metric("🏗️ Base Works", f"₹{base_total:,.0f}")
    st.metric("🔧 Maintenance 2.5%", f"₹{maintenance:,.0f}")
    st.metric("💎 GRAND TOTAL", f"₹{subtotal*1.2:,.0f}")

# =============================================================================
# TAB 3: EXPORT WITH DSR DESCRIPTIONS (UPDATED)
# =============================================================================
with tab_export:
    st.header("📥 **DSR Professional Reports**")
    
    if st.session_state.qto_items:
        # **NEW: DSR QTO REPORT**
        qto_export = pd.DataFrame([{
            "Sr_No": item.id,
            "Phase": get_phase_name(item.phase),
            "DSR_Item": item.description,
            "DSR_Description": item.dsr_specification,  # ✅ DSR SPECS
            "Quantity": item.quantity,
            "Unit": item.unit,
            "Rate_Rs": item.rate,
            "Amount_Rs": item.amount
        } for item in st.session_state.qto_items])
        
        st.markdown("### 📋 **DSR Detailed BOQ Report**")
        st.dataframe(qto_export[["Sr_No", "Phase", "DSR_Item", "Quantity", "Rate_Rs", "Amount_Rs"]], use_container_width=True)
        
        # DOWNLOAD WITH DSR SPECS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        csv_data = qto_export.to_csv(index=False)
        st.download_button(
            "⭐ **Download DSR BOQ (Full Specs)**",
            csv_data,
            f"{st.session_state.project_name.replace(' ', '_')}_DSR_BOQ_{timestamp}.csv",
            "text/csv"
        )
        
        st.success("✅ **DSR Descriptions included in all exports!**")

st.markdown("---")
st.success("✅ **DSR STANDARD DESCRIPTIONS** - Professional CPWD Format!")
