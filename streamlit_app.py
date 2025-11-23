import streamlit as st
from is1200_rules import IS1200Engine  # Your measurement module

# Initialize the IS1200 measurement engine
engine = IS1200Engine()

# Initialize session state list to store QTO items persistently
if 'qto_items' not in st.session_state:
    st.session_state['qto_items'] = []

# Step 1: Create Input Fields for Quantity Dimensions
st.header("Quantity Takeoff Input")

length = st.number_input("Length (meters):", min_value=0.1, value=10.0)
width = st.number_input("Width (meters):", min_value=0.1, value=5.0)
thickness = st.number_input("Thickness (meters):", min_value=0.05, value=0.15)
grade = st.selectbox("Concrete Grade:", ["M15", "M20", "M25", "M30"])

# Step 2: Button to Calculate and Add Quantity Item
if st.button("Calculate Concrete Volume and Add to QTO"):
    try:
        # Perform measurement using your IS1200 engine method
        item = engine.measure_concrete(length, width, thickness, grade=grade, element_type='slab')
        
        # Add the measurement item to session state list
        st.session_state.qto_items.append(item)
        
        # Give user feedback on success
        st.success(f"Added: {item.description} - {item.quantity} {item.unit} (Ref: {item.is_code_ref})")
    except Exception as e:
        # Show error message if calculation fails
        st.error(f"Error calculating quantity: {e}")

# Step 3: Display All Added Quantity Items
if st.session_state.qto_items:
    st.subheader("Current Quantity Takeoff Items")
    for idx, itm in enumerate(st.session_state.qto_items, start=1):
        st.write(f"{idx}. {itm.description} - {itm.quantity} {itm.unit} (Ref: {itm.is_code_ref})")

# Step 4: Optional Button to Clear All Entries
if st.button("Clear All QTO Items"):
    st.session_state.qto_items.clear()
    st.info("All quantity takeoff items have been cleared.")
