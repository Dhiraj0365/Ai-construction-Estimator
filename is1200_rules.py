from dataclasses import dataclass


@dataclass
class MeasurementItem:
    """
    Generic container for a measured work item as per IS 1200.
    """
    description: str
    quantity: float
    unit: str
    is_code_ref: str


class IS1200Engine:
    """
    IS 1200-based measurement engine for the AI Construction Estimator.

    Supports:
    - Earthwork excavation (IS 1200 Part 1)
    - Plain & RCC concrete (IS 1200 Part 2, IS 456)
    - Brick masonry (IS 1200 Part 3)
    - Plastering (IS 1200 Part 12)
    - Flooring (IS 1200 Part 11)
    - Formwork (IS 1200 Part 5)
    - Reinforcement steel (IS 1200 Part 8)
    - Painting / finishing (IS 1200 Part 13)
    """

    # -----------------------------
    # 1. Earthwork Excavation
    # -----------------------------
    def measure_earthwork(
        self,
        length: float,
        width: float,
        depth: float,
        lead: float,
        soil_type: str = "ordinary",
    ) -> MeasurementItem:
        volume = length * width * depth
        desc = (
            f"Earthwork in excavation in {soil_type} soil "
            f"up to {depth:.2f} m depth, lead {lead:.1f} m"
        )
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 1",
        )

    # -----------------------------
    # 2. Concrete (PCC / RCC)
    # -----------------------------
    def measure_concrete(
        self,
        length: float,
        width: float,
        thickness: float,
        grade: str = "M20",
        element_type: str = "PCC",
    ) -> MeasurementItem:
        volume = length * width * thickness
        etype = element_type.lower().strip()

        if etype == "pcc":
            desc = f"Plain cement concrete ({grade}) in foundation and flooring"
            ref = "IS 1200 Part 2"
        else:
            desc = f"Reinforced cement concrete {etype} ({grade}) as per IS 456"
            ref = "IS 1200 Part 2, IS 456"

        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref=ref,
        )

    # -----------------------------
    # 3. Brick Masonry
    # -----------------------------
    def measure_masonry(
        self,
        length: float,
        width: float,
        thickness: float,
        material: str = "brick",
    ) -> MeasurementItem:
        volume = length * width * thickness
        mat = material.capitalize().strip()
        desc = f"{mat} masonry in cement mortar, {thickness:.2f} m thick wall"
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 3",
        )

    # -----------------------------
    # 4. Plastering
    # -----------------------------
    def measure_plaster(
        self,
        length: float,
        height: float,
        thickness_mm: float = 12.0,
    ) -> MeasurementItem:
        area = length * height
        desc = f"{thickness_mm:.0f} mm thick cement plaster on wall surfaces"
        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 12",
        )

    # -----------------------------
    # 5. Flooring / Floor Finishes
    # -----------------------------
    def measure_flooring(
        self,
        length: float,
        width: float,
        thickness_mm: float = 20.0,
    ) -> MeasurementItem:
        area = length * width
        desc = f"{thickness_mm:.0f} mm thick floor finish"
        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 11",
        )

    # -----------------------------
    # 6. Formwork (Shuttering)
    # -----------------------------
    def measure_formwork(
        self,
        area: float,
        element_type: str = "beam",
    ) -> MeasurementItem:
        """
        Formwork measured as surface area in contact with concrete.

        Reference:
        - IS 1200 Part 5: Formwork
        Unit: Sqm
        """
        desc = f"Formwork for {element_type.lower()} (surface in contact with concrete)"
        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 5",
        )

    # -----------------------------
    # 7. Reinforcement steel
    # -----------------------------
    def measure_reinforcement(
        self,
        weight_kg: float,
        bar_type: str = "TMT",
    ) -> MeasurementItem:
        """
        Reinforcement generally measured by weight.

        Reference:
        - IS 1200 Part 8: Steel reinforcement (practice for measurement)
        Unit: Kg
        """
        desc = f"Reinforcement steel ({bar_type}) in RCC work"
        return MeasurementItem(
            description=desc,
            quantity=weight_kg,
            unit="Kg",
            is_code_ref="IS 1200 Part 8",
        )

    # -----------------------------
    # 8. Painting / Finishing
    # -----------------------------
    def measure_painting(
        self,
        area: float,
        system: str = "Acrylic paint",
    ) -> MeasurementItem:
        """
        Painting / finishing measured as area.

        Reference:
        - IS 1200 Part 13: Whitewashing, colour washing, distempering and painting
        Unit: Sqm
        """
        desc = f"Painting / finishing with {system}"
        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 13",
        )
