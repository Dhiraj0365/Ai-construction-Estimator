import streamlit as st
import pandas as pd

from is1200_rules import IS1200Engine, MeasurementItem
from rate_analyzer import RateAnalyzer
from boq_generator import BOQGenerator
from dsr_parser import DSRParser


st.set_page_config(page_title="AI Construction Estimator", layout="wide")

# Init session state
if "qto_items" not in st.session_state:
    st.session_state.qto_items = []

if "rate_items" not in st.session_state:
    st.session_state.rate_items = []

if "boq_df" not in st.session_state:
    st.session_state.boq_df = None

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

st.title("AI Construction Estimator")
st.caption("Quantity Take-Off (QTO), Rate Analysis, and Bill of Quantities (BOQ) as per IS 1200 and standard practice.")

tab_qto, tab_rate, tab_boq = st.tabs(["Quantity Take-Off", "Rate Analysis", "Bill of Quantities"])


# -----------------------------
# TAB 1: Quantity Take-Off
# -----------------------------
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
        depth_or_thk = st.number_input("Depth / Thickness (m)", min_value=0.05, value=1.2)

    lead = st.number_input("Lead (m)", min_value=0.0, value=50.0)

    if st.button("Add Measured Item to QTO"):
        try:
            if "Earthwork Excavation" in qto_type:
                item = engine.measure_earthwork(
                    length=length,
                    width=width,
                    depth=depth_or_thk,
                    lead=lead,
                    soil_type="ordinary",
                )

            elif "Plain Concrete" in qto_type:
                item = engine.measure_concrete(
                    length=length,
                    width=width,
                    thickness=depth_or_thk,
                    grade="Plain",
                    element_type="PCC",
                )

            elif "RCC Slab M25" in qto_type:
                item = engine.measure_concrete(
                    length=length,
                    width=width,
                    thickness=depth_or_thk,
                    grade="M25",
                    element_type="slab",
                )

            elif "Brick Masonry" in qto_type:
                item = engine.measure_masonry(
                    length=length,
                    width=width,
                    thickness=depth_or_thk,
                    material="brick",
                )

            elif "Plastering" in qto_type:
                item = engine.measure_plaster(
                    length=length,
                    height=depth_or_thk,  # use this as wall height
                    thickness_mm=12,
                )

            elif "Flooring" in qto_type:
                item = engine.measure_flooring(
                    length=length,
                    width=width,
                    thickness_mm=20,
                )

            else:
                raise ValueError("Unsupported measurement type selected.")

            st.session_state.qto_items.append(item)
            st.success(f"Added: {item.description} — {item.quantity:.2f} {item.unit}")
        except Exception as e:
            st.error(f"Error while adding item: {e}")

    if st.session_state.qto_items:
        st.markdown("### Current Measured Items")
        data = [
            {
                "Description": it.description,
                "Quantity": it.quantity,
                "Unit": it.unit,
                "IS Reference": it.is_code_ref,
            }
            for it in st.session_state.qto_items
        ]
        df_qto = pd.DataFrame(data)
        st.dataframe(df_qto, use_container_width=True)

        if st.button("Clear All Measured Items"):
            st.session_state.qto_items = []
            st.info("All measured items cleared.")
