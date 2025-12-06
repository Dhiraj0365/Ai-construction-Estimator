import streamlit as st
import pandas as pd

from is1200_rules import IS1200Engine, MeasurementItem
from rate_analyzer import RateAnalyzer
from boq_generator import BOQGenerator
from dsr_parser import DSRParser

# ---------- SESSION STATE INITIALIZATION (MUST BE FIRST) ----------
if "qto_items" not in st.session_state:
    st.session_state.qto_items = []

if "rate_items" not in st.session_state:
    st.session_state.rate_items = []

if "boq_df" not in st.session_state:
    st.session_state.boq_df = None
# -----------------------------------------------

st.set_page_config(page_title="AI Construction Estimator", layout="wide")

# Initialize engines
engine = IS1200Engine()
rate_analyzer = RateAnalyzer()
dsr_parser = DSRParser()
boq_gen = BOQGenerator()

# Sidebar: Project info
st.sidebar.header("Project Details")
project_name = st.sidebar.text_input("Project Name", "Test Project")
project_location = st.sidebar.text_input("Location", "City, State")
project_duration = st.sidebar.number_input("Project Duration (months)", min_value=1, value=12)
risk_level = st.sidebar.selectbox("Risk Level", ["Low", "Medium", "High"])

st.title("🧮 AI Construction Estimator")
st.caption("Quantity Take-Off (QTO), Rate Analysis, and Bill of Quantities (BOQ) as per IS 1200 standards")

tab_qto, tab_rate, tab_boq = st.tabs(["📏 Quantity Take-Off", "💰 Rate Analysis", "📋 Bill of Quantities"])

# ----------------------------- TAB 1: QTO -----------------------------
with tab_qto:
    st.subheader("Quantity Take-Off (IS 1200)")
    
    qto_type = st.selectbox(
        "Measurement Type",
        [
            "Earthwork Excavation (IS 1200 Part 1 & 2)",
            "Plain Concrete (IS 1200 Part 2)",
            "RCC Slab M25 (IS 1200 Part 2 & IS 456)",
            "Brick Masonry (IS 1200 Part 3)",
            "Plastering (IS 1200 Part 12)",
            "Flooring (IS 1200 Part 11)",
        ],
        index=0,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.number_input("Length (m)", min_value=0.1, value=10.0)
    with col2:
        width = st.number_input("Width (m)", min_value=0.1, value=5.0)
    with col3:
        depth_or_thk = st.number_input("Depth/Thickness/Height (m)", min_value=0.05, value=1.2)

    lead = st.number_input("Lead (m) (for earthwork)", min_value=0.0, value=50.0)

    if st.button("➕ Add Measured Item to QTO", use_container_width=True):
        try:
            if "Earthwork Excavation" in qto_type:
                item = engine.measure_earthwork(length, width, depth_or_thk, lead, "ordinary")
            elif "Plain Concrete" in qto_type:
                item = engine.measure_concrete(length, width, depth_or_thk, "Plain", "PCC")
            elif "RCC Slab M25" in qto_type:
                item = engine.measure_concrete(length, width, depth_or_thk, "M25", "slab")
            elif "Brick Masonry" in qto_type:
                item = engine.measure_masonry(length, width, depth_or_thk, "brick")
            elif "Plastering" in qto_type:
                item = engine.measure_plaster(length, depth_or_thk, 12.0)
            elif "Flooring" in qto_type:
                item = engine.measure_flooring(length, width, 20.0)
            else:
                st.error("Unsupported measurement type")
                st.stop()

            st.session_state.qto_items.append(item)
            st.success(f"✅ Added: {item.description} — {item.quantity:.2f} {item.unit}")
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Show current QTO items
    if st.session_state.qto_items:
        st.markdown("### 📋 Current Measured Items")
        data = [{"Description": it.description, "Quantity": it.quantity, "Unit": it.unit, "IS Reference": it.is_code_ref} 
                for it in st.session_state.qto_items]
        df_qto = pd.DataFrame(data)
        st.dataframe(df_qto, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All QTO Items", use_container_width=True):
                st.session_state.qto_items = []
                st.rerun()
    else:
        st.info("👆 Add your first measurement item above")

# ----------------------------- TAB 2: RATE ANALYSIS -----------------------------
with tab_rate:
    st.subheader("Rate Analysis (₹ Breakdown)")
    
    if not st.session_state.qto_items:
        st.info("📏 No measured items found. Please add items in the **Quantity Take-Off** tab first.")
    else:
        st.info(f"Found {len(st.session_state.qto_items)} measured items. Enter rates below.")
        
        rate_items = []
        for idx, item in enumerate(st.session_state.qto_items, 1):
            with st.expander(f"Item {idx}: {item.description} ({item.quantity:.2f} {item.unit})", expanded=True):
                # Auto-suggest rates
                desc_lower = item.description.lower()
                if "earthwork" in desc_lower:
                    default_rate = 250.0
                elif any(x in desc_lower for x in ["concrete", "rcc", "pcc"]):
                    default_rate = 7500.0
                elif "masonry" in desc_lower:
                    default_rate = 5500.0
                elif "plaster" in desc_lower:
                    default_rate = 250.0
                elif "floor" in desc_lower:
                    default_rate = 800.0
                else:
                    default_rate = 1000.0

                rate_value = st.number_input(
                    f"Rate (₹/{item.unit})",
                    min_value=0.0,
                    value=default_rate,
                    key=f"rate_{idx}",
                    help="Enter unit rate as per latest DSR"
                )

                # Show breakdown
                breakdown = rate_analyzer.simple_breakdown(rate_value)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Material", f"₹{breakdown['material']:.0f}")
                col2.metric("Labour", f"₹{breakdown['labor']:.0f}")
                col3.metric("Equipment", f"₹{breakdown['equipment']:.0f}")
                col4.metric("Overheads", f"₹{breakdown['overheads']:.0f}")

                total_amount = item.quantity * rate_value
                st.metric("Total Amount", f"₹{total_amount:,.0f}")

                rate_items.append({
                    "item": item,
                    "rate": rate_value,
                    "amount": total_amount,
                    "breakdown": breakdown,
                })

        if st.button("💾 Save Rate Analysis & Proceed to BOQ", use_container_width=True):
            st.session_state.rate_items = rate_items
            st.success("✅ Rate analysis saved! Go to BOQ tab.")
            st.rerun()

# ----------------------------- TAB 3: BOQ -----------------------------
with tab_boq:
    st.subheader("Bill of Quantities (BOQ)")
    
    if not st.session_state.rate_items:
        st.info("💰 No rate analysis found. Please complete the **Rate Analysis** tab first.")
    else:
        st.info(f"Found {len(st.session_state.rate_items)} items with rates. Finalize BOQ below.")
        
        boq_gen.clear_items()
        for idx, info in enumerate(st.session_state.rate_items, 1):
            item = info["item"]
            with st.expander(f"Item {idx}: {item.description}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    item_no = st.text_input("Item No", value=f"{idx:03d}", key=f"itemno_{idx}")
                    wbs_l1 = st.text_input("WBS Level 1", 
                                         value="Site Preparation" if "earthwork" in item.description.lower() else "Superstructure",
                                         key=f"wbs1_{idx}")
                with col2:
                    wbs_l2 = st.text_input("WBS Level 2",
                                         value="Earthwork" if "earthwork" in item.description.lower() 
                                         else "Concrete Works" if "concrete" in item.description.lower() 
                                         else "Finishes",
                                         key=f"wbs2_{idx}")

                st.info(f"Rate: ₹{info['rate']:.0f}/{item.unit} | Amount: ₹{info['amount']:,.0f}")

                boq_gen.add_boq_item(
                    item_no=item_no,
                    description=item.description,
                    unit=item.unit,
                    quantity=item.quantity,
                    rate=info["rate"],
                    amount=info["amount"],
                    wbs_level1=wbs_l1,
                    wbs_level2=wbs_l2,
                    is_reference=item.is_code_ref,
                )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Generate BOQ Table", use_container_width=True):
                df_boq = boq_gen.generate_dataframe(project_name, project_location)
                st.session_state.boq_df = df_boq
                st.success("✅ BOQ generated!")
                st.rerun()

        if st.session_state.boq_df is not None:
            st.markdown("### 📋 Final BOQ")
            st.dataframe(st.session_state.boq_df, use_container_width=True)
            
            # Total
            total = st.session_state.boq_df["Amount (₹)"].sum()
            st.metric("💎 GRAND TOTAL", f"₹{total:,.0f}")
            
            # Download
            excel_bytes = boq_gen.to_excel_bytes(st.session_state.boq_df)
            st.download_button(
                label="⬇️ Download BOQ Excel",
                data=excel_bytes,
                file_name=f"BOQ_{project_name.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

st.markdown("---")
st.markdown("*Powered by IS 1200 standards | Rates are indicative - verify with latest DSR*")
