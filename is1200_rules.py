from dataclasses import dataclass


@dataclass
class MeasurementItem:
    """
    Generic container for a measured work item.
    """
    description: str
    quantity: float
    unit: str
    is_code_ref: str


class IS1200Engine:
    """
    Minimal IS 1200-based measurement engine for the AI Construction Estimator.

    This version supports:
    - Earthwork excavation (IS 1200 Part 1 & 2)
    - Plain concrete (PCC) (IS 1200 Part 2)
    - RCC concrete (e.g., slab M25) (IS 1200 Part 2, IS 456)
    - Brick masonry (IS 1200 Part 3)
    - Plastering (IS 1200 Part 12)
    - Flooring (IS 1200 Part 11)
    """

    # -----------------------------
    # Earthwork
    # -----------------------------
   def measure_earthwork(...):
    volume = length * width * depth
    desc = (
        f"Earthwork in excavation in ordinary soil "
        f"up to {depth:.2f} m depth, lead {lead:.1f} m"
    )
    return MeasurementItem(
        description=desc,
        quantity=volume,
        unit="Cum",
        is_code_ref="IS 1200 Part 1",
    )

def measure_concrete(...):
    volume = length * width * thickness
    if element_type.lower() == "pcc":
        desc = f"Plain cement concrete ({grade}) in foundation and flooring"
        ref = "IS 1200 Part 2"
    else:
        desc = f"Reinforced cement concrete {element_type.lower()} ({grade}) as per IS 456"
        ref = "IS 1200 Part 2, IS 456"
    return MeasurementItem(description=desc, quantity=volume, unit="Cum", is_code_ref=ref)

def measure_masonry(...):
    volume = length * width * thickness
    desc = f"Brick masonry in cement mortar, {thickness:.2f} m thick wall"
    return MeasurementItem(description=desc, quantity=volume, unit="Cum", is_code_ref="IS 1200 Part 3")

def measure_plaster(...):
    area = length * height
    desc = f"12 mm cement plaster on wall surfaces"
    return MeasurementItem(description=desc, quantity=area, unit="Sqm", is_code_ref="IS 1200 Part 12")

def measure_flooring(...):
    area = length * width
    desc = f"{thickness_mm:.0f} mm thick floor finish"
    return MeasurementItem(description=desc, quantity=area, unit="Sqm", is_code_ref="IS 1200 Part 11")

