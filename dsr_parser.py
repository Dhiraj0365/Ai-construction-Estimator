import pandas as pd
from pathlib import Path
import streamlit as st


class DSRParser:
    """
    DSR (Schedule of Rates) helper for the AI Construction Estimator.

    - Loads items from a CSV file (dsr_items.csv by default)
    - Allows keyword + unit-based search
    - Provides rates by DSR code
    """

    def __init__(self, csv_path: str = "dsr_items.csv"):
        self.csv_path = csv_path
        self._df: pd.DataFrame | None = None

    # -----------------------------
    # Internal loader
    # -----------------------------
    def _load_dsr(self) -> pd.DataFrame:
        """
        Load DSR data from CSV into a DataFrame.

        Expected columns in dsr_items.csv:
        - code        : DSR item number (e.g., 2.8.1)
        - description : Official description
        - unit        : Unit (e.g., Cum, Sqm)
        - rate        : Rate in ₹
        """
        if self._df is not None:
            return self._df

        path = Path(self.csv_path)
        if path.is_file():
            try:
                self._df = pd.read_csv(path)
            except Exception as e:
                st.warning(f"Unable to read {self.csv_path}, using sample DSR data. Error: {e}")
                self._df = self._sample_dsr()
        else:
            st.info(f"{self.csv_path} not found in repo. Using sample DSR items.")
            self._df = self._sample_dsr()

        # Basic sanity clean-up
        for col in ["code", "description", "unit"]:
            if col in self._df.columns:
                self._df[col] = self._df[col].astype(str)

        if "rate" in self._df.columns:
            self._df["rate"] = pd.to_numeric(self._df["rate"], errors="coerce")
        else:
            self._df["rate"] = None

        return self._df

    def _sample_dsr(self) -> pd.DataFrame:
        """
        Fallback sample DSR data used if CSV is missing or invalid.
        """
        return pd.DataFrame(
            [
                {
                    "code": "EW-01",
                    "description": "Earthwork in excavation in ordinary soil",
                    "unit": "Cum",
                    "rate": 250.0,
                },
                {
                    "code": "PCC-01",
                    "description": "Plain cement concrete in foundation and flooring",
                    "unit": "Cum",
                    "rate": 4500.0,
                },
                {
                    "code": "RCC-01",
                    "description": "Reinforced cement concrete M25 in slabs",
                    "unit": "Cum",
                    "rate": 7500.0,
                },
                {
                    "code": "BM-01",
                    "description": "Brick masonry in cement mortar",
                    "unit": "Cum",
                    "rate": 5500.0,
                },
                {
                    "code": "PL-01",
                    "description": "12 mm cement plaster on wall surfaces",
                    "unit": "Sqm",
                    "rate": 250.0,
                },
                {
                    "code": "FL-01",
                    "description": "Floor finish / flooring work",
                    "unit": "Sqm",
                    "rate": 800.0,
                },
            ]
        )

    # -----------------------------
    # Public API
    # -----------------------------
    def get_all_items(self) -> pd.DataFrame:
        """
        Return the full DSR table as a DataFrame.
        """
        return self._load_dsr().copy()

    def find_matches(self, keyword: str, unit: str | None = None) -> pd.DataFrame:
        """
        Find DSR items that match a keyword and optional unit.

        Parameters:
        - keyword : part of description to search (case-insensitive)
        - unit    : optional unit filter (e.g., 'Cum', 'Sqm')

        Returns:
        - DataFrame subset with matching rows.
        """
        df = self._load_dsr()
        if not keyword:
            return df.iloc[0:0].copy()

        mask = df["description"].str.contains(keyword, case=False, na=False)

        if unit:
            mask &= df["unit"].str.lower().eq(unit.lower())

        return df[mask].copy()

    def get_rate_for_code(self, code: str) -> float | None:
        """
        Get rate (₹) for a given DSR code.

        Returns None if code not found or rate invalid.
        """
        df = self._load_dsr()
        row = df[df["code"].astype(str) == str(code)]
        if row.empty:
            return None
        rate_val = row.iloc[0].get("rate", None)
        try:
            return float(rate_val)
        except (TypeError, ValueError):
            return None
