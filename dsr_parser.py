from dsr_parser import DSRParser

if st.sidebar.button("Parse DSR PDFs"):
    if dsr_vol1 or dsr_vol2:
        parser = DSRParser()
        if dsr_vol1:
            with open("/tmp/dsr_vol1.pdf", "wb") as f:
                f.write(dsr_vol1.getbuffer())
            parser.dsr_vol1_path = "/tmp/dsr_vol1.pdf"
        if dsr_vol2:
            with open("/tmp/dsr_vol2.pdf", "wb") as f:
                f.write(dsr_vol2.getbuffer())
            parser.dsr_vol2_path = "/tmp/dsr_vol2.pdf"
        rates_df = parser.load_all_rates()
        st.session_state['rates_df'] = rates_df
        st.success(f"Loaded {len(rates_df)} rates from DSR files.")
    else:
        st.warning("Please upload at least one DSR PDF.")
