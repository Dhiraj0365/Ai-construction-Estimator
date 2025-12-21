import streamlit as st
import pandas as pd

from is1200_rules import IS1200Engine, MeasurementItem
from rate_analyzer import RateAnalyzer
from boq_generator import BOQGenerator
from dsr_parser import DSRParser


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
    help="Reference only; use to note which DSR/SOR the base rates are from.",
)

st.title("🧮 AI Construction Estimator")
st.caption(
    "Quantity Take-Off (QTO), Rate Analysis, and BOQ as per IS 1200 with DSR mapping and Cost Index."
)

tab_qto, tab_rate, tab_boq = st.tabs(
    ["📏 Quantity Take-Off", "💰 Rate Analysis", "📋 Bill of Quantities"]
)

# ============================= TAB 1: QTO =============================
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
            "Formwork (IS 1200 Part 5)",
            "Reinforcement Steel (IS 1200 Part 8)",
            "Painting / Finishing (IS 1200 Part 13)",
        ],
        index=0,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.number_input("Length (m)", min_value=0.1, value=10.0)
    with col2:
        width = st.number_input("Width (m)", min_value=0.1, value=5.0)
    with col3:
        depth_or_thk = st.number_input(
            "Depth / Thickness / Height (m or kg*)",
            min_value=0.05,
            value=1.2,
            help="For reinforcement, treat this as total weight in kg for now.",
        )

    lead = st.number_input("Lead (m) (for earthwork)", min_value=0.0, value=50.0)

    if st.button("➕ Add Measured Item to QTO", use_container_width=True):
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
                    height=depth_or_thk,
                    thickness_mm=12.0,
                )

            elif "Flooring" in qto_type:
                item = engine.measure_flooring(
                    length=length,
                    width=width,
                    thickness_mm=20.0,
                )

            elif "Formwork" in qto_type:
                form_area = length * depth_or_thk
                item = engine.measure_formwork(
                    area=form_area,
                    element_type="beam/slab",
                )

            elif "Reinforcement Steel" in qto_type:
                item = engine.measure_reinforcement(
                    weight_kg=depth_or_thk,
                    bar_type="TMT",
                )

            elif "Painting / Finishing" in qto_type:
                paint_area = length * depth_or_thk
                item = engine.measure_painting(
                    area=paint_area,
                    system="Acrylic paint",
                )

            else:
                st.error("Unsupported measurement type selected.")
                st.stop()

            st.session_state.qto_items.append(item)
            st.success(f"✅ Added: {item.description} — {item.quantity:.2f} {item.unit}")
        except Exception as e:
            st.error(f"❌ Error while adding item: {e}")

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
                if "earthwork" in desc_lower or "excavation" in desc_lower:
                    base_rate = 260.0
                elif any(x in desc_lower for x in ["plain cement concrete", "pcc"]):
                    base_rate = 4500.0
                elif any(x in desc_lower for x in ["reinforced cement concrete", "rcc"]):
                    base_rate = 7500.0
                elif "masonry" in desc_lower:
                    base_rate = 5500.0
                elif "plaster" in desc_lower:
                    base_rate = 250.0
                elif "floor" in desc_lower or "tile" in desc_lower:
                    base_rate = 800.0
                elif "formwork" in desc_lower:
                    base_rate = 900.0
                elif "reinforcement steel" in desc_lower:
                    base_rate = 80.0  # ₹/kg
                elif "painting" in desc_lower or "finishing" in desc_lower:
                    base_rate = 120.0
                else:
                    base_rate = 1000.0

                default_rate = base_rate * (cost_index / 100.0)

                rate_value = st.number_input(
                    f"Rate (₹/{item.unit})",
                    min_value=0.0,
                    value=default_rate,
                    key=f"rate_{idx}",
                    help="Enter unit rate as per latest DSR / PWD schedule",
                )

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
                            if "concrete" in desc_lower
                            or "rcc" in desc_lower
                            or "pcc" in desc_lower
                            else "Masonry"
                            if "masonry" in desc_lower
                            else "Formwork"
                            if "formwork" in desc_lower
                            else "Reinforcement"
                            if "reinforcement steel" in desc_lower
                            else "Finishes"
                        ),
                        key=f"wbs1_{idx}",
                    )
                    dsr_keyword = st.text_input(
                        "DSR description keyword (optional)",
                        value="",
                        key=f"dsr_kw_{idx}",
                        help="Type a phrase to search DSR, e.g. 'earthwork excavation', 'PCC 1:4:8', 'M25 slab', '12 mm plaster', 'vitrified tiles'.",
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
                            if "plain cement concrete" in desc_lower
                            else "Wall masonry"
                            if "masonry" in desc_lower
                            else "Shuttering"
                            if "formwork" in desc_lower
                            else "Reinforcement"
                            if "reinforcement steel" in desc_lower
                            else "Painting"
                            if "painting" in desc_lower or "finishing" in desc_lower
                            else "Flooring"
                        ),
                        key=f"wbs2_{idx}",
                    )

                if st.button("🔎 Suggest DSR items", key=f"suggest_dsr_{idx}"):
                    keyword = dsr_keyword.strip()
                    if not keyword:
                        if "earthwork" in desc_lower or "excavation" in desc_lower:
                            keyword = "earth"
                        elif "plain cement concrete" in desc_lower or "pcc" in desc_lower:
                            keyword = "plain cement concrete"
                        elif "reinforced cement concrete" in desc_lower or "rcc" in desc_lower:
                            keyword = "reinforced cement concrete"
                        elif "masonry" in desc_lower:
                            keyword = "masonry"
                        elif "plaster" in desc_lower:
                            keyword = "plaster"
                        elif "floor" in desc_lower or "tile" in desc_lower:
                            keyword = "floor"
                        elif "formwork" in desc_lower:
                            keyword = "formwork"
                        elif "reinforcement steel" in desc_lower or "tmt" in desc_lower:
                            keyword = "reinforcement"
                        elif "painting" in desc_lower or "finishing" in desc_lower:
                            keyword = "paint"

                    if keyword:
                        matches = dsr_parser.find_matches(keyword, unit=item.unit)
                    else:
                        matches = dsr_parser.get_all_items()

                    if matches.empty:
                        st.warning("No matching DSR items found. Refine the keyword or check DSR CSV.")
                    else:
                        st.write(f"Suggested DSR items for '{keyword}':")
                        st.dataframe(matches, use_container_width=True)

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
    "*Based on IS 1200 measurement standards. Verify DSR codes, cost index, rates and percentages with latest CPWD/State rules before tender use.*"
)
