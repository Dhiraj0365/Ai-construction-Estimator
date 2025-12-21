from dataclasses import dataclass


@dataclass
class MeasurementItem:
    """Data class for a single measured item."""
    description: str
    quantity: float
    unit: str
    is_code_ref: str


class IS1200Engine:
    """
    Complete IS 1200 measurement engine for:
    - Earthwork Excavation (Part 1 & 2)
    - Concrete (PCC / RCC members) (Part 2)
    - Reinforcement Steel (Part 8)
    - Brick Masonry (Part 3)
    - Plastering (Part 12)
    - Flooring (Part 11)
    - Formwork (Part 5)
    - Painting (Part 13)
    """

    # ============================================================
    # 1. EARTHWORK EXCAVATION (IS 1200 Part 1 & 2)
    # ============================================================
    def measure_earthwork(
        self,
        length: float,
        width: float,
        depth: float,
        soil_type: str,
        depth_band: str,
        lead_band: str,
    ) -> MeasurementItem:
        """
        Earthwork in excavation as per IS 1200 Part 1 & 2.

        Quantity = net excavated volume (L x B x D in m³)
        Separate items for: soil type, depth range, lead range
        No deduction: PCC volume, slips, working space
        """
        volume = length * width * depth

        desc = (
            f"Earthwork in excavation in {soil_type} soil "
            f"up to {depth_band} depth, lead {lead_band}"
        )

        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 1 & 2",
        )

    # ============================================================
    # 2. CONCRETE (Generic PCC / RCC)
    # ============================================================
    def measure_concrete(
        self,
        length: float,
        width: float,
        thickness: float,
        grade: str,
        element_type: str,
    ) -> MeasurementItem:
        """
        Generic concrete volume = L x B x T (m³).
        Used for PCC or simple RCC elements.
        """
        volume = length * width * thickness
        desc = f"{grade} {element_type} concrete {length:.2f} m x {width:.2f} m x {thickness:.3f} m"

        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 2",
        )

    # ============================================================
    # 3. RCC MEMBERS (SLAB / BEAM / COLUMN / FOOTING)
    # ============================================================
    def measure_rcc_member(
        self,
        member_type: str,
        length: float,
        width: float,
        depth_or_height: float,
        grade: str = "M25",
    ) -> MeasurementItem:
        """
        RCC concrete quantity by member type (IS 1200 Part 2 & IS 456).

        Slab:   L x B x T
        Beam:   L x B x D
        Column: L x B x H
        Footing:L x B x D
        """
        mt = member_type.lower().strip()

        if mt == "slab":
            volume = length * width * depth_or_height
            desc = f"RCC {grade} slab {length:.2f} m x {width:.2f} m x {depth_or_height:.3f} m"
        elif mt == "beam":
            volume = length * width * depth_or_height
            desc = f"RCC {grade} beam {length:.2f} m x {width:.2f} m x {depth_or_height:.3f} m"
        elif mt == "column":
            volume = length * width * depth_or_height
            desc = f"RCC {grade} column {length:.2f} m x {width:.2f} m x {depth_or_height:.3f} m"
        elif mt == "footing":
            volume = length * width * depth_or_height
            desc = f"RCC {grade} footing {length:.2f} m x {width:.2f} m x {depth_or_height:.3f} m"
        else:
            volume = length * width * depth_or_height
            desc = f"RCC {grade} {member_type}"

        return MeasurementItem(
            description=desc,
            quantity=volume,
            unit="Cum",
            is_code_ref="IS 1200 Part 2, IS 456",
        )

    # ============================================================
    # 4. REINFORCEMENT STEEL (Direct kg)
    # ============================================================
    def measure_reinforcement(
        self,
        weight_kg: float,
        bar_type: str = "TMT",
    ) -> MeasurementItem:
        """Direct reinforcement measurement from BBS or site data (kg)."""
        desc = f"Reinforcement steel ({bar_type})"

        return MeasurementItem(
            description=desc,
            quantity=weight_kg,
            unit="Kg",
            is_code_ref="IS 1200 Part 8",
        )

    # ============================================================
    # 5. REINFORCEMENT STEEL (From RCC Volume – Thumb Rules)
    # ============================================================
    def estimate_reinforcement_from_rcc(
        self,
        member_type: str,
        concrete_volume: float,
    ) -> MeasurementItem:
        """
        Quick steel estimate using typical kg/m³ thumb rules:
        - Slab:   ~80 kg/m³
        - Beam:   ~120 kg/m³
        - Column: ~140 kg/m³
        - Footing:~80 kg/m³

        For preliminary estimates; replace with BBS for final.
        """
        mt = member_type.lower().strip()
        if mt == "slab":
            density = 80.0
        elif mt == "beam":
            density = 120.0
        elif mt == "column":
            density = 140.0
        elif mt == "footing":
            density = 80.0
        else:
            density = 100.0

        weight_kg = concrete_volume * density
        desc = f"Reinforcement steel (estimated) in RCC {member_type} @ {density:.0f} kg/m³"

        return MeasurementItem(
            description=desc,
            quantity=weight_kg,
            unit="Kg",
            is_code_ref="IS 1200 Part 8 (thumb rule)",
        )

    # ============================================================
    # 6. BRICK MASONRY (With Openings)
    # ============================================================
    def measure_masonry(
        self,
        length: float,
        height: float,
        thickness: float,
        material: str = "brick",
        n_small_openings: int = 0,
        area_small_each: float = 0.0,
        n_large_openings: int = 0,
        area_large_each: float = 0.0,
    ) -> MeasurementItem:
        """
        Masonry measurement as per IS 1200 Part 3.

        Gross volume = L x H x T
        Deduct only openings > 0.1 m²
        Do not deduct openings ≤ 0.1 m² or small beam/column ends
        """
        volume_gross = length * height * thickness

        # Small openings (≤ 0.1 m²) – information only, no deduction
        small_opening_area = n_small_openings * area_small_each

        # Large openings (> 0.1 m²) – deduct
        large_opening_area = n_large_openings * area_large_each
        volume_deduction = large_opening_area * thickness

        volume_net = volume_gross - volume_deduction
        if volume_net < 0:
            volume_net = 0.0

        mat = material.capitalize().strip()

        desc_parts = [
            f"{mat} masonry in cement mortar",
            f"{thickness:.3f} m thick wall",
        ]
        if n_large_openings > 0:
            desc_parts.append(
                f"with deduction for {n_large_openings} opening(s) > 0.1 m² as per IS 1200 Part 3"
            )
        else:
            desc_parts.append(
                "no deduction for openings ≤ 0.1 m² as per IS 1200 Part 3"
            )

        desc = ", ".join(desc_parts)

        return MeasurementItem(
            description=desc,
            quantity=volume_net,
            unit="Cum",
            is_code_ref="IS 1200 Part 3",
        )

    # ============================================================
    # 7. PLASTERING (With Openings)
    # ============================================================
    def measure_plaster(
        self,
        length: float,
        height: float,
        face_count: int = 1,
        n_small_openings: int = 0,
        area_small_each: float = 0.0,
        n_large_openings: int = 0,
        area_large_each: float = 0.0,
        thickness_mm: float = 12.0,
    ) -> MeasurementItem:
        """
        Plaster measurement as per IS 1200 Part 12.

        Base area per face = L x H (Sqm)
        No deduction for openings ≤ 0.5 m²
        Deduct openings > 0.5 m²
        Thickness for description/rate only; quantity in Sqm
        """
        base_area_one_face = length * height

        # Small openings (≤ 0.5 m²) – no deduction, info only
        small_opening_area_total = n_small_openings * area_small_each

        # Large openings (> 0.5 m²) – deduct
        large_opening_area_total = n_large_openings * area_large_each

        gross_area_all_faces = base_area_one_face * face_count
        deduction_all_faces = large_opening_area_total * face_count

        net_area = gross_area_all_faces - deduction_all_faces
        if net_area < 0:
            net_area = 0.0

        face_text = "one face" if face_count == 1 else f"{face_count} faces"

        desc_parts = [
            f"{thickness_mm:.0f} mm thick cement plaster on {face_text} of wall surfaces",
        ]
        if n_large_openings > 0:
            desc_parts.append(
                f"with deduction for {n_large_openings} opening(s) > 0.5 m² as per IS 1200 Part 12"
            )
        else:
            desc_parts.append(
                "no deduction for openings ≤ 0.5 m² as per IS 1200 Part 12"
            )

        desc = ", ".join(desc_parts)

        return MeasurementItem(
            description=desc,
            quantity=net_area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 12",
        )

    # ============================================================
    # 8. FLOORING (With Openings)
    # ============================================================
    def measure_flooring(
        self,
        length: float,
        width: float,
        n_small_openings: int = 0,
        area_small_each: float = 0.0,
        n_large_openings: int = 0,
        area_large_each: float = 0.0,
        thickness_mm: float = 20.0,
        floor_type: str = "cement concrete",
    ) -> MeasurementItem:
        """
        Flooring measurement as per IS 1200 Part 11.

        Base area = L x B (finished floor surface, Sqm)
        No deduction for openings ≤ 0.1 m²
        Deduct openings > 0.1 m²
        Thickness for description only; quantity in Sqm
        """
        gross_area = length * width

        # Small openings (≤ 0.1 m²) – no deduction
        small_opening_area_total = n_small_openings * area_small_each

        # Large openings (> 0.1 m²) – deduct
        large_opening_area_total = n_large_openings * area_large_each

        net_area = gross_area - large_opening_area_total
        if net_area < 0:
            net_area = 0.0

        desc_parts = [
            f"{thickness_mm:.0f} mm thick {floor_type} flooring on finished surface",
        ]
        if n_large_openings > 0:
            desc_parts.append(
                f"with deduction for {n_large_openings} opening(s) > 0.1 m² as per IS 1200 Part 11"
            )
        else:
            desc_parts.append(
                "no deduction for openings ≤ 0.1 m² as per IS 1200 Part 11"
            )

        desc = ", ".join(desc_parts)

        return MeasurementItem(
            description=desc,
            quantity=net_area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 11",
        )

    # ============================================================
    # 9. FORMWORK (Concrete Contact Area)
    # ============================================================
    def measure_formwork(
        self,
        member_type: str,
        length: float,
        width: float,
        depth_or_height: float,
    ) -> MeasurementItem:
        """
        Formwork measurement as per IS 1200 Part 5.

        Quantity = concrete contact area (Sqm):
        - Slab:  soffit area = plan (L x B)
        - Beam:  2 sides (D x L) + soffit (B x L)
        - Column: 4 sides = perimeter x height
        - Footing: 2(L x D) + 2(B x D)

        No deduction for small openings ≤ 0.4 m², fillets, chamfers.
        """
        mt = member_type.lower().strip()

        if mt == "slab":
            area = length * width
            desc = f"Formwork to soffit of RCC slab {length:.2f} m x {width:.2f} m"
        elif mt == "beam":
            side_area = 2 * (depth_or_height * length)
            bottom_area = width * length
            area = side_area + bottom_area
            desc = (
                f"Formwork to sides and soffit of RCC beam "
                f"{length:.2f} m x {width:.2f} m x {depth_or_height:.2f} m"
            )
        elif mt == "column":
            perimeter = 2 * (length + width)
            area = perimeter * depth_or_height
            desc = (
                f"Formwork to sides of RCC column "
                f"{length:.2f} m x {width:.2f} m x {depth_or_height:.2f} m"
            )
        elif mt == "footing":
            area = 2 * (length * depth_or_height) + 2 * (width * depth_or_height)
            desc = (
                f"Formwork to sides of RCC footing "
                f"{length:.2f} m x {width:.2f} m x {depth_or_height:.2f} m"
            )
        else:
            area = length * depth_or_height
            desc = f"Formwork to RCC {member_type}"

        full_desc = (
            desc
            + ", measured as concrete contact area, "
            "no deduction for small openings ≤ 0.4 m² as per IS 1200 Part 5"
        )

        return MeasurementItem(
            description=full_desc,
            quantity=area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 5",
        )

    # ============================================================
    # 10. PAINTING / FINISHING (With Openings)
    # ============================================================
    def measure_painting(
        self,
        length: float,
        height: float,
        face_count: int = 1,
        n_small_openings: int = 0,
        area_small_each: float = 0.0,
        n_large_openings: int = 0,
        area_large_each: float = 0.0,
        coats: int = 2,
        paint_type: str = "acrylic",
    ) -> MeasurementItem:
        """
        Painting measurement as per IS 1200 Part 13.

        Uses same area rules as plaster (deduct only openings > 0.5 m²)
        Quantity = net surface area (Sqm)
        Coats and type in description only; they affect rate, not quantity
        """
        base_area_one_face = length * height

        # Small openings (≤ 0.5 m²) – no deduction
        small_opening_area_total = n_small_openings * area_small_each

        # Large openings (> 0.5 m²) – deduct
        large_opening_area_total = n_large_openings * area_large_each

        gross_area_all_faces = base_area_one_face * face_count
        deduction_all_faces = large_opening_area_total * face_count

        net_area = gross_area_all_faces - deduction_all_faces
        if net_area < 0:
            net_area = 0.0

        face_text = "one face" if face_count == 1 else f"{face_count} faces"
        coat_text = f"{coats} coats" if coats > 1 else "one coat"

        desc_parts = [
            f"{coat_text} of {paint_type} paint over primer on {face_text}",
        ]
        if n_large_openings > 0:
            desc_parts.append(
                f"with deduction for {n_large_openings} opening(s) > 0.5 m² as per IS 1200 Part 13"
            )
        else:
            desc_parts.append(
                "no deduction for openings ≤ 0.5 m² as per IS 1200 Part 13"
            )

        desc = ", ".join(desc_parts)

        return MeasurementItem(
            description=desc,
            quantity=net_area,
            unit="Sqm",
            is_code_ref="IS 1200 Part 13",
        )
