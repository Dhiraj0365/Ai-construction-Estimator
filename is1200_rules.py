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
        - IS 1200 Part 1: Earthwork
        - IS 1200 Part 2: Concrete work (lead, lift concepts also used)
        """
        volume = length * width * depth
        desc = (
            f"Earthwork excavation in {soil_type} soil, "
            f"depth {depth:.2f} m, lead {lead:.1f} m"
        )
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 1 & 2",
        )

    # -----------------------------
    # Concrete (PCC, RCC)
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
        desc = f"{element_type.upper()} using {grade} grade concrete as per IS 456"
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 2, IS 456",
        )

    # -----------------------------
    # Masonry
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
        - IS 1200 Part 3: Brickwork / masonry
        """
        volume = length * width * thickness
        desc = (
            f"{material.capitalize()} masonry wall, "
            f"thickness {thickness:.2f} m"
        )
        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 3",
        )

    # -----------------------------
    # Plastering
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
        desc = (
            f"Plastering {thickness_mm:.0f} mm thick on wall surface "
            f"(L={length:.2f} m, H={height:.2f} m)"
        )
        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 12",
        )

    # -----------------------------
    # Flooring
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
        desc = (
            f"Flooring {thickness_mm:.0f} mm thick "
            f"(L={length:.2f} m, W={width:.2f} m)"
        )
        return MeasurementItem(
            description=desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 11",
        )
