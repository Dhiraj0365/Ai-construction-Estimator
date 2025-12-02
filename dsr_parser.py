import pandas as pd


class DSRParser:
    """
    Placeholder DSR parser.
    In a real app, parse CPWD/State DSR PDFs and return item/rate tables.
    Here, we just provide a simple sample DataFrame interface.
    """

    def __init__(self):
        self._df = pd.DataFrame(
            [
                {"code": "EW01", "description": "Earthwork excavation in ordinary soil", "unit": "Cum", "rate": 250.0},
                {"code": "RCC01", "description": "RCC M25 concrete", "unit": "Cum", "rate": 7500.0},
            ]
        )

    def get_rates(self) -> pd.DataFrame:
        return self._df.copy()

    def find_rate_by_keyword(self, keyword: str) -> float | None:
        df = self._df[self._df["description"].str.contains(keyword, case=False, na=False)]
        if df.empty:
            return None
        return float(df.iloc[0]["rate"])
