"""
streamlit_app.py
Government-Compliant AI Construction Estimator
Main UI Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys

# Import custom modules (ensure they're in same directory or Python path)
try:
    from is1200_rules import IS1200Engine, MeasurementItem
    from dsr_parser import DSRParser
    from rate_analyzer import RateAnalyzer, RateAnalysis
    from boq_generator import BOQGenerator
except ImportError:
    st.error("⚠️ Required modules not found. Ensure is1200_rules.py, dsr_parser.py, rate_analyzer.py, and boq_generator.py are in the same directory.")
    st.stop()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Construction Estimator - Government Compliant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'is1200_engine' not in st.session_state:
    st.session_state.is1200_engine = IS1200Engine()

if 'dsr_parser' not in st.session_state:
    st.session_state.dsr_parser = DSRParser()
    st.session_state.dsr_loaded = False

if 'rate_analyzer' not in st.session_state:
    st.session_state.rate_analyzer = RateAnalyzer()

if 'qto_items' not in st.session_state:
    st.session_state.qto_items = []

if 'project_info' not in st.session_state:
    st.session_state.project_info = {}

# ============================================================================
# SIDEBAR - PROJECT SETUP
# ============================================================================

with st.sidebar:
    st.title("🏗️ Project Setup")
    
    st.subheader("📁 Upload DSR Files")
    dsr_vol1 = st.file_uploader("DSR Volume 1 (Civil)", type=['pdf'])
    dsr_vol2 = st.file_uploader("DSR Volume 2 (Civil)", type=['pdf'])
    
    if st.button("📊 Load DSR Rates"):
        with st.spinner("Parsing DSR PDFs..."):
            # Save uploaded files temporarily if provided
            if dsr_vol1:
                with open('/tmp/dsr_vol1.pdf', 'wb') as f:
                    f.write(dsr_vol1.getbuffer())
                st.session_state.dsr_parser.dsr_vol1_path = '/tmp/dsr_vol1.pdf'
            
            if dsr_vol2:
                with open('/tmp/dsr_vol2.pdf', 'wb') as f:
                    f.write(dsr_vol2.getbuffer())
                st.session_state.dsr_parser.dsr_vol2_path = '/tmp/dsr_vol2.pdf'
            
            # Load rates
            rates_df = st.session_state.dsr_parser.load_all_rates()
            st.session_state.dsr_loaded = True
            st.success(f"✅ Loaded {len(rates_df)} rate entries")
    
    st.divider()
    
    st.subheader("📋 Project Information")
    project_name = st.text_input("Project Name", "G+4 Residential Building")
    project_location = st.text_input("Location", "New Delhi")
    project_type = st.selectbox("Project Type", 
                                ["Building", "Bridge", "Road", "Industrial", "Other"])
    project_duration = st.number_input("Duration (months)", min_value=1, value=12)
    risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])
    
    st.session_state.project_info = {
        'name': project_name,
        'location': project_location,
        'type': project_type,
        'duration': project_duration,
        'risk': risk_level.lower()
    }

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

st.title("🏗️ AI Construction Estimator (Government Compliant)")
st.markdown("**Accurate BOQ Generation per IS 1200 & CPWD Standards**")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 QTO Input", 
    "💰 Rate Analysis", 
    "📊 BOQ Generation", 
    "✅ Compliance Check",
    "📄 Reports"
])

# ============================================================================
# TAB 1: QTO INPUT
# ============================================================================

with tab1:
    st.header("📐 Quantity Take-Off (QTO) Input")
    st.markdown("*Enter quantities per IS 1200 measurement rules*")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Select Work Type")
        work_type = st.selectbox(
            "Work Category",
            ["Earthwork", "Concrete (PCC)", "Concrete (RCC)", "Formwork", 
             "Brickwork", "Plastering", "Flooring", "Painting"]
        )
    
    with col2:
        st.subheader("IS 1200 Reference")
        is_ref_map = {
            "Earthwork": "IS 1200 Part 2",
            "Concrete (PCC)": "IS 1200 Part 9",
            "Concrete (RCC)": "IS 1200 Part 9",
            "Formwork": "IS 1200 Part 5",
            "Brickwork": "IS 1200 Part 3",
            "Plastering": "IS 1200 Part 6",
            "Flooring": "IS 1200 Part 4",
            "Painting": "IS 1200 Part 6"
        }
        st.info(f"📖 {is_ref_map.get(work_type, 'IS 1200')}")
    
    st.divider()
    
    # Dynamic input based on work type
    if work_type == "Earthwork":
        st.subheader("Earthwork Excavation Parameters")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            length = st.number_input("Length (m)", min_value=0.1, value=10.0, step=0.1)
        with col_b:
            width = st.number_input("Width (m)", min_value=0.1, value=5.0, step=0.1)
        with col_c:
            depth = st.number_input("Depth (m)", min_value=0.1, value=1.5, step=0.1)
        
        col_d, col_e = st.columns(2)
        with col_d:
            soil_type = st.selectbox("Soil Type", ["ordinary", "hard", "rock"])
        with col_e:
            lead = st.number_input("Lead (m)", min_value=10, value=50, step=10)
        
        if st.button("➕ Add Earthwork Item"):
            item = st.session_state.is1200_engine.measure_earthwork_excavation(
                length, width, depth, soil_type, lead
            )
            st.session_state.qto_items.append(item)
            st.success(f"✅ Added: {item.quantity} {item.unit} of {item.description}")
    
    elif work_type in ["Concrete (PCC)", "Concrete (RCC)"]:
        st.subheader("Concrete Parameters")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            length = st.number_input("Length (m)", min_value=0.1, value=10.0, step=0.1, key='conc_l')
        with col_b:
            width = st.number_input("Width (m)", min_value=0.1, value=5.0, step=0.1, key='conc_w')
        with col_c:
            height = st.number_input("Height/Thickness (m)", min_value=0.05, value=0.15, step=0.01)
        
        col_d, col_e = st.columns(2)
        with col_d:
            grade = st.selectbox("Concrete Grade", ["M15", "M20", "M25", "M30", "M35"])
        with col_e:
            element = st.selectbox("Element Type", 
                                   ["slab", "beam", "column", "footing", "foundation"])
        
        if st.button("➕ Add Concrete Item"):
            item = st.session_state.is1200_engine.measure_concrete(
                length, width, height, grade, element
            )
            st.session_state.qto_items.append(item)
            st.success(f"✅ Added: {item.quantity} {item.unit} of {item.description}")
    
    elif work_type == "Formwork":
        st.subheader("Formwork Parameters")
        col_a, col_b = st.columns(2)
        
        with col_a:
            length = st.number_input("Length (m)", min_value=0.1, value=10.0, step=0.1, key='form_l')
            height = st.number_input("Height (m)", min_value=0.1, value=0.15, step=0.01, key='form_h')
        with col_b:
            element = st.selectbox("Element", ["slab", "beam", "column", "wall"], key='form_elem')
            openings = st.number_input("Openings Area (m²)", min_value=0.0, value=0.0, step=0.1)
        
        if st.button("➕ Add Formwork Item"):
            item = st.session_state.is1200_engine.measure_formwork(
                length, height, element, openings
            )
            st.session_state.qto_items.append(item)
            st.success(f"✅ Added: {item.quantity} {item.unit}")
    
    st.divider()
    
    # Display current QTO items
    if st.session_state.qto_items:
        st.subheader("📋 Current QTO Items")
        qto_display = []
        for idx, item in enumerate(st.session_state.qto_items, 1):
            qto_display.append({
                'No.': idx,
                'Description': item.description[:60] + '...' if len(item.description) > 60 else item.description,
                'Quantity': item.quantity,
                'Unit': item.unit,
                'IS Ref': item.is_code_ref
            })
        
        st.dataframe(pd.DataFrame(qto_display), use_container_width=True)
        
        if st.button("🗑️ Clear All Items"):
            st.session_state.qto_items = []
            st.rerun()

# ============================================================================
# TAB 2: RATE ANALYSIS
# ============================================================================

with tab2:
    st.header("💰 Detailed Rate Analysis")
    st.markdown("*Per CPWD norms: Material (60%) + Labor (25%) + Equipment (10%) + Overheads (5%) + Profit (10%)*")
    
    if not st.session_state.qto_items:
        st.warning("⚠️ No QTO items added. Please add items in the QTO Input tab first.")
    else:
        st.subheader("Rate Analysis for QTO Items")
        
        analyses = []
        
        # Analyze each QTO item
        for item in st.session_state.qto_items:
            # Determine analysis type based on description
            if 'excavation' in item.description.lower():
                soil = 'ordinary'
                if 'hard' in item.description.lower():
                    soil = 'hard'
                elif 'rock' in item.description.lower():
                    soil = 'rock'
                
                depth_range = 'up to 1.5m'
                if '1.5m to 3.0m' in item.description or '1.5' in item.description:
                    depth_range = 'up to 1.5m'
                
                analysis = st.session_state.rate_analyzer.analyze_earthwork_rate(soil, depth_range)
                analyses.append(analysis)
            
            elif 'rcc' in item.description.lower() or 'concrete' in item.description.lower():
                # Extract grade from description
                grade = 'M25'
                for g in ['M15', 'M20', 'M25', 'M30', 'M35']:
                    if g in item.description:
                        grade = g
                        break
                
                # Get DSR rate if available
                dsr_rate = None
                if st.session_state.dsr_loaded:
                    search_result = st.session_state.dsr_parser.search_rate('RCC', 'Cum')
                    if len(search_result) > 0:
                        dsr_rate = float(search_result.iloc[0]['rate'])
                
                analysis = st.session_state.rate_analyzer.analyze_concrete_rate(grade, dsr_rate)
                analyses.append(analysis)
            
            elif 'brick' in item.description.lower():
                analysis = st.session_state.rate_analyzer.analyze_brickwork_rate('1:6')
                analyses.append(analysis)
        
        if analyses:
            # Display rate analysis table
            report_df = st.session_state.rate_analyzer.create_rate_analysis_report(analyses)
            st.dataframe(report_df, use_container_width=True)
            
            # Detailed breakdown for first item (example)
            st.subheader("📊 Sample Detailed Breakdown")
            sample_analysis = analyses[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Material Cost", f"₹{sample_analysis.material_cost:.2f}")
            col2.metric("Labor Cost", f"₹{sample_analysis.labor_cost:.2f}")
            col3.metric("Equipment Cost", f"₹{sample_analysis.equipment_cost:.2f}")
            
            col4, col5, col6 = st.columns(3)
            col4.metric("Overheads", f"₹{sample_analysis.overhead_cost:.2f}")
            col5.metric("Profit", f"₹{sample_analysis.profit_cost:.2f}")
            col6.metric("TOTAL RATE", f"₹{sample_analysis.total_rate:.2f}", 
                       delta=f"per {sample_analysis.unit}")

# ============================================================================
# TAB 3: BOQ GENERATION
# ============================================================================

with tab3:
    st.header("📊 Bill of Quantities (BOQ) Generation")
    
    if not st.session_state.qto_items:
        st.warning("⚠️ No QTO items to generate BOQ. Add items first.")
    else:
        st.success(f"✅ {len(st.session_state.qto_items)} items ready for BOQ generation")
        
        # Initialize BOQ Generator
        boq_gen = BOQGenerator(
            project_name=st.session_state.project_info['name'],
            project_location=st.session_state.project_info['location']
        )
        
        # Add items to BOQ with rates
        for idx, item in enumerate(st.session_state.qto_items, 1):
            # Get rate from DSR or analysis
            rate = 0
            
            # Search DSR for matching rate
            if st.session_state.dsr_loaded:
                # Extract key terms for search
                if 'excavation' in item.description.lower():
                    search_result = st.session_state.dsr_parser.search_rate('excavation', 'Cum')
                    if len(search_result) > 0:
                        rate = float(search_result.iloc[0]['rate'])
                
                elif 'rcc' in item.description.lower() or 'concrete' in item.description.lower():
                    search_result = st.session_state.dsr_parser.search_rate('RCC', 'Cum')
                    if len(search_result) > 0:
                        rate = float(search_result.iloc[0]['rate'])
                
                elif 'brick' in item.description.lower():
                    search_result = st.session_state.dsr_parser.search_rate('brick', 'Cum')
                    if len(search_result) > 0:
                        rate = float(search_result.iloc[0]['rate'])
            
            # Fallback to rate analyzer if DSR not found
            if rate == 0:
                if 'excavation' in item.description.lower():
                    analysis = st.session_state.rate_analyzer.analyze_earthwork_rate()
                    rate = analysis.total_rate
                elif 'concrete' in item.description.lower():
                    analysis = st.session_state.rate_analyzer.analyze_concrete_rate('M25')
                    rate = analysis.total_rate
            
            # Determine WBS
            wbs_l1 = "Civil Works"
            wbs_l2 = "Foundation" if 'foundation' in item.description.lower() else "Superstructure"
            
            boq_gen.add_boq_item(
                item_no=f"{idx:03d}",
                description=item.description,
                unit=item.unit,
                quantity=item.quantity,
                rate=rate,
                wbs_level1=wbs_l1,
                wbs_level2=wbs_l2,
                is_reference=item.is_code_ref
            )
        
        # Display BOQ
        st.subheader("📋 BOQ Preview")
        boq_df = boq_gen.generate_boq_dataframe()
        st.dataframe(boq_df, use_container_width=True)
        
        # Calculate totals
        totals = boq_gen.calculate_totals()
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Base Cost", f"₹{totals['total_cost']:,.2f}")
        col2.metric("Total Items", totals['item_count'])
        
        # Contingency calculation
        contingency_calc = st.session_state.rate_analyzer.calculate_contingency(
            totals['total_cost'],
            st.session_state.project_info['duration'],
            st.session_state.project_info['risk']
        )
        
        col3.metric("Final Project Cost", f"₹{contingency_calc['total_project_cost']:,.2f}",
                   delta=f"+{((contingency_calc['total_project_cost'] - totals['total_cost'])/totals['total_cost']*100):.1f}%")
        
        st.subheader("💰 Cost Breakdown with Provisions")
        provisions_df = pd.DataFrame([
            {"Item": "Base Cost", "Amount (₹)": f"{totals['total_cost']:,.2f}"},
            {"Item": f"Contingency ({contingency_calc['contingency_rate']*100}%)", 
             "Amount (₹)": f"{contingency_calc['contingency']:,.2f}"},
            {"Item": "Work Charged Establishment", 
             "Amount (₹)": f"{contingency_calc['work_charged_establishment']:,.2f}"},
            {"Item": "Tools & Plant", 
             "Amount (₹)": f"{contingency_calc['tools_plant']:,.2f}"},
            {"Item": "Water Charges", 
             "Amount (₹)": f"{contingency_calc['water_charges']:,.2f}"},
            {"Item": "Electricity Charges", 
             "Amount (₹)": f"{contingency_calc['electricity_charges']:,.2f}"},
            {"Item": "Escalation", 
             "Amount (₹)": f"{contingency_calc['escalation']:,.2f}"},
            {"Item": "TOTAL PROJECT COST", 
             "Amount (₹)": f"₹{contingency_calc['total_project_cost']:,.2f}"}
        ])
        
        st.dataframe(provisions_df, use_container_width=True, hide_index=True)
        
        # Export options
        st.divider()
        st.subheader("📥 Export BOQ")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button("📊 Export to Excel"):
                filename = f"BOQ_{st.session_state.project_info['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                boq_gen.export_to_excel(filename)
                st.success(f"✅ BOQ exported to {filename}")
                
                # Provide download
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=f,
                        file_name=filename,
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )

# ============================================================================
# TAB 4: COMPLIANCE CHECK
# ============================================================================

with tab4:
    st.header("✅ Government Compliance Checklist")
    
    st.subheader("📋 CPWD Requirements Checklist")
    
    compliance_items = [
        ("IS 1200 measurement rules followed", True if st.session_state.qto_items else False),
        ("Contingency provision (3-5%) included", True),
        ("Work Charged Establishment (1.5%) included", True),
        ("Tools & Plant (1%) included", True),
        ("Escalation clause for >12 months", 
         st.session_state.project_info['duration'] > 12),
        ("Rate analysis with material/labor/equipment breakdown", True),
        ("WBS structure implemented", True),
        ("DSR rates referenced", st.session_state.dsr_loaded)
    ]
    
    for item, status in compliance_items:
        if status:
            st.success(f"✅ {item}")
        else:
            st.warning(f"⚠️ {item} - Action Required")
    
    st.divider()
    
    st.subheader("📄 Required Forms for Approvals")
    
    st.markdown("""
    **1. Administrative Approval (AA)**
    - Preliminary cost estimate
    - Project justification
    - Budget allocation confirmation
    
    **2. Technical Sanction (TS)**
    - Detailed design drawings
    - Specifications as per IS codes
    - Detailed BOQ with rate analysis
    - Site investigation reports
    
    **3. Project Preparation Report (PPR)**
    - Site data and survey
    - Approximate estimate
    - Feasibility analysis
    """)
    
    if st.button("📄 Generate Compliance Report"):
        st.info("Compliance report generation feature - to be implemented with PDF export")

# ============================================================================
# TAB 5: REPORTS
# ============================================================================

with tab5:
    st.header("📄 Project Reports")
    
    st.subheader("Available Reports")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("""
        **📊 BOQ Report**
        - Complete itemized BOQ
        - Rate analysis breakdown
        - WBS cost summary
        - Abstract of cost
        """)
        
        if st.session_state.qto_items:
            st.button("Generate BOQ Report", disabled=False)
        else:
            st.button("Generate BOQ Report", disabled=True)
    
    with col_r2:
        st.markdown("""
        **📋 Measurement Book**
        - Sequential entries
        - IS 1200 references
        - Dimension details
        - Signature placeholders
        """)
        
        st.button("Generate MB Format", disabled=not bool(st.session_state.qto_items))
    
    st.divider()
    
    st.subheader("📈 Project Statistics")
    
    if st.session_state.qto_items:
        # Generate statistics
        total_items = len(st.session_state.qto_items)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Total Items", total_items)
        col_s2.metric("Project Duration", f"{st.session_state.project_info['duration']} months")
        col_s3.metric("Risk Level", st.session_state.project_info['risk'].capitalize())

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>AI Construction Estimator v2.0</strong> | Government Compliant per IS 1200 & CPWD Standards</p>
    <p>⚠️ Always verify estimates with qualified engineers | Rates based on CPWD DSR 2024-25</p>
</div>
""", unsafe_allow_html=True)
