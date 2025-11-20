"""
boq_generator.py
Bill of Quantities Generator with WBS and Excel/PDF export
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class BOQGenerator:
    """
    Generates government-compliant BOQ with WBS structure
    """
    
    def __init__(self, project_name: str, project_location: str):
        self.project_name = project_name
        self.project_location = project_location
        self.boq_items = []
        self.wbs_structure = {}
        
    def add_boq_item(self, item_no: str, description: str, unit: str,
                     quantity: float, rate: float, wbs_level1: str,
                     wbs_level2: str = '', is_reference: str = ''):
        """Add item to BOQ"""
        amount = quantity * rate
        
        self.boq_items.append({
            'Item No': item_no,
            'Description': description,
            'IS Reference': is_reference,
            'Unit': unit,
            'Quantity': round(quantity, 3),
            'Rate (₹)': round(rate, 2),
            'Amount (₹)': round(amount, 2),
            'WBS_L1': wbs_level1,
            'WBS_L2': wbs_level2
        })
    
    def generate_boq_dataframe(self) -> pd.DataFrame:
        """Generate BOQ as pandas DataFrame"""
        df = pd.DataFrame(self.boq_items)
        
        # Calculate subtotals by WBS Level 1
        df_display = df[['Item No', 'Description', 'IS Reference', 'Unit', 
                        'Quantity', 'Rate (₹)', 'Amount (₹)']].copy()
        
        return df_display
    
    def export_to_excel(self, filename: str):
        """Export BOQ to Excel with formatting"""
        df = pd.DataFrame(self.boq_items)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet 1: BOQ Summary
            df_boq = df[['Item No', 'Description', 'IS Reference', 'Unit', 
                        'Quantity', 'Rate (₹)', 'Amount (₹)']].copy()
            df_boq.to_excel(writer, sheet_name='BOQ', index=False)
            
            # Sheet 2: WBS Breakdown
            wbs_summary = df.groupby(['WBS_L1', 'WBS_L2']).agg({
                'Amount (₹)': 'sum'
            }).reset_index()
            wbs_summary.to_excel(writer, sheet_name='WBS_Breakdown', index=False)
            
            # Sheet 3: Cost Abstract
            abstract = df.groupby('WBS_L1').agg({
                'Amount (₹)': 'sum'
            }).reset_index()
            abstract.columns = ['Work Category', 'Amount (₹)']
            abstract.to_excel(writer, sheet_name='Cost_Abstract', index=False)
            
            # Format BOQ sheet
            workbook = writer.book
            worksheet = workbook['BOQ']
            
            # Header formatting
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF')
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Add title rows
            worksheet.insert_rows(1, 3)
            worksheet['A1'] = f"BILL OF QUANTITIES - {self.project_name}"
            worksheet['A1'].font = Font(bold=True, size=14)
            worksheet['A2'] = f"Location: {self.project_location}"
            worksheet['A3'] = f"Date: {datetime.now().strftime('%d-%m-%Y')}"
        
        print(f"✅ BOQ exported to {filename}")
    
    def calculate_totals(self) -> Dict:
        """Calculate project totals and abstracts"""
        df = pd.DataFrame(self.boq_items)
        
        total_cost = df['Amount (₹)'].sum()
        
        # WBS totals
        wbs_totals = df.groupby('WBS_L1')['Amount (₹)'].sum().to_dict()
        
        return {
            'total_cost': total_cost,
            'wbs_totals': wbs_totals,
            'item_count': len(self.boq_items)
        }

# ============================================================================
# Usage example in comment
# ============================================================================
