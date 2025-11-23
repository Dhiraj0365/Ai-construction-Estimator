from rate_analyzer import RateAnalyzer

if 'qto_items' in st.session_state and 'rates_df' in st.session_state:
    analyzer = RateAnalyzer()
    dsr_rates = st.session_state['rates_df']

    st.header("Rate Analysis")

    for item in st.session_state['qto_items']:
        # Naive keyword search to find base rate for item in DSR
        keyword = "RCC" if "concrete" in item.description.lower() else "earthwork"
        matched_rates = dsr_rates[dsr_rates['description'].str.contains(keyword, case=False)]

        if not matched_rates.empty:
            base_rate = float(matched_rates.iloc[0]['rate'])
        else:
            base_rate = None  # fallback in analysis function

        if "concrete" in item.description.lower():
            analysis = analyzer.analyze_concrete_rate('M25', base_rate)
        else:
            analysis = analyzer.analyze_earthwork_rate()

        total_cost = analysis.total_rate * item.quantity

        st.write(f"**{item.description}:**")
        st.write(f"- Quantity: {item.quantity} {item.unit}")
        st.write(f"- Rate: ₹{analysis.total_rate:.2f} per {item.unit}")
        st.write(f"- Estimated Cost: ₹{total_cost:.2f}")
        st.write(f"- Breakdown:")
        st.write(f"   - Material: ₹{analysis.material_cost:.2f}")
        st.write(f"   - Labor: ₹{analysis.labor_cost:.2f}")
        st.write(f"   - Equipment: ₹{analysis.equipment_cost:.2f}")
        st.write(f"   - Overheads: ₹{analysis.overhead_cost:.2f}")
        st.write(f"   - Profit: ₹{analysis.profit_cost:.2f}")
