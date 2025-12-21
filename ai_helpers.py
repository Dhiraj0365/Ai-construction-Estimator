# ai_helpers.py

from typing import List, Dict
import pandas as pd


class AISuggester:
    """
    Helper for AI-based suggestions (DSR mapping, etc.).
    You need to wire this to your LLM provider (OpenAI, Perplexity, etc.).
    """

    def __init__(self):
        # Add any API keys / client initialization you need here
        pass

    def suggest_dsr_items(
        self,
        boq_description: str,
        unit: str,
        dsr_df: pd.DataFrame,
        top_n: int = 5,
    ) -> List[Dict]:
        """
        Given a BOQ line description + unit and the full DSR table,
        return a list of up to top_n suggested DSR items.

        Each dict in the list should have keys:
        - code
        - description
        - unit
        - rate
        - match_reason (optional text)
        """
        # ---- PSEUDOCODE / PLACEHOLDER ----
        # Here you will:
        # - Build a prompt with boq_description and a subset of dsr_df
        # - Call your LLM API
        # - Parse the response into the list of dicts described above
        #
        # For now, we can do a simple fallback: just return the same as
        # a keyword search using description .str.contains.
        # This keeps code working even before LLM integration.

        if dsr_df.empty:
            return []

        mask = dsr_df["description"].str.contains(boq_description, case=False, na=False)
        if unit:
            mask |= dsr_df["unit"].str.lower().eq(unit.lower())

        candidates = dsr_df[mask].head(top_n)

        results: List[Dict] = []
        for _, row in candidates.iterrows():
            results.append(
                {
                    "code": row.get("code", ""),
                    "description": row.get("description", ""),
                    "unit": row.get("unit", ""),
                    "rate": row.get("rate", None),
                    "match_reason": "Keyword fallback (LLM not wired yet)",
                }
            )
        return results
