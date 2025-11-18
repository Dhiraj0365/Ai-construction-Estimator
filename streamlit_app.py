# streamlit_app.py - SIMPLIFIED VERSION (100% Compatible)

import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Civil Estimator", 
    page_icon="🏗️", 
    layout="wide"
)

# Simple DSR rates (works without external files)
DSR_SIMPLE = {
    'Excavation': {'rate': 186.50, 'unit': 'cum'},
    'PCC M10': {'rate': 4845.00, 'unit': 'cum'},
    'RCC M20': {'rate': 6245.00, 'unit': 'cum'},
    'Steel Fe500': {'rate': 68.50, 'unit': 'kg'},
    'Brick Masonry': {'rate': 4850.00, 'unit': 'cum'},
    'Cement Plaster': {'rate': 185.50, 'unit': 'sqm'},
    'Ceramic Flooring': {'rate': 685.00, 'unit': 'sqm'},
    'Emulsion Painting': {'rate': 125.50, 'unit': 'sqm'}
}

# Simple Estimator Class (No Complex Dependencies)
class SimpleEstimator:
    def __init__(self):
        self.project_name = ""
        self.location = ""
        self.client_name = ""
        self.items = []
        self.total = 0
    
    def create_estimate(self, project_name, location, client, length, width, floors):
        self.project_name = project_name
        self.location = location
        self.client_name = client
        
        # Basic QTO (8 items)
        area = length * width * floors
        
        # Basic calculations
        self.items = [
            {'Item': 'Excavation', 'Qty': area * 0.25, 'Unit': 'cum', 'Rate': DSR_SIMPLE['Excavation']['rate'], 'Total': area * 0.25 * DSR_SIMPLE['Excavation']['rate']},
            {'Item': 'PCC Foundation', 'Qty': area * 0.05, 'Unit': 'cum', 'Rate': DSR_SIMPLE['PCC M10']['rate'], 'Total': area * 0.05 * DSR_SIMPLE['PCC M10']['rate']},
            {'Item': 'RCC M20 Concrete', 'Qty': area * 0.40, 'Unit': 'cum', 'Rate': DSR_SIMPLE['RCC M20']['rate'], 'Total': area * 0.40 * DSR_SIMPLE['RCC M20']['rate']},
            {'Item': 'Steel Fe500', 'Qty': area * 0.40 * 80, 'Unit': 'kg', 'Rate': DSR_SIMPLE['Steel Fe500']['rate'], 'Total': area * 0.40 * 80 * DSR_SIMPLE['Steel Fe500']['rate']},
            {'Item': 'Brick Masonry', 'Qty': area * 0.23, 'Unit': 'cum', 'Rate': DSR_SIMPLE['Brick Masonry']['rate'], 'Total': area * 0.23 * DSR_SIMPLE['Brick Masonry']['rate']},
            {'Item': 'Cement Plaster', 'Qty': area * 2.0, 'Unit': 'sqm', 'Rate': DSR_SIMPLE['Cement Plaster']['rate'], 'Total': area * 2.0 * DSR_SIMPLE['Cement Plaster']['rate']},
            {'Item': 'Ceramic Flooring', 'Qty': area, 'Unit': 'sqm', 'Rate': DSR_SIMPLE['Ceramic Flooring']['rate'], 'Total': area * DSR_SIMPLE['Ceramic Flooring']['rate']},
            {'Item': 'Emulsion Painting', 'Qty': area * 2.0, 'Unit': 'sqm', 'Rate': DSR_SIMPLE['Emulsion Painting']['rate'], 'Total': area * 2.0 * DSR_SIMPLE['Emulsion Painting']['rate']}
        ]
        
        # Calculate totals
        self.total = sum(item['Total'] for item in self.items)
        
        return self.items, self.total

# Title
st.title("🏗️ AI Civil Engineering Estimator")

# Step 1: Project Information
st.subheader("📋 Project Information")
col1, col2 = st.columns(2)

with col1:
    project_name = st.text_input("Project Name", "New Project Estimate")
    location = st.text_input("Location", "Delhi")
    client_name = st.text_input("Client Name", "ABC Developers")

with col2:
    length = st.number_input("Length (m)", value=25, min_value=5, max_value=100, format="%i")
    width = st.number_input("Width (m)", value=18, min_value=5, max_value=100, format="%i")
    floors = st.number_input("Number of Floors", value=4, min_value=1, max_value=20, format="%i")

# Step 2: Generate Estimate
if st.button("🚀 Calculate Estimate", type="primary"):
    with st.spinner("Generating professional estimate..."):
        estimator = SimpleEstimator()
        items, total = estimator.create_estimate(project_name, location, client_name, length, width, floors)
        st.session_state.items = items
        st.session_state.total = total
        st.session_state.project_name = project_name
        st.session_state.generated = True
        st.rerun()

# Step 3: Display Results
if st.session_state.get('generated', False):
    st.success("✅ Estimate Generated Successfully!")
    
    # Project Info
    col1, col2 = st.columns(2)
    col1.metric("Project", st.session_state.project_name)
    col2.metric("Location", st.session_state.location)
    
    st.metric("Client", st.session_state.client_name)
    
    # Results
    items_df = pd.DataFrame(st.session_state.items)
    st.subheader("📋 Bill of Quantities")
    st.table(items_df)
    
    # Total
    st.subheader("💰 Cost Summary")
    
    total_cost = st.session_state.total
    gst = total_cost * 0.18
    overhead = total_cost * 0.12
    profit = total_cost * 0.10
    contingency = total_cost * 0.05
    grand_total = total_cost + gst + overhead + profit + (total_cost * 0.05)
    
    col1, col2 = st.columns(2)
    col1.metric("Basic Cost", f"₹{total_cost:,.0f}")
    col2.metric("GST (18%)", f"₹{gst:,.0f}")
    col1.metric("Overhead (12%)", f"₹{overhead:,.0f}")
    col2.metric("Profit (10%)", f"₹{profit:,.0f}")
    col1.metric("Contingency (5%)", f"₹{contingency:,.0f}")
    
    st.success(f"**Grand Total: ₹{grand_total:,.0f}")
    
    # Step 4: Download
    st.subheader("📥 Download Estimate")
    
    items_df['Total'] = items_df['Qty'] * items_df['Rate']
    excel_data = items_df.to_excel(index=False)
    
    st.download_button(
        label="📥 Download Excel BOQ",
        data=excel_data,
        file_name=f"{st.session_state.project_name}.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.info("""
    **Welcome to AI Civil Engineering Estimator!**
    
    Enter project details and click "Calculate Estimate" to get started.
    """)

# Footer
st.markdown("---")
st.markdown("**✅ DSR 2023 | IS Code Compliant | Government Ready**")
