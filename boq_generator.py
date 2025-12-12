from dataclasses import dataclass
from typing import List
import pandas as pd
from io import BytesIO


@dataclass
class BOQItem:
    """
    Single BOQ line item.
    """
    item_no: str
    description: str
    unit: str
    quantity: float
    rate: float
    amount: float
    wbs_level1: str
    wbs_level2: str
    is_reference: str


class BOQGenerator:
    """
    Helper to collect BOQ items and output them as
    a pandas DataFrame and Excel bytes.
    """

    def __init__(self):
        self.items: List[BOQItem] = []

    def clear_items(self) -> None:
        """Remove all stored BOQ items."""
        self.items = []

    def add_boq_item(
        self,
        item_no: str,
        description: str,
        unit: str,
        quantity: float,
        rate: float,
        amount: float,
        wbs_level1: str,
        wbs_level2: str,
        is_reference: str,
    ) -> None:
        """Append one BOQ line item."""
        self.items.append(
            BOQItem(
                item_no=item_no,
                description=description,
                unit=unit,
                quantity=quantity,
                rate=rate,
                amount=amount,
                wbs_level1=wbs_level1,
                wbs_level2=wbs_level2,
                is_reference=is_reference,
            )
        )

    def generate_dataframe(self, project_name: str, project_location: str) -> pd.DataFrame:
        """
        Build a DataFrame in standard BOQ format.

        Columns:
        - Item No
        - Description of Item
        - Unit
        - Quantity
        - Rate (₹)
        - Amount (₹)
        - WBS Level 1
        - WBS Level 2
        - IS Reference
        """
        data = [
            {
                "Item No": it.item_no,
                "Description of Item": it.description,
                "Unit": it.unit,
                "Quantity": it.quantity,
                "Rate (₹)": it.rate,
                "Amount (₹)": it.amount,
                "WBS Level 1": it.wbs_level1,
                "WBS Level 2": it.wbs_level2,
                "IS Reference": it.is_reference,
            }
            for it in self.items
        ]

        df = pd.DataFrame(data)
        # Store metadata as attributes (can be used when writing Excel header)
        df.attrs["project_name"] = project_name
        df.attrs["project_location"] = project_location
        return df

    def to_excel_bytes(self, df: pd.DataFrame) -> bytes:
        """
        Convert the BOQ DataFrame to an in-memory Excel file (bytes),
        ready for Streamlit download.
        """
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Write BOQ sheet
            df.to_excel(writer, index=False, sheet_name="BOQ")

        return output.getvalue()
