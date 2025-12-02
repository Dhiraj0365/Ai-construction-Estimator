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
        ["Earthwork Excavation", "RCC Slab (M25)"],
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

    if qto_type == "RCC Slab (M25)":
        grade = "M25"
    else:
        grade = None

    if st.button("Add Measured Item to QTO"):
        try:
            if qto_type == "Earthwork Excavation":
                item = engine.measure_earthwork(
                    length=length,
                    width=width,
                    depth=depth_or_thk,
                    lead=lead,
                    soil_type="ordinary",
                )
            else:
                item = engine.measure_concrete(
                    length=length,
                    width=width,
                    thickness=depth_or_thk,
                    grade=grade,
                    element_type="slab",
                )

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


# -----------------------------
# TAB 2: Rate Analysis
# -----------------------------
with tab_rate:
    st.subheader("Rate Analysis")

    st.write("Enter or confirm rates for each measured item. Rates are in ₹/Cum for this simple example.")

    if not st.session_state.qto_items:
        st.info("No measured items found. Please add items in the Quantity Take-Off tab first.")
    else:
        rate_items = []

        for idx, item in enumerate(st.session_state.qto_items, start=1):
            st.markdown(f"**Item {idx}: {item.description} ({item.quantity:.2f} {item.unit})**")

            # Default guess for rate depending on type
            if "earthwork" in item.description.lower():
                default_rate = 250.0
            else:
                default_rate = 7500.0

            rate_value = st.number_input(
                f"Rate (₹/ {item.unit}) for: {item.description}",
                min_value=0.0,
                value=default_rate,
                key=f"rate_input_{idx}",
            )

            breakdown = rate_analyzer.simple_breakdown(rate_value)

            st.write(
                f"Estimated breakdown — Material: ₹{breakdown['material']:.2f}, "
                f"Labor: ₹{breakdown['labor']:.2f}, Equipment: ₹{breakdown['equipment']:.2f}, "
                f"Overheads: ₹{breakdown['overheads']:.2f}"
            )

            total_amount = item.quantity * rate_value
            st.write(f"Total amount: ₹{total_amount:,.2f}")

            rate_items.append(
                {
                    "item": item,
                    "rate": rate_value,
                    "amount": total_amount,
                    "breakdown": breakdown,
                }
            )

        if st.button("Save Rate Analysis"):
            st.session_state.rate_items = rate_items
            st.success("Rate analysis saved. Now go to the Bill of Quantities tab.")


# -----------------------------
# TAB 3: BOQ
# -----------------------------
with tab_boq:
    st.subheader("Bill of Quantities (BOQ)")

    if not st.session_state.rate_items:
        st.info("No rate analysis data found. Please complete the Rate Analysis tab first.")
    else:
        st.write("Provide WBS levels and item numbers to generate a structured BOQ.")

        boq_gen.clear_items()

        for idx, info in enumerate(st.session_state.rate_items, start=1):
            item = info["item"]
            rate = info["rate"]
            amount = info["amount"]

            st.markdown(f"**BOQ Mapping for: {item.description} ({item.quantity:.2f} {item.unit})**")

            col1, col2 = st.columns(2)
            with col1:
                item_no = st.text_input(
                    f"Item No for {item.description}",
                    value=f"{idx:03d}",
                    key=f"boq_item_no_{idx}",
                )
                wbs1 = st.text_input(
                    f"WBS Level 1 for {item.description}",
                    value="Site Preparation" if "earthwork" in item.description.lower() else "Superstructure",
                    key=f"boq_wbs1_{idx}",
                )
            with col2:
                wbs2 = st.text_input(
                    f"WBS Level 2 for {item.description}",
                    value="Earthwork" if "earthwork" in item.description.lower() else "Concrete Works",
                    key=f"boq_wbs2_{idx}",
                )

            boq_gen.add_boq_item(
                item_no=item_no,
                description=item.description,
                unit=item.unit,
                quantity=item.quantity,
                rate=rate,
                amount=amount,
                wbs_level1=wbs1,
                wbs_level2=wbs2,
                is_reference=item.is_code_ref,
            )

        if st.button("Generate BOQ Table"):
            df_boq = boq_gen.generate_dataframe(
                project_name=project_name,
                project_location=project_location,
            )
            st.session_state.boq_df = df_boq
            st.success("BOQ generated below.")

        if st.session_state.boq_df is not None:
            st.markdown("### BOQ")
            st.dataframe(st.session_state.boq_df, use_container_width=True)

            # Download as Excel
            excel_bytes = boq_gen.to_excel_bytes(st.session_state.boq_df)
            st.download_button(
                label="Download BOQ as Excel",
                data=excel_bytes,
                file_name=f"BOQ_{project_name.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
