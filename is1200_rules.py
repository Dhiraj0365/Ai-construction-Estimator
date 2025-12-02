from dataclasses import dataclass


@dataclass
class MeasurementItem:
    description: str
    quantity: float
    unit: str
    is_code_ref: str


class IS1200Engine:
    """
    Minimal measurement engine aligned with IS 1200 logic for demo.
    Extend with more detailed rules as needed.
    """

    def measure_earthwork(self, length: float, width: float, depth: float, lead: float, soil_type: str = "ordinary") -> MeasurementItem:
        """
        Simple volume = L x W x D for earthwork excavation.
        Uses IS 1200 Part 1 & 2 as reference (no deductions, basic case).
        """
        volume = length * width * depth
        desc = f"Earthwork excavation in {soil_type} soil, depth {depth:.2f} m, lead {lead:.1f} m"
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 1 & 2",
        )

    def measure_concrete(self, length: float, width: float, thickness: float, grade: str = "M25", element_type: str = "slab") -> MeasurementItem:
        """
        Simple volume = L x W x T for RCC concrete.
        Reference: IS 1200 Part 9 for concrete, IS 456 for design.
        """
        volume = length * width * thickness
        desc = f"RCC {element_type.capitalize()} using {grade} grade concrete as per IS 456"
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 9, IS 456",
        )
