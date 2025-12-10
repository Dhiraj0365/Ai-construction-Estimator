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

    Currently supports:
    - Earthwork excavation (IS 1200 Part 1)
    - Plain concrete (PCC) (IS 1200 Part 2)
    - RCC concrete (e.g., slab M25) (IS 1200 Part 2, IS 456)
    - Brick masonry (IS 1200 Part 3)
    - Plastering (IS 1200 Part 12)
    - Flooring / floor finishes (IS 1200 Part 11)
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
        """
        Volume-based measurement for earthwork excavation.

        Simple volume = L × W × D (Cum).

        Reference:
        - IS 1200 Part 1: Earthwork (method of measurement)
        """
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
        """
        Volume-based measurement for concrete items (PCC, RCC).

        Simple volume = L × W × T (Cum).

        Reference:
        - IS 1200 Part 2: Concrete work (measurement)
        - IS 456: Plain and reinforced concrete (design)
        """
        volume = length * width * thickness

        etype = element_type.lower().strip()

        if etype == "pcc":
            # Plain concrete (e.g., in foundations, flooring)
            desc = f"Plain cement concrete ({grade}) in foundation and flooring"
            ref = "IS 1200 Part 2"
        else:
            # Reinforced concrete element (slab, beam, footing, etc.)
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
        """
        Volume-based measurement for masonry work.

        Simple volume = L × W × T (Cum).

        Reference:
        - IS 1200 Part 3: Brickwork and stone masonry
        """
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
        """
        Area-based measurement for plastering.

        Simple area = L × H (Sqm).

        Reference:
        - IS 1200 Part 12: Plastering and pointing
        """
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
        """
        Area-based measurement for flooring / floor finishes.

        Simple area = L × W (Sqm).

        Reference:
        - IS 1200 Part 11: Flooring, dado, skirting and similar finishes
        """
        area = length * width

        desc = f"{thickness_mm:.0f} mm thick floor finish"

        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 11",
        )
