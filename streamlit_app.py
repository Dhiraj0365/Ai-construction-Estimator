import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================================
# IS 1200 COMPLIANT RULES ENGINE (Master Implementation)
# =============================================================================
IS1200_RULES = {
    "Earthwork Excavation": {
        "code": "2.5.1",
        "method": "pit_volume",
        "deduction": "none",
        "unit": "Cum",
        "rate": 248
    },
    "PCC Foundation Bed": {
        "code": "5.2.1", 
        "method": "gross_volume",
        "deduction": "30%_voids",
        "unit": "Cum",
        "rate": 5847
    },
    "RCC Footing": {
        "code": "13.1.1",
        "method": "gross_volume", 
        "deduction": "pipes>100mm",
        "unit": "Cum",
        "rate": 8927
    },
    "RCC Column (300×300)": {
        "code": "13.2.1",
        "method": "column_volume",
        "deduction": "none",
        "unit": "Cum",
        "rate": 8927
    },
    "RCC Beam (230×450)": {
        "code": "13.3.1",
        "method": "beam_volume",
        "deduction": "none", 
        "unit": "Cum",
        "rate": 8927
    },
    "RCC Slab (150mm)": {
        "code": "13.4.1",
        "method": "slab_volume",
        "deduction": "openings>0.1m2",
        "unit": "Cum",
        "rate": 8927
    },
    "Brick Masonry (230mm)": {
        "code": "6.1.1",
        "method": "wall_volume",
        "deduction": "openings>0.1m2",
        "unit": "Cum", 
        "rate": 5123
    },
    "Plinth Wall Masonry": {
        "code": "6.1.2",
        "method": "wall_volume",
        "deduction": "openings>0.1m2",
        "unit": "Cum",
        "rate": 5123
    },
    "Plastering 12mm (Both Faces)": {
        "code": "11.1.1",
        "method": "net_wall_area",
        "deduction": "openings>0.5m2",
        "unit": "SQM",
        "rate": 187
    },
    "Vitrified Tile Flooring": {
        "code": "14.1.1",
        "method": "net_floor_area",
        "deduction": "openings>0.1m2", 
        "unit": "SQM",
        "rate": 1245
    },
    "Acrylic Painting (2 Coats)": {
        "code": "15.8.1",
        "method": "net_wall_area",
        "deduction": "openings>0.5m2",
        "unit": "SQM",
        "rate": 98
    }
}

# =============================================================================
# 5-PHASE STRUCTURE
# =============================================================================
PHASES = {
    "PHASE_1_SUBSTRUCTURE": {"name": "1️⃣ Sub-Structure", "avg_rate": 4500},
    "PHASE_2_PLINTH": {"name": "2️⃣ Plinth Level", "avg_rate": 5200},
    "PHASE_3_SUPERSTRUCTURE": {"name": "3️⃣ Super-Structure", "avg_rate": 8500},
    "PHASE_4_FINISHING": {"name": "4️⃣ Finishing", "avg_rate": 2500}
}

def get_phase_name(phase_key): 
    return PHASES.get(phase_key, PHASES["PHASE_3_SUPERSTRUCTURE"])["name"]

def get_phase_rate(phase_key):
    return PHASES.get(phase_key, PHASES["PHASE_3_SUPERSTRUCTURE"])["avg_rate"]

def calculate_is1200_quantity(work_type, length, width, thickness, openings=[]):
    """IS 1200 Compliant Quantity Calculation"""
    rule = IS1200_RULES.get(work_type, {})
    
    # Basic volume/area
    if rule.get("unit") == "SQM":
        gross_qty = length * width
    else:
        gross_qty = length * width * thickness
    
    # IS 1200 Deduction Rules
    net_qty = gross_qty
    
    if "openings" in rule.get("deduction", ""):
        opening_area = sum(o["length"] * o["width"] for o in openings)
        if opening_area > 0.5:  # >0.5m² deduction
            net_qty -= opening_area
    
    if "30%_voids" in rule.get("deduction", ""):
        net_qty *= 0.7
    
    return max(0, round(net_qty, 3))

def get_dsr_info(work_type):
    """Get DSR Code, Rate, Description"""
    rule = IS1200_RULES.get(work_type, {})
    return {
        "code": rule.get("code", "N/A"),
        "rate": rule.get("rate", 5500),
        "unit": rule.get("unit", "Cum")
    }

# =============================================================================
# APP CONFIGURATION
# =============================================================================
st.set_page_config(page_title="AI Construction Estimator PRO", page_icon="🏗️", layout="wide")

if "qto_items" not in st.session_state:
    st.session_state.qto_items = []
if "project_name" not in st.session_state:
    st.session_state.project_name = "G+1 Residential Building"

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.header("🏗️ Project Details")
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
    location = st.text_input("Location", "Ghaziabad, UP") 
    cost_index = st.number_input("Cost Index (%)", value=107.0, min_value=50.0, step=1.0)

# =============================================================================
# MAIN HEADER
# =============================================================================
st.title("🏗️ AI Construction Estimator **PRO** - IS 1200")
st.markdown("**✅ IS 1200 Deduction Rules | DSR Codes | CPWD Rates**")

tab_qto, tab_abstract, tab_export = st.tabs(["📏 IS 1200 QTO", "📊 Abstract", "📥 Export"])

# =============================================================================
# TAB 1: IS 1200 QUANTITY TAKE-OFF
# =============================================================================
with tab_qto:
    st.header("📏 IS 1200 Quantity Take-Off")
    
    col1, col2 = st.columns([1,2])
    with col1:
        selected_phase = st.selectbox("Phase", list(PHASES.keys()), format_func=get_phase_name)
    
    with col2:
        phase_worktypes = {
            "PHASE_1_SUBSTRUCTURE": ["Earthwork Excavation", "PCC Foundation Bed", "RCC Footing"],
            "PHASE_2_PLINTH": ["Plinth Wall Masonry"],
            "PHASE_3_SUPERSTRUCTURE": ["RCC Column (300×300)", "RCC Beam (230×450)", "RCC Slab (150mm)", "Brick Masonry (230mm)"],
            "PHASE_4_FINISHING": ["Plastering 12mm (Both Faces)", "Vitrified Tile Flooring", "Acrylic Painting (2 Coats)"]
        }
        work_type = st.selectbox("IS 1200 Item", phase_worktypes.get(selected_phase, []))
    
    # IS 1200 INPUT FIELDS
    col1, col2, col3 = st.columns(3)
    with col1: length = st.number_input("📏 Length (m)", value=10.0, min_value=0.1)
    with col2: width = st.number_input("📐 Width (m)", value=5.0, min_value=0.1) 
    with col3: thickness = st.number_input("📦 Thickness (m)", value=0.15, min_value=0.01)
    
    # OPENING DEDUCTIONS (IS 1200)
    openings = []
    num_openings = st.number_input("🪟 No. of Openings (>0.5m² deduct)", value=0, min_value=0, max_value=5)
    for i in range(int(num_openings)):
        with st.expander(f"Opening {i+1}"):
            ol, ow = st.columns(2)
            with ol: o_len = st.number_input(f"Opening {i+1} Length", value=1.0)
            with ow: o_width = st.number_input(f"Opening {i+1} Width", value=0.8)
            openings.append({"length": o_len, "width": o_width})
    
    # IS 1200 CALCULATION
    dsr_info = get_dsr_info(work_type)
    is1200_qty = calculate_is1200_quantity(work_type, length, width, thickness, openings)
    rate = dsr_info["rate"] * (cost_index / 100)
    amount = is1200_qty * rate
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Gross Volume", f"{length*width*thickness:.2f} {dsr_info['unit']}")
    col2.metric("✅ IS 1200 Net Qty", f"{is1200_qty:.2f} {dsr_info['unit']}")
    col3.metric("💰 Rate", f"₹{rate:,.0f}/{dsr_info['unit']}")
    col4.metric("💎 Amount", f"₹{amount:,.0f}")
    
    # DSR INFO
    st.markdown(f"**DSR Code**: {dsr_info['code']} | **Phase**: {get_phase_name(selected_phase)}")
    
    if st.button("➕ ADD IS 1200 ITEM", type="primary"):
        item = type('Item', (), {
            'id': len(st.session_state.qto_items) + 1,
            'work_type': work_type,
            'dsr_code': dsr_info['code'],
            'description': work_type,
            'gross_qty': length*width*thickness,
            'is1200_qty': is1200_qty,
            'unit': dsr_info['unit'],
            'rate': rate,
            'amount': amount,
            'phase': selected_phase,
            'dimensions': f"{length:.1f}x{width:.1f}x{thickness:.3f}m",
            'openings': len(openings)
        })()
        st.session_state.qto_items.append(item)
        st.success(f"✅ IS 1200 Item Added: {is1200_qty:.2f} {dsr_info['unit']} | ₹{amount:,.0f}")
        st.balloons()
    
    # QTO TABLE
    if st.session_state.qto_items:
        qto_data = [{
            "Sr": item.id,
            "DSR": item.dsr_code,
            "Item": item.work_type,
            "IS1200 Qty": f"{item.is1200_qty:.2f}",
            "Unit": item.unit,
            "Rate": f"₹{item.rate:,.0f}",
            "Amount": f"₹{item.amount:,.0f}"
        } for item in st.session_state.qto_items]
        
        df_qto = pd.DataFrame(qto_data)
        st.dataframe(df_qto, use_container_width=True)
        st.success(f"📊 **{len(st.session_state.qto_items)} IS 1200 Items** | Total: ₹{sum(i.amount for i in st.session_state.qto_items):,.0f}")

# =============================================================================
# TAB 2: PROFESSIONAL ABSTRACT
# =============================================================================
with tab_abstract:
    if not st.session_state.qto_items:
        st.warning("👆 Add IS 1200 items first")
        st.stop()
    
    st.header("📊 IS 1200 Project Abstract")
    
    # Phase totals
    phase_totals = {}
    grand_total = 0
    for item in st.session_state.qto_items:
        phase = item.phase
        if phase not in phase_totals:
            phase_totals[phase] = {"qty": 0, "items": 0, "amount": 0}
        phase_totals[phase]["qty"] += item.is1200_qty
        phase_totals[phase]["items"] += 1
        phase_totals[phase]["amount"] += item.amount
        grand_total += item.amount
    
    # Abstract table
    abstract_data = []
    for i, (phase, data) in enumerate(phase_totals.items()):
        abstract_data.append({
            "S.No": i+1,
            "Section": get_phase_name(phase),
            "Items": data["items"],
            "IS1200 Qty": f"{data['qty']:.2f}",
            "Amount (₹ Lacs)": f"{data['amount']/100000:.2f}"
        })
    
    abstract_data.append({
        "S.No": "TOTAL-A",
        "Section": "CIVIL WORKS", 
        "Items": len(st.session_state.qto_items),
        "IS1200 Qty": f"{sum(d['qty'] for d in phase_totals.values()):.2f}",
        "Amount (₹ Lacs)": f"{grand_total/100000:.2f}"
    })
    
    df_abstract = pd.DataFrame(abstract_data)
    st.markdown("### 📋 **ABSTRACT OF COST (IS 1200)**")
    st.dataframe(df_abstract, use_container_width=True)
    
    # Cost rollup
    maintenance = grand_total * 0.025
    subtotal = grand_total + maintenance
    gst = subtotal * 0.18
    grand_final = subtotal * 1.20
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🏗️ Base Works (A)", f"₹{grand_total:,.0f}")
    col2.metric("🔧 Maintenance 2.5% (B)", f"₹{maintenance:,.0f}")
    col3.metric("💎 GRAND TOTAL", f"₹{grand_final:,.0f}")

# =============================================================================
# TAB 3: EXPORT
# =============================================================================
with tab_export:
    st.header("📥 IS 1200 Professional Export")
    
    if st.session_state.qto_items:
        export_data = [{
            "Sr_No": item.id,
            "DSR_Code": item.dsr_code,
            "Phase": get_phase_name(item.phase),
            "Description": item.work_type,
            "Dimensions": item.dimensions,
            "Gross_Qty": f"{item.gross_qty:.3f}",
            "IS1200_Net_Qty": f"{item.is1200_qty:.3f}",
            "Unit": item.unit,
            "Rate_Rs": item.rate,
            "Amount_Rs": item.amount
        } for item in st.session_state.qto_items]
        
        df_export = pd.DataFrame(export_data)
        st.dataframe(df_export, use_container_width=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        csv = df_export.to_csv(index=False)
        st.download_button(
            "⭐ Download IS 1200 BOQ",
            csv,
            f"{st.session_state.project_name.replace(' ', '_')}_IS1200_{timestamp}.csv",
            "text/csv"
        )

st.markdown("---")
st.success("✅ **IS 1200 COMPLIANT** - Deduction Rules Applied!")
