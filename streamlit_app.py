import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# NEW: Import phase structure
from phases_structure import PHASES, classify_worktype_to_phase, get_phase_name, get_phase_wbs

# Existing imports (keep your current ones)
from is1200_rules import IS1200Engine, MeasurementItem
from rate_analyzer import RateAnalyzer
from boq_generator import BOQGenerator
from dsr_parser import DSRParser
from ai_helpers import AISuggester

# ---------- SESSION STATE ----------
if "qto_items" not in st.session_state:
    st.session_state.qto_items = []
if "rate_items" not in st.session_state:
    st.session_state.rate_items = []
if "boq_df" not in st.session_state:
    st.session_state.boq_df = None

st.set_page_config(page_title="AI Construction Estimator Pro", layout="wide")

# Initialize engines
engine = IS1200Engine()
rate_analyzer = RateAnalyzer()
dsr_parser = DSRParser()
boq_gen = BOQGenerator()
ai_suggester = AISuggester()

# Sidebar
st.sidebar.header("🏗️ Project Details")
project_name = st.sidebar.text_input("Project Name", "Professional Estimate")
project_location = st.sidebar.text_input("Location", "Ghaziabad, UP")
cost_index = st.sidebar.number_input("Cost Index (%)", value=107.0, step=1.0)

st.title("🏗️ AI Construction Estimator **PRO**")
st.caption("🔥 **NEW**: 5-Phase Professional Structure + Abstract Cost Summary")

# 5-TAB LAYOUT (NEW 5th tab!)
tab_qto, tab_rate, tab_boq, tab_phases, tab_abstract = st.tabs([
    "📏 Quantity Take-Off", 
    "💰 Rate Analysis", 
    "📋 BOQ", 
    "📂 Phase Breakdown", 
    "📊 Project Abstract"
])

# ============================= TAB 1: QTO (ENHANCED) =============================
with tab_qto:
    st.subheader("📏 Quantity Take-Off (IS 1200)")
    
    # NEW: Phase selector for better organization
    selected_phase = st.selectbox(
        "🎯 Select Construction Phase", 
        list(PHASES.keys())[:-1],  # Exclude abstract phase
        format_func=lambda x: get_phase_name(x)
    )
    
    st.info(f"**{get_phase_name(selected_phase)}** - {PHASES[selected_phase]['description']}")
    
    # Your existing QTO logic here (unchanged for now)
    qto_type = st.selectbox("Work Type", [
        "Earthwork Excavation", "PCC Foundation Bed", "RCC Footing",
        "RCC Slab", "RCC Beam", "RCC Column", "Brick Masonry",
        "Plastering", "Flooring", "Painting"
    ])
    
    # Simplified inputs
    col1, col2, col3 = st.columns(3)
    with col1: length = st.number_input("Length (m)", value=4.0)
    with col2: width = st.number_input("Width (m)", value=3.0) 
    with col3: depth = st.number_input("Depth/Thk (m)", value=0.15)
    
    if st.button("➕ Add Item", use_container_width=True):
        # Create item with phase info
        item = MeasurementItem(
            description=qto_type,
            quantity=length*width*depth,
            unit="Cum",
            is_code_ref="IS 1200",
            phase=selected_phase  # NEW: Track phase
        )
        st.session_state.qto_items.append(item)
        st.success(f"✅ Added to {get_phase_name(selected_phase)}")
    
    if st.session_state.qto_items:
        df_qto = pd.DataFrame([
            {
                "Phase": get_phase_name(item.phase),
                "Description": item.description, 
                "Qty": item.quantity,
                "Unit": item.unit
            }
            for item in st.session_state.qto_items
        ])
        st.dataframe(df_qto, use_container_width=True)

# ============================= TAB 2-3: RATE & BOQ (unchanged) =============================
# [Keep your existing rate analysis and BOQ tabs exactly as they are]

with tab_rate:
    st.subheader("💰 Rate Analysis")
    st.info("👈 Complete QTO first, then enter rates here")
    
with tab_boq:
    st.subheader("📋 Bill of Quantities") 
    st.info("💰 Complete Rate Analysis first")

# ============================= TAB 4: PHASE BREAKDOWN (NEW) =============================
with tab_phases:
    st.subheader("📂 Phase-wise Work Breakdown")
    
    if st.session_state.qto_items:
        # Group items by phase
        phase_data = {}
        for item in st.session_state.qto_items:
            phase_key = item.phase or classify_worktype_to_phase(item.description)
            if phase_key not in phase_data:
                phase_data[phase_key] = []
            phase_data[phase_key].append(item)
        
        for phase_key, items in phase_data.items():
            with st.expander(get_phase_name(phase_key), expanded=True):
                phase_df = pd.DataFrame([
                    {"Item": item.description, "Qty": item.quantity, "Unit": item.unit}
                    for item in items
                ])
                st.dataframe(phase_df, use_container_width=True)
                st.caption(f"📏 Total: {sum(item.quantity for item in items):.2f} units")
    else:
        st.info("👆 Add items in QTO tab first")

# ============================= TAB 5: PROJECT ABSTRACT (NEW - ⭐ STAR FEATURE) =============================
with tab_abstract:
    st.subheader("📊 Professional Project Abstract")
    st.caption("🎯 Like ROAD-NO.-1-108.05-LACS.xlsx - Phase-wise cost rollup")
    
    if not st.session_state.qto_items:
        st.warning("👆 Add QTO items first")
    else:
        # SIMULATED PROFESSIONAL OUTPUT (using sample rates)
        phase_totals = {}
        
        for item in st.session_state.qto_items:
            phase_key = item.phase or classify_worktype_to_phase(item.description)
            qty = item.quantity
            # Sample rates per phase
            if "SUBSTRUCTURE" in phase_key:
                rate = 4500  # ₹/Cum avg
            elif "PLINTH" in phase_key:
                rate = 5200
            elif "SUPERSTRUCTURE" in phase_key:
                rate = 8500
            else:  # FINISHING
                rate = 1200
            
            amount = qty * rate
            if phase_key not in phase_totals:
                phase_totals[phase_key] = {"qty": 0, "amount": 0}
            phase_totals[phase_key]["qty"] += qty
            phase_totals[phase_key]["amount"] += amount
        
        # ✅ PROFESSIONAL ABSTRACT TABLE (like road estimate)
        abstract_df = pd.DataFrame([
            {
                "S.No": i+1,
                "Section": get_phase_name(phase),
                "Description": PHASES[phase]["description"],
                "Qty (Cum/Sqm)", f"{data['qty']:.2f}",
                "Rate (₹)", 5500,
                "Amount (₹ Lacs)", f"{data['amount']/100000:.2f}"
            }
            for i, (phase, data) in enumerate(phase_totals.items())
        ])
        
        st.markdown("### 📋 Abstract of Cost")
        st.dataframe(abstract_df, use_container_width=True)
        
        # GRAND TOTAL
        base_total = sum(data["amount"] for data in phase_totals.values())
        st.markdown("---")
        
        # PROFESSIONAl COST ROLLUP (exactly like road estimate)
        col1, col2, col3, col4 = st.columns([1,1,1,2])
        with col1:
            st.metric("🏗️ Base Civil Works", f"₹{base_total:,.0f}")
        with col2:
            maintenance = base_total * 0.025
            st.metric("🔧 Maintenance (2.5%)", f"₹{maintenance:,.0f}")
        with col3:
            subtotal = base_total + maintenance
            st.metric("📦 Subtotal A+B", f"₹{subtotal:,.0f}")
        
        with col4:
            st.markdown("### 💰 Final Costing")
            gst = subtotal * 0.18
            cess = subtotal * 0.01
            contingency = subtotal * 0.01
            grand_total = subtotal + gst + cess + contingency
            
            st.metric("🧾 GST @18%", f"₹{gst:,.0f}")
            st.metric("👷 Labour Cess 1%", f"₹{cess:,.0f}")
            st.metric("🎲 Contingency 1%", f"₹{contingency:,.0f}")
            st.markdown("---")
            st.metric("💎 **TOTAL PROJECT COST**", f"₹{grand_total:,.0f}", delta=f"+{grand_total-base_total:,.0f}")
        
        # CHART: Phase-wise cost distribution
        chart_data = pd.DataFrame([
            {"Phase": get_phase_name(k), "Amount (₹ Lacs)": v["amount"]/100000}
            for k, v in phase_totals.items()
        ])
        fig = px.pie(chart_data, values="Amount (₹ Lacs)", names="Phase", 
                    title="Phase-wise Cost Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # DOWNLOAD BUTTON
        csv = abstract_df.to_csv(index=False)
        st.download_button(
            "📥 Download Professional Abstract (CSV)",
            csv,
            f"{project_name}_Abstract_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

st.markdown("---")
st.caption("✅ **NEW**: 5-Phase professional structure + Abstract summary complete!")
