"""
rate_analyzer.py
Detailed rate analysis per CPWD guidelines
Breakup: Materials (60%) + Labor (25%) + Equipment (10%) + Overheads (5%) + Profit (10%)
"""

import pandas as pd
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class RateAnalysis:
    """Detailed rate breakup for a construction item"""
    item_description: str
    unit: str
    
    # Material component
    material_cost: float
    material_percentage: float = 60.0
    
    # Labor component
    labor_cost: float
    labor_percentage: float = 25.0
    
    # Equipment component
    equipment_cost: float
    equipment_percentage: float = 10.0
    
    # Overheads
    overhead_cost: float
    overhead_percentage: float = 5.0
    
    # Profit
    profit_cost: float
    profit_percentage: float = 10.0
    
    # Total
    total_rate: float = 0.0
    
    def calculate_total(self) -> float:
        """Calculate total rate"""
        direct_cost = self.material_cost + self.labor_cost + self.equipment_cost
        self.overhead_cost = direct_cost * (self.overhead_percentage / 100)
        base_cost = direct_cost + self.overhead_cost
        self.profit_cost = base_cost * (self.profit_percentage / 100)
        self.total_rate = base_cost + self.profit_cost
        return self.total_rate

class RateAnalyzer:
    """
    Performs detailed rate analysis per CPWD norms
    """
    
    def __init__(self, dsr_parser=None):
        """
        Initialize with DSR parser for base rates
        """
        self.dsr_parser = dsr_parser
        
        # Standard labor rates (₹ per day) - 2024-25 typical
        self.labor_rates = {
            'skilled_1st': 850,
            'skilled_2nd': 700,
            'unskilled': 550
        }
        
        # Standard material rates (₹)
        self.material_rates = {
            'cement_50kg': 400,
            'sand_cum': 1200,
            'aggregate_20mm_cum': 1400,
            'aggregate_40mm_cum': 1350,
            'steel_fe500_kg': 58,
            'brick_modular_1000': 5500,
            'tile_ceramic_sqm': 450,
            'paint_emulsion_ltr': 180
        }
        
        # Equipment rental rates (₹ per day)
        self.equipment_rates = {
            'concrete_mixer': 800,
            'vibrator': 500,
            'excavator': 5000,
            'truck_10ton': 3500
        }
    
    def analyze_concrete_rate(self, grade: str, dsr_base_rate: float = None) -> RateAnalysis:
        """
        Detailed rate analysis for concrete
        
        Args:
            grade: M15, M20, M25, M30, etc.
            dsr_base_rate: DSR rate if available
        
        Returns:
            Complete rate analysis
        """
        # Material quantities for 1 Cum concrete (typical)
        material_qty = {
            'M15': {'cement_bags': 5.5, 'sand_cum': 0.45, 'aggregate_cum': 0.9},
            'M20': {'cement_bags': 6.5, 'sand_cum': 0.42, 'aggregate_cum': 0.84},
            'M25': {'cement_bags': 7.5, 'sand_cum': 0.40, 'aggregate_cum': 0.80},
            'M30': {'cement_bags': 8.5, 'sand_cum': 0.38, 'aggregate_cum': 0.76}
        }.get(grade, {'cement_bags': 6.5, 'sand_cum': 0.42, 'aggregate_cum': 0.84})
        
        # Calculate material cost
        cement_cost = material_qty['cement_bags'] * self.material_rates['cement_50kg']
        sand_cost = material_qty['sand_cum'] * self.material_rates['sand_cum']
        aggregate_cost = material_qty['aggregate_cum'] * self.material_rates['aggregate_20mm_cum']
        material_cost = cement_cost + sand_cost + aggregate_cost
        
        # Labor cost (assumed 1 Cum takes 0.75 man-days total)
        labor_cost = (0.3 * self.labor_rates['skilled_2nd'] + 
                     0.45 * self.labor_rates['unskilled'])
        
        # Equipment cost (mixer + vibrator for 1 Cum)
        equipment_cost = (self.equipment_rates['concrete_mixer'] * 0.1 + 
                         self.equipment_rates['vibrator'] * 0.05)
        
        analysis = RateAnalysis(
            item_description=f"RCC {grade} grade concrete",
            unit='Cum',
            material_cost=round(material_cost, 2),
            labor_cost=round(labor_cost, 2),
            equipment_cost=round(equipment_cost, 2),
            overhead_cost=0,  # Calculated by calculate_total()
            profit_cost=0
        )
        
        analysis.calculate_total()
        
        # If DSR rate provided, compare
        if dsr_base_rate:
            variance = ((analysis.total_rate - dsr_base_rate) / dsr_base_rate) * 100
            analysis.dsr_comparison = f"DSR Rate: ₹{dsr_base_rate}, Variance: {variance:+.1f}%"
        
        return analysis
    
    def analyze_earthwork_rate(self, soil_type: str = 'ordinary', 
                               depth_range: str = 'up to 1.5m') -> RateAnalysis:
        """Rate analysis for earthwork excavation"""
        
        # Labor requirements (man-days per Cum)
        labor_requirement = {
            ('ordinary', 'up to 1.5m'): {'skilled': 0.05, 'unskilled': 0.30},
            ('ordinary', '1.5m to 3.0m'): {'skilled': 0.05, 'unskilled': 0.40},
            ('hard', 'up to 1.5m'): {'skilled': 0.08, 'unskilled': 0.50},
            ('rock', 'up to 1.5m'): {'skilled': 0.10, 'unskilled': 0.70}
        }.get((soil_type, depth_range), {'skilled': 0.05, 'unskilled': 0.30})
        
        # Calculate costs
        material_cost = 10.0  # Negligible - just tools wear
        
        labor_cost = (labor_requirement['skilled'] * self.labor_rates['skilled_2nd'] +
                     labor_requirement['unskilled'] * self.labor_rates['unskilled'])
        
        # Equipment (excavator for hard/rock soil)
        equipment_cost = 0
        if soil_type in ['hard', 'rock']:
            equipment_cost = self.equipment_rates['excavator'] * 0.02  # 0.02 days per Cum
        
        analysis = RateAnalysis(
            item_description=f"Earthwork excavation in {soil_type} soil, {depth_range}",
            unit='Cum',
            material_cost=material_cost,
            labor_cost=round(labor_cost, 2),
            equipment_cost=round(equipment_cost, 2),
            overhead_cost=0,
            profit_cost=0
        )
        
        analysis.calculate_total()
        return analysis
    
    def analyze_brickwork_rate(self, mortar_ratio: str = '1:6') -> RateAnalysis:
        """Rate analysis for brick masonry"""
        
        # Material for 1 Cum brickwork
        bricks_required = 500  # Modular bricks per Cum
        mortar_cum = 0.25  # Mortar volume per Cum brickwork
        
        # Mortar composition
        mortar_cement_bags = {'1:4': 2.8, '1:5': 2.3, '1:6': 1.9}.get(mortar_ratio, 1.9)
        mortar_sand_cum = 0.25
        
        # Calculate material cost
        brick_cost = (bricks_required / 1000) * self.material_rates['brick_modular_1000']
        cement_cost = mortar_cement_bags * self.material_rates['cement_50kg']
        sand_cost = mortar_sand_cum * self.material_rates['sand_cum']
        material_cost = brick_cost + cement_cost + sand_cost
        
        # Labor (mason + helper for 1 Cum)
        labor_cost = (0.6 * self.labor_rates['skilled_2nd'] +
                     0.8 * self.labor_rates['unskilled'])
        
        # Minimal equipment
        equipment_cost = 25.0
        
        analysis = RateAnalysis(
            item_description=f"Brick masonry in CM {mortar_ratio}",
            unit='Cum',
            material_cost=round(material_cost, 2),
            labor_cost=round(labor_cost, 2),
            equipment_cost=equipment_cost,
            overhead_cost=0,
            profit_cost=0
        )
        
        analysis.calculate_total()
        return analysis
    
    def create_rate_analysis_report(self, analyses: List[RateAnalysis]) -> pd.DataFrame:
        """
        Create comprehensive rate analysis report
        
        Returns:
            DataFrame with all rate components
        """
        report_data = []
        
        for analysis in analyses:
            report_data.append({
                'Item Description': analysis.item_description,
                'Unit': analysis.unit,
                'Material (₹)': f"{analysis.material_cost:.2f}",
                'Material %': f"{analysis.material_percentage}%",
                'Labor (₹)': f"{analysis.labor_cost:.2f}",
                'Labor %': f"{analysis.labor_percentage}%",
                'Equipment (₹)': f"{analysis.equipment_cost:.2f}",
                'Equipment %': f"{analysis.equipment_percentage}%",
                'Overheads (₹)': f"{analysis.overhead_cost:.2f}",
                'Overheads %': f"{analysis.overhead_percentage}%",
                'Profit (₹)': f"{analysis.profit_cost:.2f}",
                'Profit %': f"{analysis.profit_percentage}%",
                'Total Rate (₹)': f"{analysis.total_rate:.2f}"
            })
        
        return pd.DataFrame(report_data)
    
    def calculate_contingency(self, base_cost: float, project_duration_months: int,
                             risk_level: str = 'medium') -> Dict:
        """
        Calculate contingency provisions per CPWD norms
        
        Args:
            base_cost: Base project cost
            project_duration_months: Duration
            risk_level: 'low', 'medium', 'high'
        
        Returns:
            Dict with contingency breakdown
        """
        # Standard contingency rates
        contingency_rate = {
            'low': 0.03,      # 3%
            'medium': 0.04,   # 4%
            'high': 0.05      # 5%
        }.get(risk_level, 0.04)
        
        contingency = base_cost * contingency_rate
        
        # Work charged establishment (1.5-2%)
        wce = base_cost * 0.015
        
        # Tools and plant (1-1.5%)
        tools_plant = base_cost * 0.01
        
        # Water/Electricity (8% each for lump sum)
        water_charges = base_cost * 0.08
        electricity_charges = base_cost * 0.08
        
        # Escalation (if project > 12 months)
        escalation = 0
        if project_duration_months > 12:
            excess_months = project_duration_months - 12
            escalation = base_cost * 0.05 * (excess_months / 12)  # 5% per year
        
        return {
            'base_cost': base_cost,
            'contingency': contingency,
            'contingency_rate': contingency_rate,
            'work_charged_establishment': wce,
            'tools_plant': tools_plant,
            'water_charges': water_charges,
            'electricity_charges': electricity_charges,
            'escalation': escalation,
            'total_provisions': sum([contingency, wce, tools_plant, water_charges, 
                                    electricity_charges, escalation]),
            'total_project_cost': base_cost + sum([contingency, wce, tools_plant, 
                                                   water_charges, electricity_charges, escalation])
        }

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    analyzer = RateAnalyzer()
    
    # Analyze concrete
    m25_analysis = analyzer.analyze_concrete_rate('M25', dsr_base_rate=7650)
    print("🏗️ M25 Concrete Rate Analysis:")
    print(f"   Material: ₹{m25_analysis.material_cost}")
    print(f"   Labor: ₹{m25_analysis.labor_cost}")
    print(f"   Equipment: ₹{m25_analysis.equipment_cost}")
    print(f"   Overheads: ₹{m25_analysis.overhead_cost}")
    print(f"   Profit: ₹{m25_analysis.profit_cost}")
    print(f"   TOTAL: ₹{m25_analysis.total_rate}/Cum\n")
    
    # Contingency calculation
    contingency = analyzer.calculate_contingency(
        base_cost=5000000,  # ₹50 lakhs
        project_duration_months=18,
        risk_level='medium'
    )
    
    print("💰 Project Cost Breakdown:")
    print(f"   Base Cost: ₹{contingency['base_cost']:,.2f}")
    print(f"   Contingency (4%): ₹{contingency['contingency']:,.2f}")
    print(f"   WCE: ₹{contingency['work_charged_establishment']:,.2f}")
    print(f"   Escalation: ₹{contingency['escalation']:,.2f}")
    print(f"   TOTAL: ₹{contingency['total_project_cost']:,.2f}")
