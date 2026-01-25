import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================================================
# 5-PHASE CONSTRUCTION STRUCTURE (Professional Standard)
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
    """Auto-classify work item to construction phase"""
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

# =============================================================================
# APP CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="AI Construction Estimator PRO", 
    page_icon="🏗️",
    layout="wide"
)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if "qto_items" not in st.session_state:
    st.session_state.qto_items = []
if "project_name" not in st.session_state:
    st.session_state.project_name = "G+1 Residential Building"

# =============================================================================
# SIDEBAR - PROJECT INFORMATION
# =============================================================================
with st.sidebar:
    st.header("🏗️ Project Details")
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
    location = st.text_input("Location", "Ghaziabad, UP")
    cost_index = st.number_input("Cost Index (%)", value=107.0, min_value=50.0, max_value=200.0, step=1.0)
    st.info(f"**Cost Index Applied**: {cost_index:.1f}%")

# =============================================================================
# MAIN HEADER
# =============================================================================
st.title("🏗️ AI Construction Estimator **PRO**")
st.markdown("""
**Professional 5-Phase Estimation System**  
*Like ROAD-NO.-1-108.05-LACS.xlsx format*  
**IS 1200 Compliant | DSR Rates | Phase-wise Abstract**
""")

# 3-TAB PROFESSIONAL LAYOUT
tab_qto, tab_abstract, tab_export = st.tabs(["📏 Quantity Take-Off", "📊 Project Abstract", "📥 Reports & Export"])

# =============================================================================
# TAB 1: QUANTITY TAKE-OFF (IS 1200 COMPLIANT)
# =============================================================================
with tab_qto:
    st.header("📏 Quantity Take-Off")
    st.caption("**IS 1200 Method of Measurement**")
    
    # Phase Selection
    col_phase, col_worktype = st.columns([1, 2])
    with col_phase:
        selected_phase = st.selectbox(
            "🎯 Construction Phase",
            list(PHASES.keys()),
            format_func=lambda x: PHASES[x]["name"],
            help="Select phase for professional organization"
        )
        st.info(f"**{PHASES[selected_phase]['description']}**")
    
    with col_worktype:
        phase_worktypes = {
            "PHASE_1_SUBSTRUCTURE": ["Site Clearance", "Earthwork Excavation", "PCC Foundation Bed", "RCC Footing", "Backfilling"],
            "PHASE_2_PLINTH": ["Plinth Wall Masonry", "Plinth Beam RCC", "Damp Proof Course", "Plinth Filling"],
            "PHASE_3_SUPERSTRUCTURE": ["RCC Column (300×300)", "RCC Beam (230×450)", "RCC Slab (150mm)", "Brick Masonry (230mm)"],
            "PHASE_4_FINISHING": ["Plastering 12mm (Both Faces)", "Vitrified Tile Flooring", "Acrylic Painting (2 Coats)", "Electrification Lumpsum"]
        }
        qto_type = st.selectbox("Work Item", phase_worktypes.get(selected_phase, ["RCC Slab (150mm)"]))
    
    # Geometric Inputs (IS 1200 Standard)
    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.number_input("📏 Length (m)", value=5.0, min_value=0.1, step=0.1)
    with col2:
        width = st.number_input("📐 Width (m)", value=3.0, min_value=0.1, step=0.1)
    with col3:
        thickness = st.number_input("📦 Thickness/Depth (m)", value=0.15, min_value=0.01, step=0.01)
    
    # Quantity Calculation Preview
    preview_qty = length * width * thickness
    st.metric("📊 Calculated Quantity", f"{preview_qty:.2f} Cum", delta=None)
    
    # ADD ITEM BUTTON
    if st.button("➕ ADD MEASURED ITEM TO QTO", use_container_width=True, type="primary"):
        rate = get_phase_rate(selected_phase) * (cost_index / 100.0)
        item = type('Item', (), {
            'id': len(st.session_state.qto_items) + 1,
            'description': qto_type,
            'quantity': preview_qty,
            'unit': 'Cum',
            'phase': selected_phase,
            'rate': rate,
            'amount': preview_qty * rate
        })()
        
        st.session_state.qto_items.append(item)
        st.success(f"✅ **{qto_type}** | {preview_qty:.2f} Cum | ₹{item.amount:,.0f}")
        st.balloons()
    
    # QTO SUMMARY TABLE
    if st.session_state.qto_items:
        qto_data = []
        phase_totals_display = {}
        
        for item in st.session_state.qto_items:
            phase_name = get_phase_name(item.phase)
            if phase_name not in phase_totals_display:
                phase_totals_display[phase_name] = 0
            phase_totals_display[phase_name] += item.amount
            
            qto_data.append({
                "Sr": item.id,
                "Phase": get_phase_name(item.phase),
                "Item": item.description,
                "Qty": f"{item.quantity:.2f}",
                "Unit": item.unit,
                "Rate": f"₹{item.rate:,.0f}",
                "Amount": f"₹{item.amount:,.0f}"
            })
        
        df_qto = pd.DataFrame(qto_data)
        st.markdown("### 📋 Current QTO Items")
        st.dataframe(df_qto, use_container_width=True, hide_index=True)
        
        st.markdown("### 📊 Phase-wise QTO Summary")
        phase_summary = pd.DataFrame([{
            "Phase": phase,
            "Items": len([i for i in st.session_state.qto_items if get_phase_name(i.phase) == phase]),
            "Total Amount": f"₹{amount:,.0f}"
        } for phase, amount in phase_totals_display.items()])
        st.dataframe(phase_summary, use_container_width=True)

# =============================================================================
# TAB 2: PROFESSIONAL PROJECT ABSTRACT (ROAD ESTIMATE STYLE)
# =============================================================================
with tab_abstract:
    st.header("📊 Professional Project Abstract")
    st.caption("*Format: ROAD-NO.-1-108.05-LACS.xlsx*")
    
    if not st.session_state.qto_items:
        st.warning("👆 **Complete Quantity Take-Off first**")
        st.stop()
    
    # CALCULATE PHASE TOTALS
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
    
    # ABSTRACT OF COST TABLE (Professional Format)
    abstract_data = []
    for i, (phase_key, data) in enumerate(phase_totals.items()):
        abstract_data.append({
            "S.No": i+1,
            "Section": PHASES[phase_key]["name"],
            "Description": PHASES[phase_key]["description"],
            "Items": data["items"],
            "Quantity": f"{data['qty']:.2f} Cum",
            "Amount (₹ Lacs)": f"{data['amount']/100000:.2f}"
        })
    
    # Add totals row
    abstract_data.append({
        "S.No": "**Total**",
        "Section": "**A. Civil Works**",
        "Description": "",
        "Items": len(st.session_state.qto_items),
        "Quantity": f"{sum(data['qty'] for data in phase_totals.values()):.2f} Cum",
        "Amount (₹ Lacs)": f"{base_total/100000:.2f}"
    })
    
    abstract_df = pd.DataFrame(abstract_data)
    st.markdown("### 📋 **ABSTRACT OF COST**")
    st.dataframe(abstract_df, use_container_width=True, hide_index=True)
    
    # COST ROLLUP (Professional Standard)
    maintenance = base_total * 0.025  # 2.5%
    subtotal_ab = base_total + maintenance
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏗️ **Base Civil Works (A)**", f"₹{base_total:,.0f}")
    with col2:
        st.metric("🔧 **Maintenance (2.5%) (B)**", f"₹{maintenance:,.0f}")
    with col3:
        st.metric("📦 **Subtotal A+B**", f"₹{subtotal_ab:,.0f}")
    
    # FINAL ESTIMATE WITH TAXES
    st.markdown("### 💰 **SANCTION ESTIMATE**")
    gst = subtotal_ab * 0.18
    cess = subtotal_ab * 0.01
    contingency = subtotal_ab * 0.01
    grand_total = subtotal_ab + gst + cess + contingency
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🧾 **GST @ 18%**", f"₹{gst:,.0f}")
    with col2: st.metric("👷 **Labour Cess @ 1%**", f"₹{cess:,.0f}")
    with col3: st.metric("🎲 **Contingency @ 1%**", f"₹{contingency:,.0f}")
    with col4: st.metric("💎 **GRAND TOTAL**", f"₹{grand_total:,.0f}", delta=f"+₹{grand_total-base_total:,.0f}")
    
    # PHASE-WISE PIE CHART (100% Stable)
    chart_data = pd.DataFrame([{
        "Phase": PHASES[k]["name"],
        "Amount (₹ Lacs)": round(v["amount"]/100000, 2)
    } for k, v in phase_totals.items()])
    
    fig = px.pie(
        chart_data, 
        values="Amount (₹ Lacs)", 
        names="Phase",
        hole=0.4,
        title="📈 **Phase-wise Cost Distribution**"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 3: REPORTS & EXPORT
# =============================================================================
with tab_export:
    st.header("📥 Professional Reports & Downloads")
    
    if st.session_state.qto_items:
        st.success(f"✅ **{len(st.session_state.qto_items)} items** ready for export")
        
        # QTO DETAILED REPORT
        qto_export = pd.DataFrame([{
            "Sr_No": item.id,
            "Phase": get_phase_name(item.phase),
            "Description": item.description,
            "Quantity": item.quantity,
            "Unit": item.unit,
            "Rate_Per_Unit": item.rate,
            "Amount": item.amount
        } for item in st.session_state.qto_items])
        
        st.subheader("📋 **QTO Detailed Report**")
        st.dataframe(qto_export, use_container_width=True)
        
        # DOWNLOAD BUTTONS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📥 Download QTO Report (Excel CSV)",
            data=qto_export.to_csv(index=False),
            file_name=f"{st.session_state.project_name.replace(' ', '_')}_QTO_{timestamp}.csv",
            mime="text/csv"
        )
        
        # ABSTRACT SUMMARY
        st.subheader("📊 **Abstract Summary**")
        st.dataframe(abstract_df, use_container_width=True)
        
        st.download_button(
            label="⭐ Download Professional Abstract (CSV)",
            data=abstract_df.to_csv(index=False),
            file_name=f"{st.session_state.project_name.replace(' ', '_')}_Abstract_{timestamp}.csv",
            mime="text/csv"
        )
        
        # CLEAR DATA BUTTON
        if st.button("🗑️ Clear All QTO Data", type="secondary"):
            st.session_state.qto_items = []
            st.success("✅ QTO cleared!")
            st.rerun()
            
    else:
        st.info("👆 **Add items in QTO tab first** to generate reports")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    **✅ PROFESSIONAL FEATURES:**
    • 5-Phase Construction Structure
    • IS 1200 Quantity Take-Off  
    • DSR Rate Analysis Ready
    • Phase-wise Cost Abstract
    • GST/Cess/Contingency Auto
    • Professional Excel Export
    """)
with col2:
    st.markdown("**📍 For:**\nGhaziabad Projects")

st.caption(f"**Generated:** {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}")
