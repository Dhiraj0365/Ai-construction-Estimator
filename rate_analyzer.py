from rate_analyzer import RateAnalyzer

st.header("Rate Analysis")

if 'qto_items' in st.session_state and 'rates_df' in st.session_state:
    rate_calc = RateAnalyzer()
    total_cost = 0
    for item in st.session_state['qto_items']:
        # Search rate (simple keyword search example)
        base_rate_row = st.session_state['rates_df'][st.session_state['rates_df']['description'].str.contains(item.description.split()[0], case=False)]
        base_rate = float(base_rate_row.iloc[0]['rate']) if not base_rate_row.empty else 0
        
        analysis = rate_calc.analyze_concrete_rate('M25', base_rate)
        item_cost = analysis.total_rate * item.quantity
        
        st.write(f"{item.description}: Quantity={item.quantity} {item.unit} | Unit Rate=₹{analysis.total_rate:.2f} | Item Cost=₹{item_cost:.2f}")
        total_cost += item_cost
    
    contingency_pct = st.slider("Select Contingency Percentage", 3, 5, 4)
    contingency_amount = total_cost * (contingency_pct / 100)
    grand_total = total_cost + contingency_amount
    
    st.write(f"Total Cost (Before Contingency): ₹{total_cost:.2f}")
    st.write(f"Contingency (@{contingency_pct}%): ₹{contingency_amount:.2f}")
    st.write(f"Grand Total Estimate: ₹{grand_total:.2f}")
else:
    st.warning("Upload DSR and add QTO items first.")
