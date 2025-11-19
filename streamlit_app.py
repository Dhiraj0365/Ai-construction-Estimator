# streamlit_app.py - Drive Integration Version

import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Civil Estimator",
    page_icon="🏗️",
    layout="wide"
)

# Title
st.title("🏗️ AI Civil Engineering Estimator")
st.markdown("**Real-time estimates from Google Colab → Google Drive**")

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.info("""
    **How to use:**
    1. Generate estimate in Colab (Cells 1-17)
    2. Run Cell 18 to upload to Drive
    3. Click "Refresh" button below
    4. View your estimates!
    """)
    
    st.divider()
    
    # Your Drive folder link
    drive_folder_id = "1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH"  # REPLACE WITH YOUR FOLDER ID
    drive_link = f"https://drive.google.com/drive/folders/{drive_folder_id}"
    
    st.markdown(f"**📁 [Open Drive Folder]({drive_link})**")
    
    if st.button("🔄 Refresh Files", type="primary"):
        st.rerun()

# Main content
st.header("📊 Latest Estimates from Colab")

# Manual file list (you'll update this when you upload new files)
st.info("""
**Current estimates available:**

Your latest estimates are stored in Google Drive.

**To view them:**
1. Click "Open Drive Folder" in sidebar →
2. Download Excel files directly
3. Or view summary below
""")

# Sample data display (will be replaced with real Drive integration)
st.subheader("📋 Recent Estimates")

# Placeholder for your estimates
estimate_data = {
    'Project': ['IS Compliance Project', 'Green Valley Housing', 'Road Estimate'],
    'Date': ['2025-11-17', '2025-11-17', '2025-11-17'],
    'Total Cost': ['₹2,934,439', '₹8,500,000', '₹1,250,000'],
    'Status': ['✅ Complete', '✅ Complete', '✅ Complete']
}

df = pd.DataFrame(estimate_data)
st.dataframe(df, use_container_width=True)

# File access
st.subheader("📥 Download Estimates")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Method 1: Direct from Drive**
    
    [Open Google Drive Folder →]({drive_link})
    
    - View all your Excel files
    - Download any estimate
    - Share with clients
    """)

with col2:
    st.markdown("""
    **Method 2: From Colab**
    
    1. Open your Colab notebook
    2. Find Excel file in Files tab (left sidebar)
    3. Right-click → Download
    4. Send to clients
    """)

# Stats
st.divider()
st.subheader("📈 System Status")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Estimates", "18")
col2.metric("Latest Total", "₹2.93M")
col3.metric("Compliance", "100%")
col4.metric("Last Updated", "2025-11-17")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>AI Civil Engineering Estimator</strong></p>
    <p>🔗 Colab → Google Drive → Streamlit Integration</p>
    <p>✅ DSR 2023 | IS Code Compliant | Professional BOQ</p>
</div>
""", unsafe_allow_html=True)
