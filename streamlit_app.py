# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =============================================================================
# 🔥 CPWD DSR 2023 + MULTI-LOCATION INDICES
# =============================================================================
CPWD_BASE_DSR_2023 = {
    # EARTHWORK
    "Earthwork in Excavation (2.5.1)": {
        "code": "2.5.1",
        "rate": 278,
        "unit": "cum",
        "type": "volume",
        "category": "earthwork",
    },

    # PLAIN CEMENT CONCRETE
    "PCC 1:2:4 (M15) (5.2.1)": {
        "code": "5.2.1",
        "rate": 6666,
        "unit": "cum",
        "type": "volume",
        "category": "pcc",
    },

    # RCC CONCRETE (concrete only)
    "RCC M25 Footing (13.1.1)": {
        "code": "13.1.1",
        "rate": 8692,
        "unit": "cum",
        "type": "volume",
        "category": "rcc_concrete",
    },
    "RCC M25 Column (13.2.1)": {
        "code": "13.2.1",
        "rate": 8692,
        "unit": "cum",
        "type": "volume",
        "category": "rcc_concrete",
    },
    "RCC M25 Beam (13.3.1)": {
        "code": "13.3.1",
        "rate": 8692,
        "unit": "cum",
        "type": "volume",
        "category": "rcc_concrete",
    },
    "RCC M25 Slab 150mm (13.4.1)": {
        "code": "13.4.1",
        "rate": 8692,
        "unit": "cum",
        "type": "volume",
        "category": "rcc_concrete",
    },

    # REINFORCEMENT (update code/rate from CPWD DSR 2023)
    "Steel reinforcement for R.C.C. work (TMT Fe500)": {
        "code": "5.xx.x",        # TODO: put exact DSR code
        "rate": 78,              # ₹/kg (example, update as per DSR)
        "unit": "kg",
        "type": "weight",
        "category": "reinforcement",
    },

    # FORMWORK (update codes/rates as per CPWD DSR 2023)
    "Centering & shuttering for foundations and footings": {
        "code": "5.yy.y",
        "rate": 950,             # ₹/sqm (example)
        "unit": "sqm",
        "type": "area",
        "category": "formwork",
    },
    "Centering & shuttering for columns": {
        "code": "5.yy.z",
        "rate": 1150,            # ₹/sqm (example)
        "unit": "sqm",
        "type": "area",
        "category": "formwork",
    },
    "Centering & shuttering for beams & slabs": {
        "code": "5.yy.w",
        "rate": 1050,            # ₹/sqm (example)
        "unit": "sqm",
        "type": "area",
        "category": "formwork",
    },

    # BRICKWORK
    "Brickwork 230mm (6.1.1)": {
        "code": "6.1.1",
        "rate": 4993,
        "unit": "cum",
        "type": "volume",
        "category": "brickwork",
    },

    # PLASTER
    "Plaster 12mm 1:6 (11.1.1)": {
        "code": "11.1.1",
        "rate": 182,
        "unit": "sqm",
        "type": "area",
        "category": "plaster",
    },

    # PUTTY (separate from paint – update DSR code/rate)
    "Wall putty 2 mm average thickness": {
        "code": "13.zz.z",
        "rate": 95,
        "unit": "sqm",
        "type": "area",
        "category": "putty",
    },

    # FLOORING
    "Vitrified Tiles 600x600 (14.1.1)": {
        "code": "14.1.1",
        "rate": 1215,
        "unit": "sqm",
        "type": "area",
        "category": "flooring",
    },

    # PAINTING
    "Exterior Acrylic Paint (15.8.1)": {
        "code": "15.8.1",
        "rate": 95,
        "unit": "sqm",
        "type": "area",
        "category": "painting",
    },
}

LOCATION_INDICES = {
    "Delhi": 100.0,
    "Ghaziabad": 107.0,
    "Noida": 105.0,
    "Gurgaon": 110.0,
    "Mumbai": 135.5,
    "Pune": 128.0,
    "Bangalore": 116.0,
    "Chennai": 122.0,
    "Hyderabad": 118.0,
    "Kolkata": 112.0,
    "Lucknow": 102.0,
    "Kanpur": 101.0,
}

PHASE_GROUPS = {
    "1️⃣ SUBSTRUCTURE": [
        "Earthwork in Excavation (2.5.1)",
        "PCC 1:2:4 (M15) (5.2.1)",
        "RCC M25 Footing (13.1.1)",
    ],
    "2️⃣ PLINTH": [
        "RCC M25 Beam (13.3.1)",
    ],
    "3️⃣ SUPERSTRUCTURE": [
        "RCC M25 Column (13.2.1)",
        "RCC M25 Beam (13.3.1)",
        "RCC M25 Slab 150mm (13.4.1)",
        "Brickwork 230mm (6.1.1)",
    ],
    "4️⃣ FINISHING": [
        "Plaster 12mm 1:6 (11.1.1)",
        "Wall putty 2 mm average thickness",
        "Vitrified Tiles 600x600 (14.1.1)",
        "Exterior Acrylic Paint (15.8.1)",
    ],
}

# =============================================================================
# 🧱 COMPOSITE DEFINITIONS – AUTO RCC EXPANSION
# =============================================================================
RCC_COMPONENT_DEFAULTS = {
    "RCC M25 Footing (13.1.1)": {
        "steel_kg_per_cum": 80.0,
        "formwork_type": "Centering & shuttering for foundations and footings",
    },
    "RCC M25 Column (13.2.1)": {
        "steel_kg_per_cum": 140.0,
        "formwork_type": "Centering & shuttering for columns",
    },
    "RCC M25 Beam (13.3.1)": {
        "steel_kg_per_cum": 120.0,
        "formwork_type": "Centering & shuttering for beams & slabs",
    },
    "RCC M25 Slab 150mm (13.4.1)": {
        "steel_kg_per_cum": 100.0,
        "formwork_type": "Centering & shuttering for beams & slabs",
    },
}

# Finishing dependencies (simplified)
FINISHING_DEPENDENCIES = {
    "Plaster 12mm 1:6 (11.1.1)": {
        "requires_categories": ["brickwork", "rcc_concrete"],
    },
    "Wall putty 2 mm average thickness": {
        "requires_categories": ["plaster"],
    },
    "Exterior Acrylic Paint (15.8.1)": {
        "requires_categories": ["plaster", "putty"],
    },
}

PHASE_ORDER = {
    "1️⃣ SUBSTRUCTURE": 1,
    "2️⃣ PLINTH": 2,
    "3️⃣ SUPERSTRUCTURE": 3,
    "4️⃣ FINISHING": 4,
}

# =============================================================================
# 🎯 IS 1200 ENGINE
# =============================================================================
class IS1200Engine:
    """
    Basic helpers following IS 1200 philosophy.
    """

    @staticmethod
    def volume(L: float, B: float, D: float, deductions: float = 0.0):
        gross = L * B * D
        net = max(0.0, gross - deductions)
        return {
            "gross": gross,
            "net": net,
            "deductions": deductions,
            "pct": (deductions / gross * 100.0) if gross > 0 else 0.0,
        }

    @staticmethod
    def wall_finish_area(
        length: float,
        height: float,
        sides: int = 2,
        openings=None,
        small_opening_limit: float = 0.5,
    ):
        """
        length, height in m.
        openings: list of {"w":..,"h":..} in m.
        No deduction for openings <= small_opening_limit sqm (typical IS 1200).
        """
        if openings is None:
            openings = []

        gross = sides * length * height
        deduct = 0.0

        for o in openings:
            a = o["w"] * o["h"]
            if a > small_opening_limit:
                deduct += a * min(sides, 2)

        net = max(0.0, gross - deduct)
        return {"gross": gross, "net": net, "deductions": deduct}

    @staticmethod
    def formwork_column_area(L: float, B: float, H: float):
        # Perimeter × height for 4 faces
        return 2.0 * (L + B) * H

    @staticmethod
    def formwork_beam_area(breadth: float, depth: float, length: float):
        # 3 sides of a beam (bottom + 2 sides) × length
        return (2.0 * depth + breadth) * length

    @staticmethod
    def formwork_slab_area(length: float, breadth: float):
        # Soffit area
        return length * breadth


# =============================================================================
# HELPERS
# =============================================================================
def format_rupees(amount: float) -> str:
    return f"₹{amount:,.0f}"


def format_lakhs(amount: float) -> str:
    return f"{amount / 100000:.2f} L"


@st.cache_data
def monte_carlo(base_cost: float, n: int = 1000):
    np.random.seed(42)
    sims = np.full(n, base_cost, dtype=np.float64)
    risks = [(0.30, 0.12), (0.25, 0.15), (0.20, 0.25)]
    for prob, impact in risks:
        mask = np.random.random(n) < prob
        sims[mask] *= 1.0 + impact
    return {
        "p10": float(np.percentile(sims, 10)),
        "p50": float(np.percentile(sims, 50)),
        "p90": float(np.percentile(sims, 90)),
    }


def analyse_dependencies(qto_items):
    messages = []

    if not qto_items:
        return messages

    phases_present = {item["phase"] for item in qto_items}
    if "4️⃣ FINISHING" in phases_present and "3️⃣ SUPERSTRUCTURE" not in phases_present:
        messages.append(
            "Finishing items found but no superstructure items. Check sequencing."
        )

    cats_present = {item.get("category", "") for item in qto_items}

    for item in qto_items:
        name = item["item"]
        deps = FINISHING_DEPENDENCIES.get(name)
        if not deps:
            continue
        req_cats = deps.get("requires_categories", [])
        for rc in req_cats:
            if rc not in cats_present:
                messages.append(
                    f"'{name}' added without any base item in category '{rc}'. "
                    "Example: no painting without plaster, no plaster without masonry."
                )

    return messages


# =============================================================================
# STREAMLIT SETUP
# =============================================================================
st.set_page_config(
    page_title="CPWD DSR 2023 Pro", page_icon="🏗️", layout="wide"
)

if "qto_items" not in st.session_state:
    st.session_state.qto_items = []

if "project_info" not in st.session_state:
    st.session_state.project_info = {
        "name": "G+1 Residential",
        "client": "CPWD Division",
        "engineer": "Er. Ravi Sharma",
    }

# =============================================================================
# PROFESSIONAL UI
# =============================================================================
st.markdown(
    """
<div style='background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding:2rem; border-radius:1rem; color:white; text-align:center'>
  <h1 style='margin:0;'>🏗️ Construction Estimator Master v2.1</h1>
  <p>✅ Mixed Types Fixed | Multi-Location | IS 1200 | RCC Auto-Expansion</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🏛️ PROJECT")
    for key in st.session_state.project_info:
        st.session_state.project_info[key] = st.text_input(
            key.replace("_", " ").title(),
            value=st.session_state.project_info[key],
        )

    st.header("📍 LOCATION")
    location = st.selectbox("Select City", list(LOCATION_INDICES.keys()))
    cost_index = LOCATION_INDICES[location]
    st.info(f"**{location}: {cost_index}%**")

    st.header("⚙️ RATES")
    contingency = st.slider("Contingency", 0.0, 10.0, 5.0)
    escalation = st.slider("Escalation p.a.", 3.0, 8.0, 5.5)

# Dashboard
total_cost = sum(item.get("amount", 0.0) for item in st.session_state.qto_items)
mc = monte_carlo(total_cost) if total_cost else {}
cols = st.columns(5)
cols[0].metric("💰 Base Cost", format_rupees(total_cost))
cols[1].metric("📋 Items", len(st.session_state.qto_items))
cols[2].metric("🎯 Index", f"{cost_index}%")
cols[3].metric("📊 Sanction", format_rupees(total_cost * 1.075))
cols[4].metric("🎯 P90", format_rupees(mc.get("p90", 0.0)))

tab1, tab2, tab3, tab4 = st.tabs(["📏 SOQ", "📊 Abstract", "🎯 Risk", "📄 Formats"])

# =============================================================================
# HELPER: ADD RCC WITH COMPONENTS
# =============================================================================
def add_rcc_with_components(
    base_item_name, base_item, phase, L, B, D, qto, cost_index
):
    """
    Auto-add RCC concrete + reinforcement + formwork for audit-safe estimate.
    """
    base_id_start = len(st.session_state.qto_items) + 1
    volume = float(qto["net"])

    # 1) Concrete
    rate_conc = base_item["rate"] * (cost_index / 100.0)
    amt_conc = volume * rate_conc

    st.session_state.qto_items.append(
        {
            "id": base_id_start,
            "phase": phase,
            "item": base_item_name,
            "dsr_code": base_item["code"],
            "length": float(L),
            "breadth": float(B),
            "depth": float(D),
            "quantity": volume,
            "unit": base_item["unit"],
            "rate": float(rate_conc),
            "amount": float(amt_conc),
            "category": base_item.get("category", ""),
        }
    )

    comp_def = RCC_COMPONENT_DEFAULTS.get(base_item_name)
    if not comp_def:
        return

    # 2) Reinforcement
    steel_item_name = "Steel reinforcement for R.C.C. work (TMT Fe500)"
    steel_item = CPWD_BASE_DSR_2023[steel_item_name]
    steel_kg = volume * comp_def["steel_kg_per_cum"]
    rate_steel = steel_item["rate"] * (cost_index / 100.0)
    amt_steel = steel_kg * rate_steel

    st.session_state.qto_items.append(
        {
            "id": base_id_start + 1,
            "phase": phase,
            "item": steel_item_name + f" (for {base_item_name})",
            "dsr_code": steel_item["code"],
            "length": 0.0,
            "breadth": 0.0,
            "depth": 0.0,
            "quantity": steel_kg,
            "unit": steel_item["unit"],
            "rate": float(rate_steel),
            "amount": float(amt_steel),
            "category": steel_item.get("category", ""),
        }
    )

    # 3) Formwork
    formwork_name = comp_def["formwork_type"]
    formwork_item = CPWD_BASE_DSR_2023[formwork_name]

    if "Column" in base_item_name:
        formwork_area = IS1200Engine.formwork_column_area(L, B, D)
    elif "Beam" in base_item_name:
        formwork_area = IS1200Engine.formwork_beam_area(B, D, L)
    elif "Slab" in base_item_name:
        formwork_area = IS1200Engine.formwork_slab_area(L, B)
    else:
        # Footings etc. – approx 4 vertical faces
        formwork_area = IS1200Engine.formwork_column_area(L, B, D)

    rate_fw = formwork_item["rate"] * (cost_index / 100.0)
    amt_fw = formwork_area * rate_fw

    st.session_state.qto_items.append(
        {
            "id": base_id_start + 2,
            "phase": phase,
            "item": formwork_name + f" (for {base_item_name})",
            "dsr_code": formwork_item["code"],
            "length": float(L),
            "breadth": float(B),
            "depth": float(D),
            "quantity": formwork_area,
            "unit": formwork_item["unit"],
            "rate": float(rate_fw),
            "amount": float(amt_fw),
            "category": formwork_item.get("category", ""),
        }
    )


# =============================================================================
# TAB 1: SOQ – WITH IS 1200 & RCC AUTO-EXPANSION
# =============================================================================
with tab1:
    st.header("📏 **CPWD FORM 7 - IS 1200 SOQ**")

    col1, col2 = st.columns([1, 3])
    phase = col1.selectbox("Phase", list(PHASE_GROUPS.keys()))
    selected_item = col2.selectbox("DSR Item", PHASE_GROUPS[phase])

    if selected_item in CPWD_BASE_DSR_2023:
        dsr_item = CPWD_BASE_DSR_2023[selected_item]
        D = 0.0  # default depth

        if dsr_item["type"] == "volume":
            c1, c2, c3, c4 = st.columns(4)
            L = c1.number_input(
                "Length (m)",
                min_value=float(0.01),
                max_value=float(100.0),
                value=float(10.0),
                step=float(0.1),
            )
            B = c2.number_input(
                "Breadth (m)",
                min_value=float(0.01),
                max_value=float(100.0),
                value=float(5.0),
                step=float(0.1),
            )
            D = c3.number_input(
                "Depth/Height (m)",
                min_value=float(0.001),
                max_value=float(5.0),
                value=float(0.15),
                step=float(0.01),
            )
            deductions = c4.number_input(
                "Deductions (cum)",
                min_value=float(0.0),
                max_value=float(10.0),
                value=float(0.0),
                step=float(0.01),
            )

            qto = IS1200Engine.volume(L, B, D, deductions)
            rate = dsr_item["rate"] * (cost_index / 100.0)
            amount = qto["net"] * rate

        else:
            # AREA ITEMS
            c1, c2, c3 = st.columns(3)
            if dsr_item.get("category") in ["plaster", "painting", "putty"]:
                L = c1.number_input(
                    "Wall Length (m)",
                    min_value=float(0.01),
                    max_value=float(100.0),
                    value=float(10.0),
                    step=float(0.1),
                )
                H = c2.number_input(
                    "Wall Height (m)",
                    min_value=float(0.01),
                    max_value=float(10.0),
                    value=float(3.0),
                    step=float(0.1),
                )
                openings_area = c3.number_input(
                    "Area of large openings >0.5 sqm (sqm)",
                    min_value=float(0.0),
                    max_value=float(100.0),
                    value=float(0.0),
                    step=float(0.1),
                )

                openings = []
                if openings_area > 0:
                    # One equivalent opening; IS deduction rule handled by engine
                    openings = [{"w": 1.0, "h": openings_area}]

                qto = IS1200Engine.wall_finish_area(
                    L, H, sides=2, openings=openings
                )
                B = H  # store height in breadth for MB/formats
            else:
                # Flooring, tiles, formwork, etc.
                L = c1.number_input(
                    "Length (m)",
                    min_value=float(0.01),
                    max_value=float(100.0),
                    value=float(10.0),
                    step=float(0.1),
                )
                B = c2.number_input(
                    "Breadth (m)",
                    min_value=float(0.01),
                    max_value=float(100.0),
                    value=float(5.0),
                    step=float(0.1),
                )
                openings_area = c3.number_input(
                    "Deductions (sqm)",
                    min_value=float(0.0),
                    max_value=float(100.0),
                    value=float(0.0),
                    step=float(0.1),
                )
                gross = L * B
                net = max(0.0, gross - openings_area)
                qto = {
                    "gross": gross,
                    "net": net,
                    "deductions": openings_area,
                }

            rate = dsr_item["rate"] * (cost_index / 100.0)
            amount = qto["net"] * rate

        # RESULTS
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "📐 Quantity", f"{qto['net']:.3f} {dsr_item['unit']}"
        )
        c2.metric("💰 Rate", f"₹{rate:,.0f}")
        c3.metric("💵 Amount", format_rupees(amount))
        c4.metric("🔢 DSR", dsr_item["code"])

        if dsr_item["type"] == "volume":
            st.info(
                f"**IS 1200**: {L:.2f}×{B:.2f}×{D:.3f} = "
                f"{qto['gross']:.3f} – {qto['deductions']:.3f} "
                f"= **{qto['net']:.3f} {dsr_item['unit']}**"
            )
        else:
            st.info(
                f"**IS 1200**: Gross {qto['gross']:.3f} – Deductions {qto['deductions']:.3f} "
                f"= **{qto['net']:.3f} {dsr_item['unit']}**"
            )

        if st.button("➕ ADD TO SOQ", type="primary"):
            if dsr_item.get("category") == "rcc_concrete":
                # Auto-expand RCC
                add_rcc_with_components(
                    selected_item,
                    dsr_item,
                    phase,
                    L,
                    B,
                    D,
                    qto,
                    cost_index,
                )
            else:
                # Single items (earthwork, PCC, brickwork, plaster, tiles, paint, etc.)
                st.session_state.qto_items.append(
                    {
                        "id": len(st.session_state.qto_items) + 1,
                        "phase": phase,
                        "item": selected_item,
                        "dsr_code": dsr_item["code"],
                        "length": float(L),
                        "breadth": float(B),
                        "depth": float(D) if dsr_item["type"] == "volume" else 0.0,
                        "quantity": float(qto["net"]),
                        "unit": dsr_item["unit"],
                        "rate": float(rate),
                        "amount": float(amount),
                        "category": dsr_item.get("category", ""),
                    }
                )

            st.success("✅ Item(s) added with mandatory components where applicable.")
            st.balloons()

    if st.session_state.qto_items:
        df = pd.DataFrame(st.session_state.qto_items)[
            ["id", "dsr_code", "phase", "item", "quantity", "unit", "rate", "amount"]
        ]
        st.dataframe(df.round(2), use_container_width=True)


# =============================================================================
# TAB 2: ABSTRACT + TECHNICAL CHECKS
# =============================================================================
with tab2:
    if st.session_state.qto_items:
        st.header("📊 **FORM 5A ABSTRACT**")
        phase_totals = {}
        for item in st.session_state.qto_items:
            phase_totals[item["phase"]] = phase_totals.get(
                item["phase"], 0.0
            ) + item["amount"]

        data = []
        for i, (p, a) in enumerate(phase_totals.items()):
            data.append(
                {
                    "S.No.": i + 1,
                    "Particulars": p,
                    "Amount": format_rupees(a),
                }
            )
        data.append(
            {
                "S.No.": "TOTAL",
                "Particulars": "CIVIL WORKS",
                "Amount": format_rupees(total_cost),
            }
        )
        df_abs = pd.DataFrame(data)
        st.dataframe(df_abs, use_container_width=True)
        st.download_button(
            "📥 Form 5A",
            df_abs.to_csv(index=False),
            f"Form5A_{datetime.now().strftime('%Y%m%d')}.csv",
        )

        st.subheader("🛡️ Technical & Audit Checks")
        issues = analyse_dependencies(st.session_state.qto_items)
        if issues:
            for msg in issues:
                st.warning("• " + msg)
        else:
            st.success(
                "Estimate passes basic sequencing & dependency checks "
                "(RCC components, plaster, putty, painting)."
            )
    else:
        st.info("Add SOQ items in Tab 1 to view abstract.")


# =============================================================================
# TAB 3: RISK ANALYSIS
# =============================================================================
with tab3:
    st.header("🎯 **RISK ANALYSIS**")
    if total_cost:
        mc = monte_carlo(total_cost)
        c1, c2, c3 = st.columns(3)
        c1.metric("P10", format_rupees(mc["p10"]))
        c2.metric("P50", format_rupees(mc["p50"]))
        c3.metric("P90", format_rupees(mc["p90"]))
        st.success(f"**Recommended Budget (P90): {format_rupees(mc['p90'])}**")
    else:
        st.info("Add items in SOQ to run risk analysis.")


# =============================================================================
# TAB 4: CPWD/PWD FORMATS
# =============================================================================
with tab4:
    if not st.session_state.qto_items:
        st.warning("👆 **Complete SOQ first**")
        st.stop()

    st.header("📄 **CPWD/PWD GOVERNMENT FORMATS - ALL 5 WORKING**")

    format_type = st.selectbox(
        "**Select CPWD/PWD Format**",
        [
            "1️⃣ Form 5A - Abstract of Cost",
            "2️⃣ Form 7 - Schedule of Quantities",
            "3️⃣ Form 8 - Measurement Book",
            "4️⃣ Form 31 - Running Account Bill ✅",
            "5️⃣ PWD Form 6 - Work Order ✅",
        ],
    )

    grand_total = sum(item["amount"] for item in st.session_state.qto_items)
    today = datetime.now()

    # 1️⃣ FORM 5A - ABSTRACT OF COST
    if "Form 5A" in format_type:
        st.markdown("### **📋 CPWD FORM 5A - ABSTRACT OF COST**")
        phase_totals = {}
        for item in st.session_state.qto_items:
            phase = item["phase"]
            phase_totals[phase] = phase_totals.get(phase, 0.0) + float(
                item["amount"]
            )

        form5a_data = []
        for i, (phase_name, amount) in enumerate(phase_totals.items(), 1):
            form5a_data.append(
                {
                    "S.No.": i,
                    "Description": phase_name,
                    "No.Items": len(
                        [
                            it
                            for it in st.session_state.qto_items
                            if it["phase"] == phase_name
                        ]
                    ),
                    "Amount (₹)": format_rupees(amount),
                }
            )

        form5a_data.append(
            {
                "S.No.": "**TOTAL-A**",
                "Description": "**CIVIL WORKS**",
                "No.Items": len(st.session_state.qto_items),
                "Amount (₹)": format_rupees(grand_total),
            }
        )

        df5a = pd.DataFrame(form5a_data)
        st.dataframe(df5a, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 DOWNLOAD FORM 5A",
            df5a.to_csv(index=False),
            f"CPWD_Form5A_{today.strftime('%Y%m%d')}.csv",
        )

    # 2️⃣ FORM 7 - SCHEDULE OF QUANTITIES
    elif "Form 7" in format_type:
        st.markdown("### **📋 CPWD FORM 7 - SCHEDULE OF QUANTITIES**")
        soq_data = []
        for item in st.session_state.qto_items:
            soq_data.append(
                {
                    "Item No": item["id"],
                    "DSR Code": item["dsr_code"],
                    "Description": item["item"],
                    "Quantity": f"{float(item['quantity']):.3f}",
                    "Unit": item["unit"],
                    "Rate (₹)": f"₹{float(item['rate']):,.0f}",
                    "Amount (₹)": format_rupees(float(item["amount"])),
                }
            )
        soq_data.append(
            {
                "Item No": "**TOTAL**",
                "DSR Code": "",
                "Description": "**GRAND TOTAL**",
                "Quantity": "",
                "Unit": "",
                "Rate (₹)": "",
                "Amount (₹)": format_rupees(grand_total),
            }
        )

        df7 = pd.DataFrame(soq_data)
        st.dataframe(df7, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 DOWNLOAD FORM 7",
            df7.to_csv(index=False),
            f"SOQ_Form7_{today.strftime('%Y%m%d')}.csv",
        )

    # 3️⃣ FORM 8 - MEASUREMENT BOOK
    elif "Form 8" in format_type:
        st.markdown(
            "### **📏 CPWD FORM 8 - MEASUREMENT BOOK** ✅ DIMENSIONS FIXED"
        )
        mb_data = []
        for item in st.session_state.qto_items:
            mb_data.append(
                {
                    "Date": today.strftime("%d/%m/%Y"),
                    "MB Page": f"MB/{int(item['id']):03d}",
                    "Item Description": item["item"][:40],
                    "Length": f"{float(item['length']):.2f} m",
                    "Breadth": f"{float(item['breadth']):.2f} m",
                    "Depth": f"{float(item['depth']):.3f} m",
                    "Content": f"{float(item['quantity']):.3f} {item['unit']}",
                    "Initials": "RKS/Checked & Verified",
                }
            )

        df8 = pd.DataFrame(mb_data)
        st.dataframe(df8, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 DOWNLOAD FORM 8",
            df8.to_csv(index=False),
            f"MB_Form8_{today.strftime('%Y%m%d')}.csv",
        )

    # 4️⃣ FORM 31 - RUNNING ACCOUNT BILL
    elif "Form 31" in format_type:
        st.markdown("### **💰 CPWD FORM 31 - RUNNING ACCOUNT BILL** ✅")

        ra_data = {
            "S.No.": [1, 2, 3, 4, 5, 6, 7],
            "Particulars": [
                "Gross value of work measured (this bill)",
                "Work done - previous bills",
                "Total value of work done (1+2)",
                "Deductions:",
                "Income Tax @2%",
                "Labour Cess @1%",
                "**NET AMOUNT PAYABLE**",
            ],
            "Amount (₹)": [
                format_rupees(grand_total),
                format_rupees(0.0),
                format_rupees(grand_total),
                "",
                format_rupees(grand_total * 0.02),
                format_rupees(grand_total * 0.01),
                format_rupees(grand_total * 0.97),
            ],
        }

        df31 = pd.DataFrame(ra_data)
        st.dataframe(df31, use_container_width=True, hide_index=True)

        csv31 = df31.to_csv(index=False)
        st.download_button(
            "📥 DOWNLOAD FORM 31",
            csv31,
            f"RAB_Form31_{today.strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        c1, c2 = st.columns(2)
        c1.metric("**Gross Value**", format_rupees(grand_total))
        c2.metric("**Net Payable**", format_rupees(grand_total * 0.97))

    # 5️⃣ PWD FORM 6 - WORK ORDER
    elif "PWD Form 6" in format_type:
        st.markdown("### **📜 PWD FORM 6 - WORK ORDER** ✅")
        completion_date = today + timedelta(days=180)

        wo_data = {
            "S.No.": list(range(1, 10)),
            "Particulars": [
                "Name of Work",
                "Location",
                "Probable Amount of Contract",
                "Earnest Money Deposit (2%)",
                "Security Deposit (5%)",
                "Time Allowed",
                "Date of Commencement",
                "Scheduled Completion Date",
                "Performance Guarantee (3%)",
            ],
            "Details": [
                st.session_state.project_info["name"],
                location,
                format_rupees(grand_total),
                format_rupees(grand_total * 0.02),
                format_rupees(grand_total * 0.05),
                "6 (Six) Months",
                today.strftime("%d/%m/%Y"),
                completion_date.strftime("%d/%m/%Y"),
                format_rupees(grand_total * 0.03),
            ],
        }

        df6 = pd.DataFrame(wo_data)
        st.dataframe(df6, use_container_width=True, hide_index=True)

        csv6 = df6.to_csv(index=False)
        st.download_button(
            "📥 DOWNLOAD PWD FORM 6",
            csv6,
            f"WorkOrder_PWD6_{today.strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        st.markdown(
            f"""
**WORK ORDER No: WO/{location[:3].upper()}/2026/{today.strftime('%m%d')}/001**

**To: M/s [CONTRACTOR NAME]**

**Subject: Award of Contract - {st.session_state.project_info['name']}**
"""
        )

st.success("✅ **All 5 CPWD/PWD formats and RCC auto-expansion are now active.**")
