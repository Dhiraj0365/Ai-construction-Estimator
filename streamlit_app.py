# streamlit_app.py - FIXED VERSION (NO COLAB DEPENDENCIES)

import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="AI Civil Engineering Estimator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #2e7d32;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .stMetric > label {
        color: white !important;
        font-size: 16px;
    }
    .stMetric > div > div {
        color: white !important;
        font-size: 24px;
    }
    .file-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Google Drive Configuration
FOLDER_ID = "1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH"  # YOUR FOLDER

# Setup Google Drive API
@st.cache_resource
def get_drive_service():
    """Connect to Google Drive API"""
    try:
        # Use service account credentials (set up in Streamlit secrets)
        from streamlit import secrets
        
        if "drive_credentials" in secrets:
            credentials = Credentials.from_service_account_info(
                secrets["drive_credentials"],
                scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
        else:
            # Fallback: use simple API key (less secure but works)
            st.warning("⚠️ Using API key - limited access")
            return None
        
        service = build('drive', 'v3', credentials=credentials)
        return service
        
    except Exception as e:
        st.error(f"Drive connection failed: {e}")
        st.info("""
        **To fix this:**
        1. Go to Google Cloud Console
        2. Enable Drive API for your project
        3. Create service account
        4. Add credentials to Streamlit secrets
        
        **For now, you can still view files manually:**
        [Open Drive Folder](https://drive.google.com/drive/folders/1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH)
        """)
        return None

# Get files from your Google Drive folder
@st.cache_data(ttl=300)  # Refresh every 5 minutes
def get_estimate_files():
    """Fetch Excel files from your Google Drive folder"""
    service = get_drive_service()
    
    if not service:
        # Fallback: return static info
        return [
            {
                "id": "manual",
                "name": "Manual Access",
                "modifiedTime": datetime.now().isoformat(),
                "type": "manual",
                "url": "https://drive.google.com/drive/folders/1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH"
            }
        ]
    
    try:
        # Query your specific folder for Excel files
        query = f"'{FOLDER_ID}' in parents and trashed=false and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or name contains 'estimate')"
        
        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, size, webViewLink)",
            orderBy="modifiedTime desc",
            pageSize=20
        ).execute()
        
        files = results.get('files', [])
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.get('modifiedTime', ''), reverse=True)
        
        st.success(f"✅ Connected to Google Drive! Found {len(files)} file(s)")
        return files
        
    except Exception as e:
        st.error(f"Error fetching files: {e}")
        st.info("**Manual Access:** [Open Drive Folder](https://drive.google.com/drive/folders/1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH)")
        return []

# Read Excel file from Google Drive
@st.cache_data(ttl=600)
def read_excel_file(file_id, file_name):
    """Download and read Excel file"""
    service = get_drive_service()
    
    if not service:
        st.warning("Cannot read file without Drive connection")
        return None
    
    try:
        # Download file
        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()
        
        # Read with pandas
        df = pd.read_excel(io.BytesIO(file_content))
        return df, len(df)
        
    except Exception as e:
        st.error(f"Error reading {file_name}: {e}")
        return None, 0

# Main App
def main():
    st.markdown('<h1 class="main-header">🏗️ AI Civil Engineering Estimator</h1>', unsafe_allow_html=True)
    st.markdown("**DSR 2023 Compliant | IS Code Ready | Real-time Estimates**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Files", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.header("📁 Your Drive Folder")
        st.info(f"**ID:** `{FOLDER_ID}`")
        st.markdown(f"[🔗 Open Folder](https://drive.google.com/drive/folders/{FOLDER_ID})")
        
        # Connection status
        service = get_drive_service()
        if service:
            st.success("✅ Google Drive Connected")
        else:
            st.warning("⚠️ Drive API not configured")
    
    # Main content
    st.header("📊 Latest Estimates from Colab")
    
    # Get files
    files = get_estimate_files()
    
    if files:
        # Show file count
        st.success(f"**✅ Found {len(files)} estimate file(s)**")
        
        if len(files) > 0:
            # File tabs
            tab_names = []
            for file in files[:5]:  # Show top 5
                name = file.get('name', 'Unknown')[:30]
                modified = file.get('modifiedTime', '')[:10]
                tab_names.append(f"{name} ({modified})")
            
            # Create tabs
            if len(tab_names) > 1:
                tabs = st.tabs(tab_names)
                
                for idx, (tab, file) in enumerate(zip(tabs, files[:5])):
                    with tab:
                        display_file_content(file)
            else:
                # Single file display
                st.subheader(f"📄 {files[0].get('name', 'Estimate')}")
                display_file_content(files[0])
        else:
            st.info("📝 **Upload Instructions:**\nRun Cell 18 in Colab to upload estimates")
            
    else:
        st.warning("⏳ No estimates found")
        st.info("""
        **🚀 Quick Start:**
        1. **Open Colab:** https://colab.research.google.com/drive/1C91g0Nxiel0doDlKqLaWjOi8joqqNVtN
        2. **Run Cells 1-17:** Generate your estimate
        3. **Run Cell 18:** Upload to Drive (30 seconds)
        4. **Refresh this page:** See files appear automatically!
        
        **Your Drive folder:** https://drive.google.com/drive/folders/1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        <p>🔗 Connected to Google Drive Folder: 1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH</p>
        <p>📱 Real-time estimates | 🏗️ DSR 2023 Compliant | ✅ IS Code Ready</p>
    </div>
    """, unsafe_allow_html=True)

def display_file_content(file):
    """Display the content of a single estimate file"""
    file_id = file.get('id')
    file_name = file.get('name', 'Estimate')
    modified_time = file.get('modifiedTime', '')
    
    # File information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 File", file_name[:25])
    
    with col2:
        if file_id != "manual":
            st.markdown(f"[🔗 Open in Drive](https://drive.google.com/file/d/{file_id}/view)")
        else:
            st.info("Manual access")
    
    with col3:
        st.metric("📅 Updated", modified_time[:10] if modified_time else "Unknown")
    
    st.divider()
    
    # Read file content
    df, row_count = read_excel_file(file_id, file_name)
    
    if df is not None and row_count > 0:
        st.subheader("📊 Estimate Details")
        
        # Show data
        st.dataframe(df, use_container_width=True)
        
        # Summary metrics
        if 'Amount' in df.columns:
            total_amount = df['Amount'].sum()
            st.metric("💰 Total Amount", f"₹{total_amount:,.2f}")
        
        if 'Quantity' in df.columns and 'Unit' in df.columns:
            total_items = len(df)
            st.metric("📋 Total Items", total_items)
        
        st.divider()
        
        # Download button
        try:
            # Recreate Excel for download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Estimate', index=False)
            
            excel_buffer.seek(0)
            
            st.download_button(
                label=f"📥 Download {file_name}",
                data=excel_buffer,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_{file.get('id', idx)}"
            )
            
            st.success("✅ File ready for download!")
            
        except Exception as e:
            st.error(f"Download error: {e}")
            st.info(f"💡 Direct download: https://drive.google.com/file/d/{file_id}/view")
    
    else:
        if file_id == "manual":
            st.info("""
            **🚀 Getting Started:**
            1. Open your Colab notebook
            2. Run Cells 1-17 to generate estimate
            3. Run Cell 18 to upload to Drive
            4. Refresh this page to see files!
            
            **📁 Your Drive Folder:** https://drive.google.com/drive/folders/1lGa6PaLktE7Tl-C-yDDDUiRx-1lOgLHH
            """)
        else:
            st.warning("⚠️ Could not read file content")
            st.info(f"💡 View directly: https://drive.google.com/file/d/{file_id}/view")

if __name__ == "__main__":
    main()

