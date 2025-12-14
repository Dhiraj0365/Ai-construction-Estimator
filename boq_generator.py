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
    a pandas DataFrame and Excel bytes (BOQ + Abstract).
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
        df.attrs["project_name"] = project_name
        df.attrs["project_location"] = project_location
        return df

    def to_excel_bytes(
        self,
        df_boq: pd.DataFrame,
        section_totals: pd.DataFrame | None = None,
        base_total: float | None = None,
        contingency_pct: float | None = None,
        overhead_pct: float | None = None,
        profit_pct: float | None = None,
        gst_pct: float | None = None,
    ) -> bytes:
        """
        Convert the BOQ DataFrame to an in-memory Excel file (bytes),
        with two sheets:
        - 'BOQ'      : Detailed item-wise BOQ
        - 'Abstract' : Section-wise totals + percentage provisions
        """
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: Detailed BOQ
            df_boq.to_excel(writer, index=False, sheet_name="BOQ")

            # Sheet 2: Abstract of cost
            abstract_rows = []

            # Section-wise totals
            if section_totals is not None and not section_totals.empty:
                abstract_rows.append({"Head": "Section-wise totals", "Amount (₹)": ""})
                for _, row in section_totals.iterrows():
                    abstract_rows.append(
                        {
                            "Head": str(row["WBS Level 1"]),
                            "Amount (₹)": row["Amount (₹)"],
                        }
                    )

            # Base total and percentage provisions
            cont_amt = 0.0
            oh_amt = 0.0
            profit_amt = 0.0
            gst_amt = 0.0

            if base_total is not None:
                abstract_rows.append({"Head": "", "Amount (₹)": ""})
                abstract_rows.append(
                    {
                        "Head": "Base total",
                        "Amount (₹)": base_total,
                    }
                )

                # Contingency
                if contingency_pct is not None:
                    cont_amt = base_total * contingency_pct / 100.0
                    abstract_rows.append(
                        {
                            "Head": f"Add: Contingency @ {contingency_pct:.1f}%",
                            "Amount (₹)": cont_amt,
                        }
                    )

                # Overheads
                if overhead_pct is not None:
                    oh_amt = base_total * overhead_pct / 100.0
                    abstract_rows.append(
                        {
                            "Head": f"Add: Departmental overheads @ {overhead_pct:.1f}%",
                            "Amount (₹)": oh_amt,
                        }
                    )

                # Contractor's profit
                if profit_pct is not None:
                    profit_base = base_total + cont_amt + oh_amt
                    profit_amt = profit_base * profit_pct / 100.0
                    abstract_rows.append(
                        {
                            "Head": f"Add: Contractor's profit @ {profit_pct:.1f}%",
                            "Amount (₹)": profit_amt,
                        }
                    )

                # GST
                if gst_pct is not None:
                    tax_base = base_total + cont_amt + oh_amt + profit_amt
                    gst_amt = tax_base * gst_pct / 100.0
                    abstract_rows.append(
                        {
                            "Head": f"Add: GST @ {gst_pct:.1f}%",
                            "Amount (₹)": gst_amt,
                        }
                    )

                # Grand total
                final_total = base_total + cont_amt + oh_amt + profit_amt + gst_amt
                abstract_rows.append({"Head": "", "Amount (₹)": ""})
                abstract_rows.append(
                    {
                        "Head": "Grand total",
                        "Amount (₹)": final_total,
                    }
                )

            if abstract_rows:
                df_abs = pd.DataFrame(abstract_rows)
                df_abs.to_excel(writer, index=False, sheet_name="Abstract")

        return output.getvalue()
        
