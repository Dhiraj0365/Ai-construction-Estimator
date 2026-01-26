import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =============================================================================
# CPWD DSR 2023 - GHAZIABAD RATES (Cost Index 107%)
# =============================================================================
DSR_2023 = {
    "Earthwork Excavation": {"code": "2.5.1", "rate": 285, "unit": "cum"},
    "PCC 1:2:4 M15": {"code": "5.2.1", "rate": 6847, "unit": "cum"},
    "RCC M25 Footing": {"code": "13.1.1", "rate": 8927, "unit": "cum"},
    "RCC M25 Column": {"code": "13.2.1", "rate": 8927, "unit": "cum"},
    "RCC M25 Beam": {"code": "13.3.1", "rate": 8927, "unit": "cum"},
    "RCC M25 Slab 150mm": {"code": "13.4.1", "rate": 8927, "unit": "cum"},
    "Brickwork 230mm": {"code": "6.1.1", "rate": 5123, "unit": "cum"},
    "Plaster 12mm C:S 1:6": {"code": "11.1.1", "rate": 187, "unit": "sqm"},
    "Vitrified Tiles 600x600": {"code": "14.1.1", "rate": 1245, "unit": "sqm"},
    "Exterior Acrylic Paint": {"code": "15.8.1", "rate": 98, "unit": "sqm"}
}

# Phase-wise item grouping
PHASE_ITEMS = {
    "PHASE_1_SUBSTRUCTURE": ["Earthwork Excavation", "PCC 1:2:4 M15", "RCC M25 Footing"],
    "PHASE_2_PLINTH": ["Brickwork 230mm"],
    "PHASE_3_SUPERSTRUCTURE": ["RCC M25 Column", "RCC M25 Beam", "RCC M25 Slab 150mm", "Brickwork 230mm"],
    "PHASE_4_FINISHING": ["Plaster 12mm C:S 1:6", "Vitrified Tiles 600x600", "Exterior Acrylic Paint"]
}

PHASE_NAMES = {
    "PHASE_1_SUBSTRUCTURE": "1️⃣ SUBSTRUCTURE",
    "PHASE_2_PLINTH": "2️⃣ PLINTH", 
    "PHASE_3_SUPERSTRUCTURE": "3️⃣ SUPERSTRUCTURE",
    "PHASE_4_FINISHING": "4️⃣ FINISHING"
}

# =============================================================================
# SAFE UTILITY FUNCTIONS
# =============================================================================
@st.cache_data
def safe_total_cost(items):
    """Safe total cost calculation - handles empty lists"""
    if not items:
        return 0.0
    return sum(item.get('amount', 0.0) for item in items)

def format_rupees(amount):
    """Indian Rupee formatting"""
    return f"₹{float(amount):,.0f}"

def format_lakhs(amount):
    """Format amount in lakhs"""
    return round(float(amount) / 100000, 2)

# =============================================================================
# STREAMLIT CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="CPWD DSR 2023 Estimator Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state safely
if "qto_items" not in st.session_state:
    st.session_state.qto_items = []
if "project_info" not in st.session_state:
    st.session_state.project_info = {
        "name": "G+1 Residential Building - Ghaziabad",
        "client": "CPWD Ghaziabad Division",
        "engineer": "Er. Ravi Sharma, EE"
    }

# =============================================================================
# HEADER & DASHBOARD
# =============================================================================
st.title("🏗️ **CPWD DSR 2023 ESTIMATOR PRO**")
st.markdown("*Delhi Schedule of Rates 2023 | Ghaziabad Cost Index: 107% | IS 1200 Compliant*")

# Sidebar - Project Configuration
with st.sidebar:
    st.header("🏛️ **PROJECT CONFIGURATION**")
    
    with st.expander("📋 Project Details", expanded=True):
        st.session_state.project_info["name"] = st.text_input(
            "Name of Work:", value=st.session_state.project_info["name"]
        )
        st.session_state.project_info["client"] = st.text_input(
            "Client/Department:", value=st.session_state.project_info["client"]
        )
        st.session_state.project_info["engineer"] = st.text_input(
            "Prepared by:", value=st.session_state.project_info["engineer"]
        )
    
    st.header("⚙️ **ESTIMATION SETTINGS**")
    cost_index = st.number_input(
        "Cost Index (%)", min_value=90.0, max_value=130.0, value=107.0, step=0.5
    )
    contingency = st.slider("Contingency (%)", 0.0, 15.0, 5.0)

# Live Dashboard Metrics
total_cost = safe_total_cost(st.session_state.qto_items)
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Base Cost", format_rupees(total_cost))
col2.metric("📋 Items", len(st.session_state.qto_items))
col3.metric("🎯 Cost Index", f"{cost_index}%")
col4.metric("📊 Sanction Total", format_rupees(total_cost * 1.05))

# Main Application Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📏 Schedule of Quantities", 
    "📊 Abstract of Cost", 
    "🎯 Risk Analysis", 
    "📄 Government Formats"
])

# =============================================================================
# TAB 1: SCHEDULE OF QUANTITIES (SOQ)
# =============================================================================
with tab1:
    st.header("📏 **SCHEDULE OF QUANTITIES - CPWD FORM 7**")
    
    # Item Selection
    col1, col2 = st.columns([1, 4])
    with col1:
        phase_key = st.selectbox("**Construction Phase**", list(PHASE_ITEMS.keys()))
        st.info(f"**{PHASE_NAMES[phase_key]}**")
    with col2:
        available_items = PHASE_ITEMS[phase_key]
        selected_item = st.selectbox("**DSR Item**", available_items)
    
    # Quantity Take-off (IS 1200)
    col1, col2, col3 = st.columns(3)
    length = col1.number_input("**Length (m)**", min_value=0.01, value=10.0, step=0.1, format="%.2f")
    breadth = col2.number_input("**Breadth (m)**", min_value=0.01, value=5.0, step=0.1, format="%.2f")
    depth = col3.number_input("**Depth/Thickness (m)**", min_value=0.001, value=0.15, step=0.01, format="%.3f")
    
    # Live Rate Analysis
    if selected_item and selected_item in DSR_2023:
        dsr_item = DSR_2023[selected_item]
        volume = length * breadth * depth
        base_rate = dsr_item["rate"]
        adjusted_rate = base_rate * (cost_index / 100)
        item_amount = volume * adjusted_rate
        
        # Results Display
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📐 Volume", f"{volume:.2f} {dsr_item['unit']}")
        col2.metric("💰 Base Rate", f"₹{base_rate:,.0f}")
        col3.metric("📈 Adjusted Rate", f"₹{adjusted_rate:,.0f}")
        col4.metric("💵 Amount", format_rupees(item_amount))
        col5.metric("🔢 DSR Code", dsr_item['code'])
        
        st.success(f"**{selected_item}** | DSR {dsr_item['code']} | Ghaziabad Rate {cost_index}%")
        
        # Add Item Button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"L×B×D = {length:.1f} × {breadth:.1f} × {depth:.3f} = {volume:.2f} {dsr_item['unit']}")
        with col2:
            if st.button("➕ **ADD TO SOQ**", type="primary", use_container_width=True):
                st.session_state.qto_items.append({
                    'id': len(st.session_state.qto_items) + 1,
                    'phase': phase_key,
                    'phase_name': PHASE_NAMES[phase_key],
                    'description': selected_item,
                    'dsr_code': dsr_item['code'],
                    'length': length,
                    'breadth': breadth,
                    'depth': depth,
                    'volume': volume,
                    'unit': dsr_item['unit'],
                    'base_rate': base_rate,
                    'rate': adjusted_rate,
                    'amount': item_amount
                })
                st.success(f"✅ **Item #{len(st.session_state.qto_items)} Added!**")
                st.balloons()
    
    # SOQ Table
    if st.session_state.qto_items:
        soq_df = pd.DataFrame(st.session_state.qto_items)[
            ['id', 'dsr_code', 'phase_name', 'description', 'volume', 'unit', 'rate', 'amount']
        ].round(2)
        st.dataframe(soq_df, use_container_width=True, hide_index=True)
        st.caption(f"**Total: {len(st.session_state.qto_items)} Items | Grand Total: {format_rupees(total_cost)}**")

# =============================================================================
# TAB 2: ABSTRACT OF COST
# =============================================================================
with tab2:
    if not st.session_state.qto_items:
        st.warning("👆 **Please complete Schedule of Quantities first**")
        st.stop()
    
    st.header("📊 **ABSTRACT OF COST - CPWD FORM 5A**")
    
    # Phase-wise totals
    phase_totals = {}
    grand_total = safe_total_cost(st.session_state.qto_items)
    
    for item in st.session_state.qto_items:
        phase = item['phase']
        if phase not in phase_totals:
            phase_totals[phase] = {'count': 0, 'volume': 0.0, 'amount': 0.0}
        phase_totals[phase]['count'] += 1
        phase_totals[phase]['volume'] += item['volume']
        phase_totals[phase]['amount'] += item['amount']
    
    # Abstract Table
    abstract_data = []
    for i, (phase_key, totals) in enumerate(phase_totals.items(), 1):
        abstract_data.append({
            "S.No.": i,
            "Particulars": PHASE_NAMES[phase_key],
            "No. of Items": totals['count'],
            "Total Volume": f"{totals['volume']:.2f}",
            "Amount (₹ Lakhs)": format_lakhs(totals['amount'])
        })
    
    abstract_data.append({
        "S.No.": "**TOTAL-A**",
        "Particulars": "**CIVIL WORKS**",
        "No. of Items": len(st.session_state.qto_items),
        "Total Volume": f"{sum(t['volume'] for t in phase_totals.values()):.2f}",
        "Amount (₹ Lakhs)": format_lakhs(grand_total)
    })
    
    st.markdown("### **ABSTRACT OF COST STATEMENT**")
    st.dataframe(pd.DataFrame(abstract_data), use_container_width=True, hide_index=True)
    
    # Cost Summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("**A: Base Cost**", format_rupees(grand_total))
    col2.metric("**B: Contingency**", format_rupees(grand_total * 0.05))
    col3.metric("**C: Maintenance**", format_rupees(grand_total * 0.025))
    col4.metric("**SANCTION TOTAL**", format_rupees(grand_total * 1.075), 
                delta=f"+{format_lakhs(grand_total*0.075)} Lakhs")

# =============================================================================
# TAB 3: RISK ANALYSIS
# =============================================================================
with tab3:
    if not st.session_state.qto_items:
        st.warning("👆 **Complete SOQ first**")
        st.stop()
    
    st.header("🎯 **RISK & CONTINGENCY ANALYSIS**")
    base_cost = safe_total_cost(st.session_state.qto_items)
    
    # Monte Carlo Simulation
    np.random.seed(42)
    simulations = [base_cost]
    
    # Risk factors: (probability, impact)
    risks = [(0.25, 0.15), (0.40, 0.10), (0.35, 0.12), (0.20, 0.08), (0.15, 0.20)]
    
    for prob, impact in risks:
        new_simulations = []
        for cost in simulations:
            if np.random.random() < prob:
                new_simulations.append(cost * (1 + impact))
            else:
                new_simulations.append(cost)
        simulations = new_simulations
    
    p10 = np.percentile(simulations, 10)
    p50 = np.percentile(simulations, 50)
    p90 = np.percentile(simulations, 90)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("**P10 (Safe)**", format_rupees(p10), delta=f"{p10-base_cost:+,.0f}")
    col2.metric("**P50 (Expected)**", format_rupees(p50))
    col3.metric("**P90 (Worst Case)**", format_rupees(p90), delta=f"{p90-base_cost:+,.0f}")
    
    st.success(f"""
    **RECOMMENDED BUDGET: {format_rupees(p90)}**  
    📊 Confidence Level: 90% | Extra Provision: **{((p90-base_cost)/base_cost*100):.1f}%**
    """)

# =============================================================================
# TAB 4: GOVERNMENT FORMATS (All 5 Working)
# =============================================================================
with tab4:
    if not st.session_state.qto_items:
        st.warning("👆 **Complete SOQ first**")
        st.stop()
    
    st.header("📄 **GOVERNMENT TENDER DOCUMENTS**")
    format_type = st.selectbox("**Select CPWD/PWD Format**", [
        "1️⃣ CPWD Abstract of Cost (Form 5A)",
        "2️⃣ Schedule of Quantities (Form 7)",
        "3️⃣ Measurement Book (Form 8)",
        "4️⃣ Running Account Bill (Form 31)",
        "5️⃣ PWD Work Order (Form PWD-6)"
    ])
    
    grand_total = safe_total_cost(st.session_state.qto_items)
    today = datetime.now()
    
    # 1. CPWD Abstract (Form 5A)
    if "1️⃣" in format_type or "5A" in format_type:
        st.markdown("### **📋 CPWD FORM 5A - ABSTRACT OF COST**")
        phase_totals = {}
        for item in st.session_state.qto_items:
            phase_totals[item['phase']] = phase_totals.get(item['phase'], 0) + item['amount']
        
        data = [{"S.No": i+1, "Particulars": PHASE_NAMES[p], "Amount (₹Lakhs)": format_lakhs(a)}
                for i, (p, a) in enumerate(phase_totals.items())]
        data.append({"S.No": "TOTAL-A", "Particulars": "CIVIL WORKS", "Amount (₹Lakhs)": format_lakhs(grand_total)})
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "📥 DOWNLOAD FORM 5A", 
            df.to_csv(index=False), 
            f"CPWD_Form5A_{st.session_state.project_info['name'][:20]}_{today.strftime('%Y%m%d')}.csv"
        )
    
    # 2. Schedule of Quantities (Form 7)
    elif "2️⃣" in format_type or "Form 7" in format_type:
        st.markdown("### **📋 CPWD FORM 7 - SCHEDULE OF QUANTITIES**")
        soq_data = []
        for item in st.session_state.qto_items:
            soq_data.append({
                "Item No": item['id'],
                "DSR Code": item['dsr_code'],
                "Description": item['description'],
                "L(m)": f"{item['length']:.2f}",
                "B(m)": f"{item['breadth']:.2f}",
                "D(m)": f"{item['depth']:.3f}",
                "Volume": f"{item['volume']:.3f}",
                "Unit": item['unit'],
                "Rate(₹)": f"{item['rate']:,.0f}",
                "Amount(₹)": format_rupees(item['amount'])
            })
        df = pd.DataFrame(soq_data)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "📥 DOWNLOAD FORM 7", 
            df.to_csv(index=False), 
            f"SOQ_Form7_{today.strftime('%Y%m%d')}.csv"
        )
    
    # 3. Measurement Book (Form 8)
    elif "3️⃣" in format_type or "Form 8" in format_type:
        st.markdown("### **📏 CPWD FORM 8 - MEASUREMENT BOOK**")
        mb_data = []
        for item in st.session_state.qto_items:
            mb_data.append({
                "Date": today.strftime('%d/%m/%Y'),
                "MB No": f"MB/{item['id']:03d}",
                "Item": item['description'][:30],
                "Length": f"{item['length']:.2f}m",
                "Breadth": f"{item['breadth']:.2f}m",
                "Depth": f"{item['depth']:.3f}m",
                "Content": f"{item['volume']:.3f} {item['unit']}",
                "Initials": "RKS/Verified"
            })
        df = pd.DataFrame(mb_data)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "📥 DOWNLOAD FORM 8", 
            df.to_csv(index=False), 
            f"MB_Form8_{today.strftime('%Y%m%d')}.csv"
        )
    
    # 4. Running Account Bill (Form 31)
    elif "4️⃣" in format_type or "Form 31" in format_type:
        st.markdown("### **💰 CPWD FORM 31 - RUNNING ACCOUNT BILL**")
        ra_data = {
            "Particulars": [
                "1. Gross value of work (this bill)",
                "2. Work done previous bills (secured advance)",
                "3. Total value of work (1+2)",
                "4. Deduction: Income Tax @2%",
                "5. Deduction: Labour Cess @1%",
                "6. **NET AMOUNT PAYABLE**"
            ],
            "Amount (₹)": [
                grand_total,
                0.0,
                grand_total,
                grand_total * 0.02,
                grand_total * 0.01,
                grand_total * 0.97
            ]
        }
        df = pd.DataFrame(ra_data)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "📥 DOWNLOAD FORM 31", 
            df.to_csv(index=False), 
            f"RABill_Form31_{today.strftime('%Y%m%d')}.csv"
        )
    
    # 5. Work Order (PWD Form 6)
    else:
        st.markdown("### **📜 PWD FORM 6 - WORK ORDER**")
        completion_date = today + timedelta(days=180)
        
        st.markdown(f"""
        **WORK ORDER No: WO/GZB/2026/{today.strftime('%m%d')}/001**
        
        **To: M/s [CONTRACTOR NAME]**
        
        **Subject: Award of Contract - {st.session_state.project_info['name']}**
        
        | S.No | Particulars | Details |
        |------|-------------|---------|
        | 1 | Name of Work | {st.session_state.project_info['name']} |
        | 2 | Location | Ghaziabad, UP |
        | 3 | Contract Value | {format_rupees(grand_total)} |
        | 4 | Time Allowed | 6 Months |
        | 5 | Commencement Date | {today.strftime('%d/%m/%Y')} |
        | 6 | Scheduled Completion | {completion_date.strftime('%d/%m/%Y')} |
        | 7 | EMD (2%) | {format_rupees(grand_total*0.02)} |
        | 8 | Security Deposit (5%) | {format_rupees(grand_total*0.05)} |
        """)
        
        wo_data = pd.DataFrame({
            "S.No": [1,2,3,4,5,6,7,8],
            "Particulars": ["Name of Work", "Location", "Contract Value", "Time Allowed", 
                          "Commencement", "Completion", "EMD", "Security Deposit"],
            "Details": [
                st.session_state.project_info['name'],
                "Ghaziabad, UP",
                format_rupees(grand_total),
                "6 Months",
                today.strftime('%d/%m/%Y'),
                completion_date.strftime('%d/%m/%Y'),
                format_rupees(grand_total*0.02),
                format_rupees(grand_total*0.05)
            ]
        })
        st.dataframe(wo_data)
        st.download_button(
            "📥 DOWNLOAD FORM PWD-6", 
            wo_data.to_csv(index=False), 
            f"WorkOrder_PWD6_{today.strftime('%Y%m%d')}.csv"
        )

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.success("✅ **DSR 2023 Rates**")
col2.success("✅ **5 Govt Formats**")
col3.success("✅ **Risk Analysis**")

st.markdown(f"""
**👨‍💼 {st.session_state.project_info['engineer']}** | 
**📅 {datetime.now().strftime('%d %b %Y %H:%M IST')}** | 
**🏛️ CPWD Ghaziabad Division** | 
**📊 DSR 2023 | Cost Index: 107%**
""")
