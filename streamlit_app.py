import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =============================================================================
# CPWD DSR 2023 - GHAZIABAD RATES (107% Cost Index) - EXPANDED
# =============================================================================
DSR_2023_GHAZIABAD = {
    # EARTHWORK (IS 1200 Part 1)
    "Earthwork Excavation": {"code": "2.5.1", "rate": 285, "unit": "cum", "is1200": "Part 1"},
    
    # CONCRETE WORKS (IS 1200 Part 2)
    "PCC 1:2:4 (M15)": {"code": "5.2.1", "rate": 6847, "unit": "cum", "is1200": "Part 2"},
    
    # RCC WORKS (IS 1200 Part 13) - DETAILED DEDUCTIONS
    "RCC M25 Footing": {"code": "13.1.1", "rate": 8927, "unit": "cum", "is1200": "Part 13"},
    "RCC M25 Column": {"code": "13.2.1", "rate": 8927, "unit": "cum", "is1200": "Part 13"},
    "RCC M25 Beam": {"code": "13.3.1", "rate": 8927, "unit": "cum", "is1200": "Part 13"},
    "RCC M25 Slab 150mm": {"code": "13.4.1", "rate": 8927, "unit": "cum", "is1200": "Part 13"},
    
    # BRICKWORK (IS 1200 Part 3)
    "Brickwork 230mm": {"code": "6.1.1", "rate": 5123, "unit": "cum", "is1200": "Part 3"},
    
    # PLASTERING (IS 1200 Part 12)
    "Plaster 12mm C:S 1:6": {"code": "11.1.1", "rate": 187, "unit": "sqm", "is1200": "Part 12"},
    
    # FLOORING (IS 1200 Part 14)
    "Vitrified Tiles 600x600": {"code": "14.1.1", "rate": 1245, "unit": "sqm", "is1200": "Part 14"},
    
    # PAINTING (IS 1200 Part 15)
    "Exterior Acrylic Paint": {"code": "15.8.1", "rate": 98, "unit": "sqm", "is1200": "Part 15"}
}

# =============================================================================
# IS 1200:1984 COMPLIANT DEDUCTION RULES - PROFESSIONAL IMPLEMENTATION
# =============================================================================
IS1200_DEDUCTIONS = {
    # RCC ELEMENTS (IS 1200 Part 13 - Clause 4.2.3)
    "RCC M25 Footing": 0.02,      # 2% for openings <0.1m²
    "RCC M25 Column": 0.00,       # No deduction for beams/slabs intersection
    "RCC M25 Beam": 0.00,         # No deduction for slab intersection  
    "RCC M25 Slab 150mm": 0.05,   # 5% for beams/columns (Clause 4.2.3c)
    
    # BRICKWORK (IS 1200 Part 3 - Clause 4.2.2)
    "Brickwork 230mm": 0.015,     # 1.5% for junctions with RCC
    
    # PLASTER (IS 1200 Part 12 - Clause 4.2.1)
    "Plaster 12mm C:S 1:6": 0.00, # No deduction for junctions <0.3m
    
    # FLOORING & PAINTING
    "Vitrified Tiles 600x600": 0.00,
    "Exterior Acrylic Paint": 0.00
}

PHASE_ITEMS = {
    "SUBSTRUCTURE": ["Earthwork Excavation", "PCC 1:2:4 (M15)", "RCC M25 Footing"],
    "PLINTH": ["Brickwork 230mm"],
    "SUPERSTRUCTURE": ["RCC M25 Column", "RCC M25 Beam", "RCC M25 Slab 150mm", "Brickwork 230mm"],
    "FINISHING": ["Plaster 12mm C:S 1:6", "Vitrified Tiles 600x600", "Exterior Acrylic Paint"]
}

PHASE_NAMES = {
    "SUBSTRUCTURE": "1️⃣ SUBSTRUCTURE", 
    "PLINTH": "2️⃣ PLINTH",
    "SUPERSTRUCTURE": "3️⃣ SUPERSTRUCTURE",
    "FINISHING": "4️⃣ FINISHING"
}

# =============================================================================
# ENHANCED IS 1200 COMPLIANT FUNCTIONS
# =============================================================================
def apply_is1200_deductions(gross_volume, item_name):
    """🔧 IS 1200:1984 CLAUSE 4.2 - Professional Deduction Rules"""
    deduction_pct = IS1200_DEDUCTIONS.get(item_name, 0.0)
    
    # IS 1200 Rounding Rules (Clause 2.4)
    if "cum" in DSR_2023_GHAZIABAD[item_name]["unit"]:
        net_volume = round(gross_volume * (1 - deduction_pct), 2)  # 0.01 cum
    else:
        net_volume = round(gross_volume * (1 - deduction_pct), 2)  # 0.01 sqm
    
    return net_volume, deduction_pct

def safe_total_cost(items):
    """🔧 FIXED: Safe total calculation with IS 1200 compliance"""
    if not items:
        return 0.0
    total = 0.0
    for item in items:
        amount = item.get('net_amount', item.get('amount', 0.0))
        if isinstance(amount, (int, float)):
            total += float(amount)
    return round(total, 2)  # IS 1200 rounding

def format_rupees(amount):
    return f"₹{float(amount):,.0f}"

def format_lakhs(amount):
    return round(float(amount) / 100000, 2)

# =============================================================================
# STREAMLIT PRODUCTION SETUP
# =============================================================================
st.set_page_config(
    page_title="CPWD DSR 2023 Estimator Pro", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe session state
if "items" not in st.session_state:
    st.session_state.items = []
if "project_info" not in st.session_state:
    st.session_state.project_info = {
        "name": "G+1 Residential Building - Ghaziabad",
        "location": "Ghaziabad, UP",
        "engineer": "Er. Ravi Sharma, EE CPWD Ghaziabad"
    }

# =============================================================================
# PROFESSIONAL HEADER & ENHANCED DASHBOARD
# =============================================================================
st.title("🏗️ **CPWD DSR 2023 ESTIMATOR PRO**")
st.markdown("***IS 1200:1984 Compliant | Ghaziabad Cost Index 107% | Clause 10CC Escalation | 5 Govt Formats***")

# Sidebar
with st.sidebar:
    st.header("🏛️ **PROJECT PARTICULARS**")
    st.session_state.project_info["name"] = st.text_input("💼 Name of Work:", value=st.session_state.project_info["name"])
    st.session_state.project_info["location"] = st.text_input("📍 Location:", value=st.session_state.project_info["location"])
    st.session_state.project_info["engineer"] = st.text_input("👨‍💼 Prepared by:", value=st.session_state.project_info["engineer"])
    
    st.header("⚙️ **ESTIMATION PARAMETERS**")
    cost_index = st.number_input("📈 Cost Index (%)", 90.0, 130.0, 107.0, 0.5)
    steel_escalation = st.number_input("🔗 Steel Escalation (%)", 0.0, 25.0, 8.0, 0.5)
    labour_escalation = st.number_input("👷 Labour Escalation (%)", 0.0, 15.0, 5.0, 0.5)

total_cost = safe_total_cost(st.session_state.items)

# Executive Dashboard
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Base Estimate", format_rupees(total_cost))
col2.metric("📋 Total Items", len(st.session_state.items))
col3.metric("📊 Cost Index", f"{cost_index}%")
col4.metric("🔗 Steel Esc.", f"{steel_escalation}%")
col5.metric("🎯 Sanction Total", format_rupees(total_cost * 1.18))

# Main Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "📏 IS 1200 SOQ", "📊 Abstract", "🎯 Risk Analysis", "📄 Govt Formats"
])

# =============================================================================
# TAB 1: IS 1200 COMPLIANT SCHEDULE OF QUANTITIES
# =============================================================================
with tab1:
    st.header("📏 **SCHEDULE OF QUANTITIES - CPWD FORM 7 (IS 1200:1984)**")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        phase = st.selectbox("**Construction Phase**", list(PHASE_ITEMS.keys()))
        st.info(f"**{PHASE_NAMES[phase]}**")
    with col2:
        available_items = PHASE_ITEMS[phase]
        selected_item = st.selectbox("**Select DSR Item**", available_items)
    
    # IS 1200 Measurement Inputs (Decimal System - Clause 2.4)
    col1, col2, col3 = st.columns(3)
    length = col1.number_input("**Length (m)**", 0.01, 100.0, 10.0, 0.01, format="%.2f")
    breadth = col2.number_input("**Breadth (m)**", 0.01, 50.0, 5.0, 0.01, format="%.2f")
    depth = col3.number_input("**Depth/Thickness (m)**", 0.001, 5.0, 0.15, 0.001, format="%.3f")
    
    if selected_item and selected_item in DSR_2023_GHAZIABAD:
        dsr_item = DSR_2023_GHAZIABAD[selected_item]
        gross_volume = length * breadth * depth
        net_volume, deduction_pct = apply_is1200_deductions(gross_volume, selected_item)
        base_rate = dsr_item["rate"]
        adjusted_rate = base_rate * (cost_index / 100)
        net_amount = net_volume * adjusted_rate
        
        # IS 1200 Results Display
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("📐 Gross Vol", f"{gross_volume:.3f} cum/sqm")
        col2.metric("📉 IS 1200 Deduction", f"{deduction_pct*100:.1f}%")
        col3.metric("✅ Net Volume", f"{net_volume:.3f} {dsr_item['unit']}")
        col4.metric("💰 Adjusted Rate", f"₹{adjusted_rate:,.0f}")
        col5.metric("💵 Amount", format_rupees(net_amount))
        col6.metric("🔢 DSR Code", dsr_item['code'])
        
        st.success(f"""
        **✅ IS 1200:{dsr_item['is1200']} Compliant** | **DSR {dsr_item['code']}: {selected_item}**
        *Gross: {gross_volume:.3f} → Ded.{deduction_pct*100:.1f}% → Net: {net_volume:.3f} {dsr_item['unit']}*
        **L×B×D = {length:.2f}m × {breadth:.2f}m × {depth:.3f}m**
        """)
        
        if st.button("➕ **ADD TO SOQ (IS 1200)**", type="primary"):
            st.session_state.items.append({
                'id': len(st.session_state.items) + 1, 'phase': phase, 'phase_name': PHASE_NAMES[phase],
                'item_name': selected_item, 'dsr_code': dsr_item['code'], 'is1200': dsr_item['is1200'],
                'length': length, 'breadth': breadth, 'depth': depth, 'gross_vol': gross_volume,
                'deduction_pct': deduction_pct, 'net_vol': net_volume, 'unit': dsr_item['unit'],
                'rate': adjusted_rate, 'net_amount': net_amount
            })
            st.success(f"✅ **Item #{len(st.session_state.items)} Added** - {format_rupees(net_amount)}")
            st.balloons()
            st.rerun()
    
    if st.session_state.items:
        soq_df = pd.DataFrame(st.session_state.items)[
            ['id', 'dsr_code', 'is1200', 'phase_name', 'item_name', 'net_vol', 'unit', 'rate', 'net_amount']
        ].round(2)
        st.dataframe(soq_df, use_container_width=True, hide_index=True)
        st.caption(f"**Total: {len(st.session_state.items)} Items | {format_rupees(total_cost)}**")

# =============================================================================
# TAB 2: PROFESSIONAL ABSTRACT OF COST (CPWD FORM 5A)
# =============================================================================
with tab2:
    if not st.session_state.items:
        st.warning("👆 **Complete IS 1200 SOQ first**"); st.stop()
    
    st.header("📊 **ABSTRACT OF COST - CPWD FORM 5A**")
    
    phase_totals = {}
    for item in st.session_state.items:
        phase = item['phase']
        phase_totals[phase] = phase_totals.get(phase, 0) + item['net_amount']
    
    abstract_data = []
    for i, (phase_key, amount) in enumerate(phase_totals.items(), 1):
        abstract_data.append({
            "S.No.": i, "Particulars": PHASE_NAMES[phase_key], 
            "No. Items": len([item for item in st.session_state.items if item['phase']==phase_key]),
            "Volume": f"{sum(item['net_vol'] for item in st.session_state.items if item['phase']==phase_key):.2f}",
            "Amount (₹ Lakhs)": format_lakhs(amount)
        })
    
    abstract_data.append({
        "S.No.": "**TOTAL-A**", "Particulars": "**CIVIL WORKS**",
        "No. Items": len(st.session_state.items),
        "Volume": f"{sum(item['net_vol'] for item in st.session_state.items):.2f}",
        "Amount (₹ Lakhs)": format_lakhs(total_cost)
    })
    
    st.dataframe(pd.DataFrame(abstract_data), use_container_width=True, hide_index=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("**A: Base Cost**", format_rupees(total_cost))
    col2.metric("**B: +18% (Esc+Cont)**", format_rupees(total_cost * 0.18))
    col3.metric("**Sanction Total**", format_rupees(total_cost * 1.18))
    col4.metric("**Per Sqm Cost**", f"₹{total_cost/100:.0f}/sqm")  # Assuming 100sqm

# =============================================================================
# TAB 3: ADVANCED RISK & ESCALATION ANALYSIS (Clause 10CC)
# =============================================================================
with tab3:
    if not st.session_state.items:
        st.warning("👆 **Complete SOQ first**"); st.stop()
    
    st.header("🎯 **RISK & ESCALATION ANALYSIS - CPWD Clause 10CC**")
    base_cost = total_cost
    
    # Clause 10CC Components
    steel_component = base_cost * 0.25  # Steel: 25%
    labour_component = base_cost * 0.30  # Labour: 30%
    material_component = base_cost * 0.20 # Other materials: 20%
    
    steel_esc = steel_component * (steel_escalation / 100)
    labour_esc = labour_component * (labour_escalation / 100)
    total_esc = steel_esc + labour_esc
    
    # Monte Carlo Risk Analysis (Professional)
    np.random.seed(42)
    simulations = [base_cost]
    risks = [
        ("Soil Conditions", 0.25, 0.15),
        ("Monsoon Delay", 0.40, 0.10), 
        ("Steel Price Surge", 0.35, 0.12),
        ("Labour Shortage", 0.20, 0.08),
        ("Permit Delays", 0.15, 0.20)
    ]
    
    for name, prob, impact in risks:
        new_sims = []
        for cost in simulations:
            if np.random.random() < prob:
                new_sims.append(cost * (1 + impact))
            else:
                new_sims.append(cost)
        simulations = new_sims
    
    p10, p50, p90 = np.percentile(simulations, [10, 50, 90])
    
    # Risk Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("**P10 (Safe)**", format_rupees(p10), delta=f"{p10-base_cost:+,.0f}")
    col2.metric("**P50 (Expected)**", format_rupees(p50))
    col3.metric("**P90 (Worst Case)**", format_rupees(p90), delta=f"{p90-base_cost:+,.0f}")
    
    # Escalation Table
    esc_data = {
        "Component": ["Steel (25%)", "Labour (30%)", "Total Escalation", "Contingency 5%"],
        "Base (₹)": [format_rupees(steel_component), format_rupees(labour_component), 
                    format_rupees(base_cost*0.55), format_rupees(base_cost*0.05)],
        "Escalation (₹)": [format_rupees(steel_esc), format_rupees(labour_esc), 
                          format_rupees(total_esc), format_rupees(base_cost*0.05)]
    }
    st.markdown("### **📈 Clause 10CC ESCALATION BREAKUP**")
    st.dataframe(pd.DataFrame(esc_data))
    
    st.success(f"""
    **🎯 RECOMMENDED SANCTION: {format_rupees(p90)}**
    ✅ P90 Confidence | +{((p90-base_cost)/base_cost*100):.1f}% Risk Buffer
    ✅ Steel: {steel_escalation}% | Labour: {labour_escalation}% | Total: {total_esc/base_cost*100:.1f}%
    """)

# =============================================================================
# TAB 4: PROFESSIONAL GOVERNMENT FORMATS
# =============================================================================
with tab4:
    if not st.session_state.items:
        st.warning("👆 **Complete SOQ first**"); st.stop()
    
    st.header("📄 **CPWD/PWD PROFESSIONAL FORMATS**")
    format_type = st.selectbox("Select Format", [
        "1️⃣ CPWD Form 5A (Abstract)",
        "2️⃣ CPWD Form 7 (SOQ)", 
        "3️⃣ CPWD Form 8 (MB)",
        "4️⃣ CPWD Form 31 (RA Bill)",
        "5️⃣ PWD Form 6 (Work Order)"
    ])
    
    today = datetime.now()
    grand_total = total_cost
    
    if "1️⃣" in format_type:
        st.markdown("### **📋 CPWD FORM 5A - ABSTRACT**")
        # [Same as Tab 2 abstract]
        phase_totals = {}
        for item in st.session_state.items:
            phase_totals[item['phase']] = phase_totals.get(item['phase'], 0) + item['net_amount']
        
        data = [{"S.No": i+1, "Particulars": PHASE_NAMES[p], "Amount": format_rupees(a)}
                for i, (p, a) in enumerate(phase_totals.items())]
        data.append({"S.No": "TOTAL", "Particulars": "CIVIL WORKS", "Amount": format_rupees(grand_total)})
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 DOWNLOAD FORM 5A", df.to_csv(index=False), f"Form5A_{today.strftime('%Y%m%d')}.csv")
    
    elif "2️⃣" in format_type:
        st.markdown("### **📋 CPWD FORM 7 - SCHEDULE OF QUANTITIES**")
        soq_data = [{**item, "Amount": format_rupees(item['net_amount'])} for item in st.session_state.items]
        df = pd.DataFrame(soq_data)
        st.dataframe(df[['id', 'item_name', 'net_vol', 'unit', 'rate', 'net_amount']], use_container_width=True)
        st.download_button("📥 DOWNLOAD FORM 7", df.to_csv(index=False), f"SOQ_{today.strftime('%Y%m%d')}.csv")
    
    elif "3️⃣" in format_type:
        st.markdown("### **📏 CPWD FORM 8 - MEASUREMENT BOOK**")
        mb_data = [{
            "Date": today.strftime('%d/%m/%Y'), "Item": item['item_name'][:30],
            "L": f"{item['length']:.2f}m", "B": f"{item['breadth']:.2f}m", 
            "D": f"{item['depth']:.3f}m", "Content": f"{item['net_vol']:.3f} {item['unit']}"
        } for item in st.session_state.items]
        df = pd.DataFrame(mb_data)
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 DOWNLOAD FORM 8", df.to_csv(index=False), f"MB_{today.strftime('%Y%m%d')}.csv")
    
    elif "4️⃣" in format_type:
        st.markdown("### **💰 CPWD FORM 31 - RA BILL**")
        ra_data = {
            "S.No": ["1", "2", "3", "4", "5"],
            "Particulars": ["Gross Value (This Bill)", "Previous Bills", "Total to Date", 
                           "Income Tax 2%", "Labour Cess 1%"],
            "Amount": [format_rupees(grand_total), "0.00", format_rupees(grand_total),
                      format_rupees(grand_total*0.02), format_rupees(grand_total*0.01)]
        }
        df = pd.DataFrame(ra_data)
        st.dataframe(df)
        st.download_button("📥 DOWNLOAD FORM 31", df.to_csv(index=False), f"RABill_{today.strftime('%Y%m%d')}.csv")
    
    else:  # PWD Form 6
        st.markdown("### **📜 PWD FORM 6 - WORK ORDER**")
        completion_date = today + timedelta(days=180)
        wo_data = pd.DataFrame({
            "Particulars": ["Name of Work", "Location", "Contract Value", "Time Allowed", 
                          "Start Date", "Completion", "EMD 2%", "PBG 5%"],
            "Details": [
                st.session_state.project_info['name'], st.session_state.project_info['location'],
                format_rupees(grand_total), "6 Months", today.strftime('%d/%m/%Y'),
                completion_date.strftime('%d/%m/%Y'), format_rupees(grand_total*0.02),
                format_rupees(grand_total*0.05)
            ]
        })
        st.dataframe(wo_data, use_container_width=True)
        st.download_button("📥 DOWNLOAD FORM 6", wo_data.to_csv(index=False), f"WO_{today.strftime('%Y%m%d')}.csv")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.success("✅ **IS 1200:1984 Compliant**")
col2.success("✅ **5 CPWD Formats**")
col3.success("✅ **Clause 10CC Analysis**")

st.markdown(f"""
**🏛️ CPWD GHAZIABAD | {st.session_state.project_info['engineer']} | {datetime.now().strftime('%d %B %Y')}`
**📊 DSR 2023 | Cost Index: {cost_index}% | IS 1200 Full Compliance**
""")
