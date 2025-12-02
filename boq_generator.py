from dataclasses import dataclass
from typing import List
import pandas as pd
from io import BytesIO


@dataclass
class BOQItem:
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
    def __init__(self):
        self.items: List[BOQItem] = []

    def clear_items(self):
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
    ):
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
        data = [
            {
                "Item No": it.item_no,
                "Description": it.description,
                "Unit": it.unit,
                "Quantity": it.quantity,
                "Rate (₹/Unit)": it.rate,
                "Amount (₹)": it.amount,
                "WBS Level 1": it.wbs_level1,
                "WBS Level 2": it.wbs_level2,
                "IS Reference": it.is_reference,
            }
            for it in self.items
        ]
        df = pd.DataFrame(data)
        df.attrs["project_name"] = project_name
        df.attrs["project_location"] = project_location
        return df

    def to_excel_bytes(self, df: pd.DataFrame) -> bytes:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="BOQ")
        return output.getvalue()
