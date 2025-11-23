import streamlit as st

with st.sidebar:
    st.title("Project Setup and File Upload")

    dsr_vol1 = st.file_uploader("Upload DSR Volume 1 (Civil Works) PDF", type=["pdf"])
    dsr_vol2 = st.file_uploader("Upload DSR Volume 2 (Civil Works) PDF", type=["pdf"])
    drawing_pdf = st.file_uploader("Upload Project Drawing (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

    project_name = st.text_input("Project Name", "Sample Project")
    location = st.text_input("Location", "Delhi")
    project_duration = st.number_input("Project Duration (months)", min_value=1, value=12)
    risk_level = st.selectbox("Project Risk Level", ["Low", "Medium", "High"])
