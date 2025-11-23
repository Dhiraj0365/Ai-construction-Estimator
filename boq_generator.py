from boq_generator import BOQGenerator
import pandas as pd
import streamlit as st

st.header("Bill of Quantities (BOQ) Generation")

# Check for QTO and Rate Analysis data
if 'qto_items' in st.session_state and 'rates_df' in st.session_state:
    boq = BOQGenerator(project_name="My Project", project_location="Delhi")

    for idx, item in enumerate(st.session_state['qto_items'], start=1):
        # For simplicity, use dummy rate or match with DSR rates here
        rate = 5000  # Placeholder or fetch from rates_df
        
        boq.add_boq_item(
            item_no=f"{idx:03d}",
            description=item.description,
            unit=item.unit,
            quantity=item.quantity,
            rate=rate,
            wbs_level1="Civil Works",
            wbs_level2="Foundation",
            is_reference=item.is_code_ref
        )
        
    df_boq = boq.generate_boq_dataframe()
    st.write(df_boq)

    if st.button("Export BOQ to Excel"):
        export_filename = f"BOQ_{st.session_state['project_name'].replace(' ', '_')}.xlsx"
        boq.export_to_excel(export_filename)
        st.success(f"BOQ exported to {export_filename}")
        with open(export_filename, "rb") as file:
            st.download_button("Download Excel", file.read(), file_name=export_filename)
else:
    st.warning("Please complete Quantity Takeoff and Rate Analysis first.")
