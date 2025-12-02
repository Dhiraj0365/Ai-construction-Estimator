class RateAnalyzer:
    """
    Very simple rate breakdown helper.
    For a given total rate, it splits into components using fixed percentages.
    """

    def __init__(self):
        # Percentages can be tuned as per your standard
        self.material_pct = 0.60
        self.labor_pct = 0.25
        self.equipment_pct = 0.10
        self.overhead_pct = 0.05

    def simple_breakdown(self, total_rate: float) -> dict:
        """
        Split total ₹/unit into components.
        """
        material = total_rate * self.material_pct
        labor = total_rate * self.labor_pct
        equipment = total_rate * self.equipment_pct
        overheads = total_rate * self.overhead_pct

        return {
            "material": material,
            "labor": labor,
            "equipment": equipment,
            "overheads": overheads,
        }
