import streamlit as st
import pandas as pd

from is1200_rules import IS1200Engine, MeasurementItem
from rate_analyzer import RateAnalyzer
from boq_generator import BOQGenerator
from dsr_parser import DSRParser
from ai_helpers import AISuggester


# ---------- SESSION STATE INITIALIZATION ----------
if "qto_items" not in st.session_state:
    st.session_state.qto_items = []

if "rate_items" not in st.session_state:
    st.session_state.rate_items = []

if "boq_df" not in st.session_state:
    st.session_state.boq_df = None
# --------------------------------------------------


st.set_page_config(page_title="AI Construction Estimator", layout="wide")

# Initialize engines
engine = IS1200Engine()
rate_analyzer = RateAnalyzer()
dsr_parser = DSRParser()
boq_gen = BOQGenerator()
ai_suggester = AISuggester()

# Sidebar: Project info
st.sidebar.header("Project Details")
project_name = st.sidebar.text_input("Project Name", "Test Project")
project_location = st.sidebar.text_input("Location", "City, State")
project_duration = st.sidebar.number_input(
    "Project Duration (months)", min_value=1, value=12
)
risk_level = st.sidebar.selectbox("Risk Level", ["Low", "Medium", "High"])

cost_index = st.sidebar.number_input(
    "Cost Index (%)",
    min_value=50.0,
    value=100.0,
    step=1.0,
    help="Enter building cost index for this location (e.g., 107 for DSR 2023 Delhi).",
)
dsr_year = st.sidebar.text_input(
    "DSR Year / Source",
    value="DSR 2023",
    help="Reference only; note which DSR/SOR the base rates are from.",
)

st.title("🧮 AI Construction Estimator")
st.caption(
    "IS 1200-based Quantity Take-Off, Rate Analysis, and BOQ with DSR mapping, Cost Index, detailed rate analysis, and AI-assisted DSR suggestions."
)

tab_qto, tab_rate, tab_boq = st.tabs(
    ["📏 Quantity Take-Off", "💰 Rate Analysis", "📋 Bill of Quantities"]
)

# ============================= TAB 1: QTO =============================
with tab_qto:
    st.subheader("Quantity Take-Off (IS 1200 measurement rules)")

    qto_type = st.selectbox(
        "Measurement Type",
        [
            "Earthwork Excavation (IS 1200 Part 1 & 2)",
            "PCC (Plain Cement Concrete) (IS 1200 Part 2)",
            "RCC Slab (M25)",
            "RCC Beam (M25)",
            "RCC Column (M25)",
            "RCC Footing (M25)",
            "Brick Masonry (IS 1200 Part 3)",
            "Plastering (IS 1200 Part 12)",
            "Flooring (IS 1200 Part 11)",
            "Formwork (IS 1200 Part 5)",
            "Reinforcement Steel (direct kg)",
            "Reinforcement Steel (from RCC volume)",
            "Painting / Finishing (IS 1200 Part 13)",
        ],
        index=0,
    )

    # ========== SET REALISTIC DEFAULTS PER WORK TYPE ==========
    base_length = 4.0
    base_width = 3.0
    base_thk = 0.15

    if "RCC Slab" in qto_type:
        base_length, base_width, base_thk = 4.0, 3.0, 0.15
    elif "RCC Beam" in qto_type:
        base_length, base_width, base_thk = 4.0, 0.23, 0.45
    elif "RCC Column" in qto_type:
        base_length, base_width, base_thk = 0.23, 0.45, 3.0
    elif "RCC Footing" in qto_type:
        base_length, base_width, base_thk = 1.5, 1.5, 0.45
    elif "Brick Masonry" in qto_type:
        base_length, base_width, base_thk = 4.0, 0.23, 3.0  # height
    elif "Plastering" in qto_type or "Painting" in qto_type:
        base_length, base_width, base_thk = 4.0, 0.23, 3.0
    elif "Flooring" in qto_type or "Formwork" in qto_type:
        base_length, base_width, base_thk = 4.0, 3.0, 0.15
    elif "PCC" in qto_type:
        base_length, base_width, base_thk = 4.0, 3.0, 0.10
    # Earthwork, reinforcement keep generic defaults

    # Common geometry inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.number_input("Length (m)", min_value=0.1, value=base_length)
    with col2:
        width = st.number_input("Width (m)", min_value=0.1, value=base_width)
    with col3:
        depth_or_thk = st.number_input(
            "Depth / Height / Thickness (m or kg*)",
            min_value=0.05,
            value=base_thk,
            help="For reinforcement (direct kg), treat this as total weight in kg.",
        )

    # ============== EARTHWORK EXTRAS ==============
    lead = st.number_input("Lead (m) (for earthwork)", min_value=0.0, value=50.0)

    soil_type = "ordinary"
    depth_band = "up to 1.5 m"
    lead_band = "up to 50 m"

    if "Earthwork Excavation" in qto_type:
        st.markdown("#### Earthwork classification (IS 1200 Part 1 & 2)")
        col_ew1, col_ew2, col_ew3 = st.columns(3)
        with col_ew1:
            soil_type = st.selectbox(
                "Soil type",
                [
                    "ordinary",
                    "hard soil",
                    "soft rock",
                    "hard rock (blasting)",
                    "hard rock (blasting prohibited)",
                ],
                index=0,
            )
        with col_ew2:
            depth_band = st.selectbox(
                "Depth range",
                ["up to 1.5 m", "1.5 m to 3.0 m", "3.0 m to 4.5 m", "exceeding 4.5 m"],
                index=0,
            )
        with col_ew3:
            lead_band = st.selectbox(
                "Lead range",
                ["up to 50 m", "50 m to 250 m", "250 m to 500 m", "exceeding 500 m"],
                index=0,
            )

    # ============== MASONRY EXTRAS (with separate wall thickness) ==============
    n_small_openings = 0
    area_small_each = 0.0
    n_large_openings = 0
    area_large_each = 0.0
    wall_thickness = 0.23

    if "Brick Masonry" in qto_type:
        st.markdown("#### Masonry configuration (IS 1200 Part 3)")
        col_mw1, col_mw2 = st.columns(2)
        with col_mw1:
            wall_thickness = st.number_input(
                "Wall thickness (m)",
                min_value=0.075,
                value=0.23,
                step=0.01,
                help="Use 0.23 for 230 mm wall, 0.115 for half-brick, 0.34 for brick-and-half, etc.",
            )

        st.markdown("#### Masonry openings (IS 1200 Part 3)")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            n_small_openings = st.number_input(
                "No. of small openings (≤ 0.1 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_m2:
            area_small_each = st.number_input(
                "Area of each small opening (m²)",
                min_value=0.0,
                value=0.05,
                step=0.01,
            )
        with col_m3:
            n_large_openings = st.number_input(
                "No. of large openings (> 0.1 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_m4:
            area_large_each = st.number_input(
                "Area of each large opening (m²)",
                min_value=0.0,
                value=1.0,
                step=0.05,
            )

    # ============== PLASTER EXTRAS ==============
    plaster_faces = 1
    p_n_small_openings = 0
    p_area_small_each = 0.0
    p_n_large_openings = 0
    p_area_large_each = 0.0

    if "Plastering" in qto_type:
        st.markdown("#### Plastering details (IS 1200 Part 12)")
        col_p0, col_p1, col_p2 = st.columns(3)
        with col_p0:
            plaster_faces = st.selectbox(
                "Number of faces plastered",
                [1, 2],
                index=1,
            )
        with col_p1:
            p_n_small_openings = st.number_input(
                "No. of small openings (≤ 0.5 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_p2:
            p_area_small_each = st.number_input(
                "Area of each small opening (m²)",
                min_value=0.0,
                value=0.25,
                step=0.01,
            )

        col_p3, col_p4 = st.columns(2)
        with col_p3:
            p_n_large_openings = st.number_input(
                "No. of large openings (> 0.5 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_p4:
            p_area_large_each = st.number_input(
                "Area of each large opening (m²)",
                min_value=0.0,
                value=1.0,
                step=0.05,
            )

    # ============== PAINTING EXTRAS ==============
    paint_faces = 1
    paint_coats = 2
    paint_type = "acrylic"
    paint_n_small_openings = 0
    paint_area_small_each = 0.0
    paint_n_large_openings = 0
    paint_area_large_each = 0.0

    if "Painting" in qto_type:
        st.markdown("#### Painting details (IS 1200 Part 13)")
        col_pa1, col_pa2, col_pa3 = st.columns(3)
        with col_pa1:
            paint_faces = st.selectbox(
                "Number of faces painted",
                [1, 2],
                index=1,
            )
        with col_pa2:
            paint_coats = st.number_input(
                "Number of coats (primer + paint)",
                min_value=1,
                value=2,
                step=1,
            )
        with col_pa3:
            paint_type = st.selectbox(
                "Paint type",
                ["acrylic", "oil", "emulsion", "enamel"],
            )

        col_pb1, col_pb2 = st.columns(2)
        with col_pb1:
            paint_n_small_openings = st.number_input(
                "No. of small openings (≤ 0.5 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_pb2:
            paint_area_small_each = st.number_input(
                "Area of each small opening (m²)",
                min_value=0.0,
                value=0.25,
                step=0.01,
            )

        col_pb3, col_pb4 = st.columns(2)
        with col_pb3:
            paint_n_large_openings = st.number_input(
                "No. of large openings (> 0.5 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_pb4:
            paint_area_large_each = st.number_input(
                "Area of each large opening (m²)",
                min_value=0.0,
                value=1.0,
                step=0.05,
            )

    # ============== FLOORING EXTRAS ==============
    f_n_small_openings = 0
    f_area_small_each = 0.0
    f_n_large_openings = 0
    f_area_large_each = 0.0
    floor_type = "cement concrete"
    floor_thk_mm = 20.0

    if "Flooring" in qto_type:
        st.markdown("#### Flooring details (IS 1200 Part 11)")
        col_f0, col_f1 = st.columns(2)
        with col_f0:
            floor_type = st.selectbox(
                "Floor type",
                ["cement concrete", "vitrified tiles", "ceramic tiles", "stone flooring"],
            )
        with col_f1:
            floor_thk_mm = st.number_input(
                "Floor thickness (mm)",
                min_value=10.0,
                value=20.0,
                step=5.0,
            )

        col_f1a, col_f2a = st.columns(2)
        with col_f1a:
            f_n_small_openings = st.number_input(
                "No. of small openings (≤ 0.1 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_f2a:
            f_area_small_each = st.number_input(
                "Area of each small opening (m²)",
                min_value=0.0,
                value=0.05,
                step=0.01,
            )

        col_f3a, col_f4a = st.columns(2)
        with col_f3a:
            f_n_large_openings = st.number_input(
                "No. of large openings (> 0.1 m²)",
                min_value=0,
                value=0,
                step=1,
            )
        with col_f4a:
            f_area_large_each = st.number_input(
                "Area of each large opening (m²)",
                min_value=0.0,
                value=0.5,
                step=0.05,
            )

    # ============== FORMWORK EXTRAS ==============
    formwork_member_type = "slab"
    if "Formwork" in qto_type:
        formwork_member_type = st.selectbox(
            "Formwork for",
            ["slab", "beam", "column", "footing"],
        )

    # =================== ADD ITEM BUTTON ===================
    if st.button("➕ Add Measured Item to QTO", use_container_width=True):
        try:
            if "Earthwork Excavation" in qto_type:
                item = engine.measure_earthwork(
                    length=length,
                    width=width,
                    depth=depth_or_thk,
                    soil_type=soil_type,
                    depth_band=depth_band,
                    lead_band=lead_band,
                )

            elif "PCC (Plain Cement Concrete)" in qto_type:
                item = engine.measure_concrete(
                    length=length,
                    width=width,
                    thickness=depth_or_thk,
                    grade="Plain",
                    element_type="PCC",
                )

            elif "RCC Slab (M25)" in qto_type:
                item = engine.measure_rcc_member(
                    member_type="slab",
                    length=length,
                    width=width,
                    depth_or_height=depth_or_thk,
                    grade="M25",
                )

            elif "RCC Beam (M25)" in qto_type:
                item = engine.measure_rcc_member(
                    member_type="beam",
                    length=length,
                    width=width,
                    depth_or_height=depth_or_thk,
                    grade="M25",
                )

            elif "RCC Column (M25)" in qto_type:
                item = engine.measure_rcc_member(
                    member_type="column",
                    length=length,
                    width=width,
                    depth_or_height=depth_or_thk,
                    grade="M25",
                )

            elif "RCC Footing (M25)" in qto_type:
                item = engine.measure_rcc_member(
                    member_type="footing",
                    length=length,
                    width=width,
                    depth_or_height=depth_or_thk,
                    grade="M25",
                )

            elif "Brick Masonry" in qto_type:
                item = engine.measure_masonry(
                    length=length,
                    height=depth_or_thk,
                    thickness=wall_thickness,
                    material="brick",
                    n_small_openings=n_small_openings,
                    area_small_each=area_small_each,
                    n_large_openings=n_large_openings,
                    area_large_each=area_large_each,
                )

            elif "Plastering" in qto_type:
                item = engine.measure_plaster(
                    length=length,
                    height=depth_or_thk,
                    face_count=plaster_faces,
                    n_small_openings=p_n_small_openings,
                    area_small_each=p_area_small_each,
                    n_large_openings=p_n_large_openings,
                    area_large_each=p_area_large_each,
                    thickness_mm=12.0,
                )

            elif "Flooring" in qto_type:
                item = engine.measure_flooring(
                    length=length,
                    width=width,
                    n_small_openings=f_n_small_openings,
                    area_small_each=f_area_small_each,
                    n_large_openings=f_n_large_openings,
                    area_large_each=f_area_large_each,
                    thickness_mm=floor_thk_mm,
                    floor_type=floor_type,
                )

            elif "Formwork" in qto_type:
                item = engine.measure_formwork(
                    member_type=formwork_member_type,
                    length=length,
                    width=width,
                    depth_or_height=depth_or_thk,
                )

            elif "Reinforcement Steel (direct kg)" in qto_type:
                item = engine.measure_reinforcement(
                    weight_kg=depth_or_thk,
                    bar_type="TMT",
                )

            elif "Reinforcement Steel (from RCC volume)" in qto_type:
                rcc_item = engine.measure_rcc_member(
                    member_type="slab",
                    length=length,
                    width=width,
                    depth_or_height=depth_or_thk,
                    grade="M25",
                )
                item = engine.estimate_reinforcement_from_rcc(
                    member_type="slab",
                    concrete_volume=rcc_item.quantity,
                )

            elif "Painting" in qto_type:
                item = engine.measure_painting(
                    length=length,
                    height=depth_or_thk,
                    face_count=paint_faces,
                    n_small_openings=paint_n_small_openings,
                    area_small_each=paint_area_small_each,
                    n_large_openings=paint_n_large_openings,
                    area_large_each=paint_area_large_each,
                    coats=paint_coats,
                    paint_type=paint_type,
                )

            else:
                st.error("Unsupported measurement type selected.")
                st.stop()

            st.session_state.qto_items.append(item)
            st.success(f"✅ Added: {item.description} — {item.quantity:.2f} {item.unit}")
        except Exception as e:
            st.error(f"❌ Error while adding item: {e}")

    # -------- Show QTO table --------
    if st.session_state.qto_items:
        st.markdown("### 📋 Current Measured Items")
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

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All QTO Items", use_container_width=True):
                st.session_state.qto_items = []
                st.rerun()
    else:
        st.info("👆 Add your first measurement item above to start QTO.")

# ========================== TAB 2: RATE ANALYSIS ==========================
with tab_rate:
    st.subheader("Rate Analysis (₹ Breakdown)")

    if not st.session_state.qto_items:
        st.info(
            "📏 No measured items found. Please add items in the **Quantity Take-Off** tab first."
        )
    else:
        st.info(
            f"Found {len(st.session_state.qto_items)} measured items. Enter or confirm rates below."
        )

        rate_items = []
        for idx, item in enumerate(st.session_state.qto_items, start=1):
            with st.expander(
                f"Item {idx}: {item.description} ({item.quantity:.2f} {item.unit})",
                expanded=True,
            ):
                desc_lower = item.description.lower()

                # ========== IMPROVED TUNED BASE RATES (DSR 2023 approx) ==========
                if "earthwork" in desc_lower or "excavation" in desc_lower:
                    base_rate = 250.0  # ₹/Cum
                elif "pcc" in desc_lower or ("plain" in desc_lower and "concrete" in desc_lower):
                    base_rate = 4800.0  # ₹/Cum
                elif "rcc" in desc_lower:
                    base_rate = 8500.0  # ₹/Cum for M25 structural RCC
                elif "masonry" in desc_lower:
                    base_rate = 5800.0  # ₹/Cum for brick masonry CM 1:6
                elif "plaster" in desc_lower:
                    base_rate = 280.0  # ₹/Sqm for 12mm plaster
                elif "floor" in desc_lower or "tile" in desc_lower:
                    base_rate = 950.0  # ₹/Sqm for vitrified tiles
                elif "formwork" in desc_lower:
                    base_rate = 650.0  # ₹/Sqm for slab/beam formwork
                elif "reinforcement" in desc_lower:
                    base_rate = 75.0  # ₹/Kg for TMT
                elif "paint" in desc_lower or "finishing" in desc_lower:
                    base_rate = 150.0  # ₹/Sqm for 2 coats acrylic
                else:
                    base_rate = 1000.0

                default_rate = base_rate * (cost_index / 100.0)

                st.markdown("#### Unit Rate")
                rate_value = st.number_input(
                    f"Rate (₹/{item.unit})",
                    min_value=0.0,
                    value=default_rate,
                    key=f"rate_{idx}",
                    help="Enter unit rate as per latest DSR / PWD schedule or from detailed rate analysis below.",
                )

                show_detail = st.checkbox(
                    "Show detailed rate analysis (materials + labour)",
                    value=False,
                    key=f"show_detail_{idx}",
                )

                if show_detail:
                    st.markdown("##### Materials per unit of work")
                    mat_df_default = pd.DataFrame(
                        [
                            {"Resource": "Cement", "Qty per unit": 0.0, "Unit": "bag", "Rate": 0.0},
                            {"Resource": "Sand", "Qty per unit": 0.0, "Unit": "Cum", "Rate": 0.0},
                            {"Resource": "Aggregate", "Qty per unit": 0.0, "Unit": "Cum", "Rate": 0.0},
                        ]
                    )
                    mat_df = st.data_editor(
                        mat_df_default,
                        num_rows="dynamic",
                        key=f"mat_editor_{idx}",
                        use_container_width=True,
                    )
                    mat_cost = float((mat_df["Qty per unit"] * mat_df["Rate"]).sum())

                    st.markdown("##### Labour per unit of work")
                    lab_df_default = pd.DataFrame(
                        [
                            {"Category": "Mason", "Hrs per unit": 0.0, "Wage/hr": 0.0},
                            {"Category": "Helper", "Hrs per unit": 0.0, "Wage/hr": 0.0},
                        ]
                    )
                    lab_df = st.data_editor(
                        lab_df_default,
                        num_rows="dynamic",
                        key=f"lab_editor_{idx}",
                        use_container_width=True,
                    )
                    lab_cost = float((lab_df["Hrs per unit"] * lab_df["Wage/hr"]).sum())

                    direct_cost = mat_cost + lab_cost
                    st.write(f"Direct cost (Material + Labour) per {item.unit}: ₹{direct_cost:,.2f}")

                    oh_pct_detail = st.number_input(
                        "Overheads for this item (%)",
                        min_value=0.0,
                        value=10.0,
                        step=1.0,
                        key=f"oh_detail_{idx}",
                    )
                    profit_pct_detail = st.number_input(
                        "Profit for this item (%)",
                        min_value=0.0,
                        value=10.0,
                        step=1.0,
                        key=f"profit_detail_{idx}",
                    )

                    oh_amt_detail = direct_cost * oh_pct_detail / 100.0
                    profit_amt_detail = (direct_cost + oh_amt_detail) * profit_pct_detail / 100.0
                    suggested_rate = direct_cost + oh_amt_detail + profit_amt_detail

                    st.write(f"Suggested unit rate from detailed analysis: ₹{suggested_rate:,.2f}")

                    if st.button("Use suggested rate above", key=f"use_suggested_{idx}"):
                        rate_value = suggested_rate
                        st.session_state[f"rate_{idx}"] = suggested_rate
                        st.success("Unit rate updated from detailed analysis.")

                breakdown = rate_analyzer.simple_breakdown(rate_value)

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Material", f"₹{breakdown['material']:.0f}")
                col2.metric("Labour", f"₹{breakdown['labor']:.0f}")
                col3.metric("Equipment", f"₹{breakdown['equipment']:.0f}")
                col4.metric("Overheads", f"₹{breakdown['overheads']:.0f}")

                total_amount = item.quantity * rate_value
                st.metric("Total Amount", f"₹{total_amount:,.0f}")

                rate_items.append(
                    {
                        "item": item,
                        "rate": rate_value,
                        "amount": total_amount,
                        "breakdown": breakdown,
                    }
                )

        if st.button(
            "💾 Save Rate Analysis & Proceed to BOQ", use_container_width=True
        ):
            st.session_state.rate_items = rate_items
            st.success("✅ Rate analysis saved. Go to the **BOQ** tab.")
            st.rerun()

# ============================= TAB 3: BOQ =============================
with tab_boq:
    st.subheader("Bill of Quantities (BOQ)")
    st.caption(f"Using cost index: {cost_index:.2f}% based on {dsr_year}")

    if not st.session_state.rate_items:
        st.info("💰 No rate analysis found. Please complete the **Rate Analysis** tab first.")
    else:
        st.info(
            f"Found {len(st.session_state.rate_items)} items with rates. Finalize BOQ below."
        )

        boq_gen.clear_items()
        for idx, info in enumerate(st.session_state.rate_items, start=1):
            item = info["item"]
            desc_lower = item.description.lower()

            with st.expander(f"Item {idx}: {item.description}", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    item_no = st.text_input(
                        "Item No", value=f"{idx:03d}", key=f"itemno_{idx}"
                    )
                    wbs_l1 = st.text_input(
                        "WBS Level 1",
                        value=(
                            "Earthwork"
                            if "earthwork" in desc_lower or "excavation" in desc_lower
                            else "Concrete"
                            if "concrete" in desc_lower or "rcc" in desc_lower or "pcc" in desc_lower
                            else "Masonry"
                            if "masonry" in desc_lower
                            else "Formwork"
                            if "formwork" in desc_lower
                            else "Reinforcement"
                            if "reinforcement" in desc_lower
                            else "Finishes"
                        ),
                        key=f"wbs1_{idx}",
                    )
                    dsr_keyword = st.text_input(
                        "DSR description keyword (optional)",
                        value="",
                        key=f"dsr_kw_{idx}",
                        help="Type a phrase to search DSR.",
                    )

                    rate_source = st.selectbox(
                        "Rate Source",
                        ["DSR", "Market", "Client", "Assumed"],
                        index=0,
                        key=f"rate_source_{idx}",
                    )

                with col2:
                    wbs_l2 = st.text_input(
                        "WBS Level 2",
                        value=(
                            "Excavation"
                            if "earthwork" in desc_lower or "excavation" in desc_lower
                            else "Structural concrete"
                            if "rcc" in desc_lower
                            else "PCC"
                            if "pcc" in desc_lower or "plain" in desc_lower
                            else "Wall masonry"
                            if "masonry" in desc_lower
                            else "Shuttering"
                            if "formwork" in desc_lower
                            else "Reinforcement"
                            if "reinforcement" in desc_lower
                            else "Painting"
                            if "paint" in desc_lower or "finishing" in desc_lower
                            else "Flooring"
                        ),
                        key=f"wbs2_{idx}",
                    )

                    item_note = st.text_area(
                        "Note / Justification (optional)",
                        value="",
                        key=f"note_{idx}",
                        help="Example: 'Rate as per vendor quote dated 22-12-2025'.",
                    )

                # Keyword-based DSR suggestion
                if st.button("🔎 Suggest DSR items (keyword)", key=f"suggest_dsr_{idx}"):
                    keyword = dsr_keyword.strip()
                    if not keyword:
                        if "earthwork" in desc_lower:
                            keyword = "earth"
                        elif "pcc" in desc_lower:
                            keyword = "plain concrete"
                        elif "rcc" in desc_lower:
                            keyword = "reinforced concrete"
                        elif "masonry" in desc_lower:
                            keyword = "masonry"
                        elif "plaster" in desc_lower:
                            keyword = "plaster"
                        elif "floor" in desc_lower:
                            keyword = "floor"
                        elif "formwork" in desc_lower:
                            keyword = "formwork"
                        elif "reinforcement" in desc_lower:
                            keyword = "reinforcement"
                        elif "paint" in desc_lower:
                            keyword = "paint"

                    if keyword:
                        matches = dsr_parser.find_matches(keyword, unit=item.unit)
                    else:
                        matches = dsr_parser.get_all_items()

                    if matches.empty:
                        st.warning("No matching DSR items found.")
                    else:
                        st.write(f"Suggested DSR items for '{keyword}':")
                        st.dataframe(matches, use_container_width=True)

                # AI-based DSR suggestion
                if st.button("🤖 Ask AI for DSR suggestions", key=f"ai_dsr_{idx}"):
                    dsr_df = dsr_parser.get_all_items()
                    with st.spinner("Asking AI to suggest closest DSR items..."):
                        ai_results = ai_suggester.suggest_dsr_items(
                            boq_description=item.description,
                            unit=item.unit,
                            dsr_df=dsr_df,
                            top_n=5,
                        )
                    if not ai_results:
                        st.warning("AI could not find suitable DSR suggestions.")
                    else:
                        st.write("AI-suggested DSR items (please verify before use):")
                        ai_df = pd.DataFrame(ai_results)
                        st.dataframe(ai_df, use_container_width=True)

                st.info(
                    f"Rate: ₹{info['rate']:.2f}/{item.unit} | Amount: ₹{info['amount']:,.2f}"
                )

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
                    rate_source=rate_source,
                    note=item_note,
                )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Generate BOQ Table", use_container_width=True):
                df_boq = boq_gen.generate_dataframe(project_name, project_location)
                st.session_state.boq_df = df_boq
                st.success("✅ BOQ generated!")
                st.rerun()

        if st.session_state.boq_df is not None:
            df_boq = st.session_state.boq_df

            st.markdown("### 📋 Final BOQ")
            st.dataframe(df_boq, use_container_width=True)

            st.markdown("### 📊 Section-wise totals (by WBS Level 1)")
            section_totals = (
                df_boq.groupby("WBS Level 1")["Amount (₹)"]
                .sum()
                .reset_index()
            )
            st.dataframe(section_totals, use_container_width=True)

            base_total = df_boq["Amount (₹)"].sum()
            st.metric("💎 BASE TOTAL", f"₹{base_total:,.0f}")

            st.markdown("### ⚙️ Contingency, Overheads, Profit & GST")

            contingency_pct = st.number_input(
                "Contingency (%)", min_value=0.0, value=3.0, step=0.5
            )
            overhead_pct = st.number_input(
                "Departmental overheads (%)", min_value=0.0, value=2.0, step=0.5
            )
            profit_pct = st.number_input(
                "Contractor's profit (%)", min_value=0.0, value=10.0, step=0.5
            )
            gst_pct = st.number_input(
                "GST (%)", min_value=0.0, value=18.0, step=0.5
            )

            contingency_amt = base_total * contingency_pct / 100.0
            overhead_amt = base_total * overhead_pct / 100.0
            works_plus_overheads = base_total + contingency_amt + overhead_amt
            profit_amt = works_plus_overheads * profit_pct / 100.0
            tax_base = works_plus_overheads + profit_amt
            gst_amt = tax_base * gst_pct / 100.0
            final_total = tax_base + gst_amt

            st.write(f"Contingency ({contingency_pct:.1f}%): ₹{contingency_amt:,.0f}")
            st.write(
                f"Departmental overheads ({overhead_pct:.1f}%): ₹{overhead_amt:,.0f}"
            )
            st.write(f"Contractor's profit ({profit_pct:.1f}%): ₹{profit_amt:,.0f}")
            st.write(f"GST ({gst_pct:.1f}%): ₹{gst_amt:,.0f}")
            st.metric("🔹 SANCTION ESTIMATE TOTAL", f"₹{final_total:,.0f}")

            excel_bytes = boq_gen.to_excel_bytes(
                df_boq,
                section_totals=section_totals,
                base_total=base_total,
                contingency_pct=contingency_pct,
                overhead_pct=overhead_pct,
                profit_pct=profit_pct,
                gst_pct=gst_pct,
                cost_index=cost_index,
                dsr_year=dsr_year,
            )
            st.download_button(
                label="⬇️ Download BOQ + Abstract (Excel)",
                data=excel_bytes,
                file_name=f"BOQ_{project_name.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

st.markdown("---")
st.markdown(
    "*Based on IS 1200 measurement standards. Verify IS clauses, DSR codes, Cost Index, AI suggestions, and all rates with latest CPWD/State rules before tender use.*"
)
