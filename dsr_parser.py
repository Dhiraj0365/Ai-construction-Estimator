import pandas as pd
import streamlit as st


class DSRParser:
    """
    DSR (Delhi Schedule of Rates) parser for construction rates.
    Currently provides sample rates. Real PDF parsing can be added later.
    """

    def __init__(self):
        # Sample DSR rates (2023 approximate values)
        self.rates_df = pd.DataFrame([
            {"code": "EW-01", "description": "Earthwork excavation ordinary soil", "unit": "Cum", "rate": 250.0},
            {"code": "PCC-01", "description": "PCC 1:4:8", "unit": "Cum", "rate": 4500.0},
            {"code": "RCC-01", "description": "RCC M25 concrete", "unit": "Cum", "rate": 7500.0},
            {"code": "BM-01", "description": "Brick masonry 1st class", "unit": "Cum", "rate": 5500.0},
            {"code": "PL-01", "description": "12mm cement plaster", "unit": "Sqm", "rate": 250.0},
            {"code": "FL-01", "description": "Vitrified tiles flooring", "unit": "Sqm", "rate": 800.0},
        ])

    def get_rates(self) -> pd.DataFrame:
        """Get all available rates."""
        return self.rates_df.copy()

    def find_rate_by_keyword(self, keyword: str) -> float | None:
        """Find rate by keyword search."""
        match = self.rates_df[
            self.rates_df["description"].str.contains(keyword, case=False, na=False)
        ]
        return float(match.iloc[0]["rate"]) if not match.empty else None

    def parse_dsr(self, uploaded_file):
        """Handle uploaded DSR file (placeholder - shows sample rates)."""
        st.info("📄 DSR uploaded! Showing sample rates (PDF parsing coming soon).")
        return self.get_rates()
