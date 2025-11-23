import streamlit as st
from is1200_rules import IS1200Engine

engine = IS1200Engine()

st.header("Quantity Takeoff Input")

length = st.number_input("Length (m)", min_value=0.1, value=10.0)
width = st.number_input("Width (m)", min_value=0.1, value=5.0)
thickness = st.number_input("Thickness (m)", min_value=0.05, value=0.15)
grade = st.selectbox("Concrete Grade", ["M15", "M20", "M25", "M30"])

if st.button("Calculate Concrete Volume"):
    item = engine.measure_concrete(length, width, thickness, grade=grade, element_type='slab')
    st.success(f"Calculated volume: {item.quantity} {item.unit} ({item.description})")
    
    if 'qto_items' not in st.session_state:
        st.session_state['qto_items'] = []
    
    st.session_state['qto_items'].append(item)

if 'qto_items' in st.session_state and st.session_state['qto_items']:
    st.subheader("Current QTO Items")
    for i, itm in enumerate(st.session_state['qto_items'], 1):
        st.write(f"{i}. {itm.description} - {itm.quantity} {itm.unit} [{itm.is_code_ref}]")
