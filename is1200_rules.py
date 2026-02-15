# is1200_rules.py

"""
IS 1200 Measurement Engine – Building Works

This module provides reusable helpers for civil quantity calculation
aligned with IS 1200 style measurement, suitable for CPWD/State SoR
estimation and MB preparation.

Design goals:
- Technically correct, audit‑friendly quantities.
- Separate logic for volume, area, formwork and openings.
- Conservative, IS‑style rules (no negative quantities, proper rounding).
- Backward compatible with your existing streamlit_app usage:
  - IS1200Engine.volume(...)
  - IS1200Engine.wall_finish_area(...)
  - IS1200Engine.formwork_column_area(...)
  - IS1200Engine.formwork_beam_area(...)
  - IS1200Engine.formwork_slab_area(...)

Note:
- Exact thresholds and rules may vary slightly between IS 1200,
  CPWD Works Manual and local SoR practice. Key limits are parameterised
  (e.g. 0.1 m², 0.5 m², 3.0 m²) so you can tune them if needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Internal helper dataclass for consistent results
# ---------------------------------------------------------------------------

@dataclass
class MeasureResult:
    """Container for a measurement computation."""

    gross: float
    deductions: float = 0.0
    additions: float = 0.0
    unit: str = ""
    meta: Dict[str, float | str] = field(default_factory=dict)

    def to_dict(self, round_to: int = 3) -> Dict[str, float | str]:
        """Convert to dict (gross, deductions, additions, net, ...)."""
        g = round(self.gross, round_to)
        d = round(self.deductions, round_to)
        a = round(self.additions, round_to)
        n = round(max(g - d + a, 0.0), round_to)
        out: Dict[str, float | str] = {
            "gross": g,
            "deductions": d,
            "additions": a,
            "net": n,
        }
        out.update(self.meta)
        return out


def _round_for_unit(value: float, unit: str) -> float:
    """
    IS‑1200 style rounding:
    - Linear (m): 2 decimals
    - Area (sqm): 2 decimals
    - Volume (cum): 3 decimals
    - Weight (kg): 2 decimals
    Default: 3 decimals
    """
    unit = unit.lower().strip()
    if unit in ("m", "rm", "rmt"):
        return round(value, 2)
    if unit in ("sqm", "m2", "sq.m", "sq.m."):
        return round(value, 2)
    if unit in ("cum", "m3", "cu.m", "cu.m."):
        return round(value, 3)
    if unit in ("kg", "kilogram", "kilograms"):
        return round(value, 2)
    return round(value, 3)


def _normalise_openings(openings: Optional[List[Dict]]) -> List[Dict]:
    """
    Normalise openings to a uniform structure:
    each opening: {"w": width, "h": height, "n": count}
    """
    if not openings:
        return []
    out: List[Dict] = []
    for o in openings:
        if not isinstance(o, dict):
            continue
        w = float(o.get("w", 0.0))
        h = float(o.get("h", 0.0))
        n = float(o.get("n", 1.0))
        if w <= 0 or h <= 0 or n <= 0:
            continue
        out.append({"w": w, "h": h, "n": n})
    return out


# ---------------------------------------------------------------------------
# Public Engine
# ---------------------------------------------------------------------------

class IS1200Engine:
    """
    Core IS‑1200 style calculation helpers.

    All methods return dictionaries with at least:
    - gross
    - deductions
    - additions
    - net

    For backward compatibility with your Streamlit app, the
    following methods should be considered stable:
    - volume(...)
    - wall_finish_area(...)
    - formwork_column_area(...)
    - formwork_beam_area(...)
    - formwork_slab_area(...)
    """

    # ---------------------------------------------------------------------
    # GENERIC VOLUME – EARTHWORK, CONCRETE, BRICKWORK
    # ---------------------------------------------------------------------
    @staticmethod
    def volume(
        L: float,
        B: float,
        D: float,
        deductions: float = 0.0,
        unit: str = "cum",
    ) -> Dict[str, float]:
        """
        Generic volume as L × B × D minus explicit deductions.

        Parameters
        ----------
        L, B, D : float
            Length, breadth, depth (m).
        deductions : float, optional
            Deductions in m³ (already combined).
        unit : str
            Output unit (default cum).

        Returns
        -------
        dict
            {gross, deductions, additions, net, pct}
        """
        gross = max(L, 0.0) * max(B, 0.0) * max(D, 0.0)
        deductions = max(deductions, 0.0)

        # Round per unit
        gross_r = _round_for_unit(gross, unit)
        ded_r = _round_for_unit(deductions, unit)
        net_r = _round_for_unit(max(gross_r - ded_r, 0.0), unit)

        pct = round((ded_r / gross_r * 100.0), 2) if gross_r > 0 else 0.0

        return {
            "gross": gross_r,
            "deductions": ded_r,
            "additions": 0.0,
            "net": net_r,
            "pct": pct,
        }

    # ---------------------------------------------------------------------
    # EARTHWORK – TRENCH EXCAVATION WITH SIDE SLOPES
    # ---------------------------------------------------------------------
    @staticmethod
    def trench_excavation(
        length: float,
        breadth_bottom: float,
        depth: float,
        side_slope_h_over_v: float = 0.0,
        deductions: float = 0.0,
        unit: str = "cum",
    ) -> Dict[str, float]:
        """
        Earthwork in excavation for trenches/foundations.

        If side_slope_h_over_v > 0, uses average breadth as per
        side slopes:
            top_breadth = breadth_bottom + 2 * side_slope * depth
            avg_breadth = (breadth_bottom + top_breadth) / 2

        For vertical sides, side_slope_h_over_v = 0.

        Returns
        -------
        dict : {gross, deductions, additions, net}
        """
        length = max(length, 0.0)
        breadth_bottom = max(breadth_bottom, 0.0)
        depth = max(depth, 0.0)

        if side_slope_h_over_v > 0.0:
            top_b = breadth_bottom + 2.0 * side_slope_h_over_v * depth
            avg_b = (breadth_bottom + top_b) / 2.0
            gross = length * avg_b * depth
        else:
            gross = length * breadth_bottom * depth

        mr = MeasureResult(gross=gross, deductions=max(deductions, 0.0), unit=unit)
        return mr.to_dict(round_to=3)

    # ---------------------------------------------------------------------
    # BRICKWORK – WALL VOLUME WITH OPENING DEDUCTIONS
    # ---------------------------------------------------------------------
    @staticmethod
    def brickwork_wall(
        length: float,
        thickness: float,
        height: float,
        openings: Optional[List[Dict]] = None,
        small_opening_limit: float = 0.10,   # sqm (typical IS‑1200)
        unit: str = "cum",
    ) -> Dict[str, float]:
        """
        Brick masonry in wall.

        - Gross = length × thickness × height
        - No deduction for individual openings up to small_opening_limit
          (IS 1200 Part 5, small apertures).
        - Full deduction for larger openings: area × thickness.

        Parameters
        ----------
        openings : list of dict, optional
            Each {"w": width_m, "h": height_m, "n": count}

        Returns
        -------
        dict : {gross, deductions, additions, net}
        """
        length = max(length, 0.0)
        thickness = max(thickness, 0.0)
        height = max(height, 0.0)

        gross = length * thickness * height

        norm_openings = _normalise_openings(openings)
        ded = 0.0
        for o in norm_openings:
            area_one = o["w"] * o["h"]
            n = o["n"]
            if area_one <= small_opening_limit:
                # No deduction (small openings)
                continue
            ded += area_one * thickness * n

        mr = MeasureResult(gross=gross, deductions=ded, unit=unit)
        return mr.to_dict(round_to=3)

    # ---------------------------------------------------------------------
    # PLASTER / PAINT – WALL FINISH AREA WITH OPENINGS
    # ---------------------------------------------------------------------
    @staticmethod
    def wall_finish_area(
        length: float,
        height: float,
        sides: int = 2,
        openings: Optional[List[Dict]] = None,
        small_opening_limit: float = 0.50,   # no deduction
        medium_opening_limit: float = 3.00,  # deduct one face only
        unit: str = "sqm",
    ) -> Dict[str, float]:
        """
        Wall surface area for plaster/putty/painting as per IS‑1200 style.

        Simplified rule set:
        - Gross area = length × height × sides.
        - For each opening (area A per face):
          * A <= small_opening_limit  → no deduction for opening or jambs.
          * small_opening_limit < A <= medium_opening_limit
                → deduct A for ONE face only (for both‑side finish).
          * A > medium_opening_limit → deduct A × sides (full opening on all sides).

        Parameters
        ----------
        openings : list of dict, optional
            Each {"w": width_m, "h": height_m, "n": count}

        Returns
        -------
        dict : {gross, deductions, additions, net}
        """
        length = max(length, 0.0)
        height = max(height, 0.0)
        sides = max(int(sides), 0)

        gross = length * height * sides

        norm_openings = _normalise_openings(openings)
        ded = 0.0

        for o in norm_openings:
            A_one = o["w"] * o["h"]  # area on one face
            n = o["n"]

            if A_one <= small_opening_limit:
                # No deduction
                continue
            elif A_one <= medium_opening_limit:
                # Deduct one face only (per opening group)
                ded += A_one * n
            else:
                # Deduct for all sides
                ded += A_one * sides * n

        mr = MeasureResult(gross=gross, deductions=ded, unit=unit)
        return mr.to_dict(round_to=2)

    # ---------------------------------------------------------------------
    # FLOORING / TILING AREA
    # ---------------------------------------------------------------------
    @staticmethod
    def floor_area(
        length: float,
        breadth: float,
        cutouts: Optional[List[Dict]] = None,
        unit: str = "sqm",
    ) -> Dict[str, float]:
        """
        Floor / roof / tile area.

        Gross = length × breadth (single side).
        cutouts: list of {"w": width_m, "h": height_m, "n": count}
        """
        length = max(length, 0.0)
        breadth = max(breadth, 0.0)
        gross = length * breadth

        norm_cutouts = _normalise_openings(cutouts)
        ded = 0.0
        for c in norm_cutouts:
            ded += c["w"] * c["h"] * c["n"]

        mr = MeasureResult(gross=gross, deductions=ded, unit=unit)
        return mr.to_dict(round_to=2)

    # ---------------------------------------------------------------------
    # RCC FORMWORK AREAS
    # ---------------------------------------------------------------------
    @staticmethod
    def formwork_column_area(
        L: float,
        B: float,
        H: float,
        unit: str = "sqm",
    ) -> float:
        """
        Formwork for column – area of four faces.

        Approx as:
            2 × (L + B) × H

        Returns
        -------
        float : area in sqm (rounded as per unit).
        """
        L = max(L, 0.0)
        B = max(B, 0.0)
        H = max(H, 0.0)
        area = 2.0 * (L + B) * H
        return _round_for_unit(area, unit)

    @staticmethod
    def formwork_beam_area(
        breadth: float,
        depth: float,
        length: float,
        unit: str = "sqm",
    ) -> float:
        """
        Formwork for beam – 3 exposed sides (bottom + 2 sides).

        Approx as:
            (2 × depth + breadth) × length
        """
        breadth = max(breadth, 0.0)
        depth = max(depth, 0.0)
        length = max(length, 0.0)
        area = (2.0 * depth + breadth) * length
        return _round_for_unit(area, unit)

    @staticmethod
    def formwork_slab_area(
        length: float,
        breadth: float,
        unit: str = "sqm",
    ) -> float:
        """
        Formwork for slab – soffit area.

        Approx as:
            length × breadth
        """
        length = max(length, 0.0)
        breadth = max(breadth, 0.0)
        area = length * breadth
        return _round_for_unit(area, unit)

    # ---------------------------------------------------------------------
    # SIMPLE REBAR UTILITIES (OPTIONAL)
    # ---------------------------------------------------------------------
    @staticmethod
    def steel_from_kg_per_cum(
        concrete_volume_cum: float,
        kg_per_cum: float,
        unit: str = "kg",
    ) -> Dict[str, float]:
        """
        Convenience function for RCC estimation when you use
        empirical kg of steel per cubic metre of RCC.

        Parameters
        ----------
        concrete_volume_cum : float
            Net concrete volume in m³.
        kg_per_cum : float
            Assumed steel consumption in kg/m³.

        Returns
        -------
        dict : {gross, deductions, additions, net}
               (all values same, in kg)
        """
        concrete_volume_cum = max(concrete_volume_cum, 0.0)
        kg_per_cum = max(kg_per_cum, 0.0)
        wt = concrete_volume_cum * kg_per_cum
        mr = MeasureResult(gross=wt, deductions=0.0, unit=unit)
        return mr.to_dict(round_to=2)

    # You can extend this class further with:
    # - earthwork_roadwork(...)
    # - concrete_pavement(...)
    # - detailed lintel / chajja / sill rules
    # - etc.


# If you want a quick standalone test, run this file directly.
if __name__ == "__main__":
    # Example self‑test
    print("Volume test:", IS1200Engine.volume(5, 2, 0.3))
    print(
        "Wall finish with opening:",
        IS1200Engine.wall_finish_area(
            length=5,
            height=3,
            sides=2,
            openings=[{"w": 1.2, "h": 1.5, "n": 2}],
        ),
    )
    print(
        "Brickwork:",
        IS1200Engine.brickwork_wall(
            length=5,
            thickness=0.23,
            height=3,
            openings=[{"w": 1.0, "h": 2.1, "n": 1}],
        ),
    )
