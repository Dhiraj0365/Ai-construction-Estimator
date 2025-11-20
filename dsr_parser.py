"""
dsr_parser.py
PDF Parser for CPWD Delhi Schedule of Rates
Extracts rates from DSR Vol 1 & 2 PDFs
"""

import pdfplumber
import pandas as pd
import re
from typing import Dict, List, Optional

class DSRParser:
    """
    Parses CPWD DSR PDFs and extracts rate information
    Handles DSR 2024-25 format
    """
    
    def __init__(self, dsr_vol1_path: str = None, dsr_vol2_path: str = None):
        """
        Initialize with paths to DSR PDF files
        
        Args:
            dsr_vol1_path: Path to DSR Vol 1 (Civil Works)
            dsr_vol2_path: Path to DSR Vol 2 (Electrical/Mechanical)
        """
        self.dsr_vol1_path = dsr_vol1_path
        self.dsr_vol2_path = dsr_vol2_path
        self.rates_df = None
        
    def parse_dsr_pdf(self, pdf_path: str, volume: str = 'Vol1') -> pd.DataFrame:
        """
        Extract rates from DSR PDF
        
        Returns:
            DataFrame with columns: item_code, description, unit, rate, volume
        """
        if not pdf_path:
            print("⚠️ DSR path not provided. Using fallback rates.")
            return self._get_fallback_rates()
        
        try:
            rates_data = []
            
            with pdfplumber.open(pdf_path) as pdf:
                print(f"📄 Parsing {volume}: {len(pdf.pages)} pages...")
                
                for page_num, page in enumerate(pdf.pages[:50], 1):  # First 50 pages
                    text = page.extract_text()
                    
                    if not text:
                        continue
                    
                    # Parse line by line for rate entries
                    lines = text.split('\n')
                    
                    for line in lines:
                        # Match pattern: DSR code, description, unit, rate
                        # Example: "4.1.6  PCC 1:4:8  Cum  5546.17"
                        rate_match = re.search(
                            r'(\d+\.\d+\.?\d*)\s+(.+?)\s+(Cum|Sqm|Rmt|Kg|Each|LS|cum|sqm)\s+([\d,]+\.?\d*)',
                            line
                        )
                        
                        if rate_match:
                            item_code = rate_match.group(1)
                            description = rate_match.group(2).strip()
                            unit = rate_match.group(3).capitalize()
                            if unit == 'Cum': unit = 'Cum'  # Standardize
                            if unit == 'Sqm': unit = 'Sqm'
                            rate_str = rate_match.group(4).replace(',', '')
                            
                            try:
                                rate = float(rate_str)
                                rates_data.append({
                                    'item_code': item_code,
                                    'description': description,
                                    'unit': unit,
                                    'rate': rate,
                                    'volume': volume
                                })
                            except ValueError:
                                continue
                
                print(f"✅ Extracted {len(rates_data)} rate entries from {volume}")
            
            if len(rates_data) == 0:
                print("⚠️ No rates extracted. Using fallback.")
                return self._get_fallback_rates()
            
            return pd.DataFrame(rates_data)
        
        except Exception as e:
            print(f"❌ Error parsing DSR: {e}")
            print("📊 Using fallback rates database")
            return self._get_fallback_rates()
    
    def _get_fallback_rates(self) -> pd.DataFrame:
        """
        Fallback rate database based on CPWD DSR 2024-25 approximate rates
        Use when PDF parsing fails
        """
        fallback_data = [
            # EARTHWORK
            {'item_code': '2.1', 'description': 'Earthwork excavation in ordinary soil up to 1.5m', 
             'unit': 'Cum', 'rate': 158.16, 'category': 'Earthwork'},
            {'item_code': '2.2', 'description': 'Earthwork excavation in hard soil up to 1.5m', 
             'unit': 'Cum', 'rate': 225.00, 'category': 'Earthwork'},
            {'item_code': '2.3', 'description': 'Earthwork in filling and compaction', 
             'unit': 'Cum', 'rate': 192.31, 'category': 'Earthwork'},
            
            # CONCRETE WORKS - PCC
            {'item_code': '4.1.1', 'description': 'PCC 1:5:10 using 40mm aggregate', 
             'unit': 'Cum', 'rate': 4850.00, 'category': 'PCC'},
            {'item_code': '4.1.6', 'description': 'PCC 1:3:6 using 20mm aggregate', 
             'unit': 'Cum', 'rate': 5546.17, 'category': 'PCC'},
            
            # CONCRETE WORKS - RCC
            {'item_code': '4.3', 'description': 'RCC M20 grade using 20mm aggregate', 
             'unit': 'Cum', 'rate': 7200.00, 'category': 'RCC'},
            {'item_code': '4.4', 'description': 'RCC M25 grade using 20mm aggregate', 
             'unit': 'Cum', 'rate': 7650.00, 'category': 'RCC'},
            {'item_code': '4.5', 'description': 'RCC M30 grade using 20mm aggregate', 
             'unit': 'Cum', 'rate': 8100.00, 'category': 'RCC'},
            
            # FORMWORK
            {'item_code': '5.9', 'description': 'Centering shuttering for slabs including removal', 
             'unit': 'Sqm', 'rate': 520.00, 'category': 'Formwork'},
            {'item_code': '5.10', 'description': 'Centering shuttering for beams including removal', 
             'unit': 'Sqm', 'rate': 597.62, 'category': 'Formwork'},
            {'item_code': '5.11', 'description': 'Centering shuttering for columns including removal', 
             'unit': 'Sqm', 'rate': 580.00, 'category': 'Formwork'},
            
            # REINFORCEMENT
            {'item_code': '8.1', 'description': 'TMT bars Fe500 including cutting, bending, binding', 
             'unit': 'Kg', 'rate': 68.50, 'category': 'Steel'},
            {'item_code': '8.2', 'description': 'TMT bars Fe500D including cutting, bending, binding', 
             'unit': 'Kg', 'rate': 71.20, 'category': 'Steel'},
            
            # BRICKWORK
            {'item_code': '7.1', 'description': 'Brick masonry in CM 1:6 modular bricks', 
             'unit': 'Cum', 'rate': 5200.00, 'category': 'Masonry'},
            {'item_code': '7.2', 'description': 'Brick masonry in CM 1:4 modular bricks', 
             'unit': 'Cum', 'rate': 5450.00, 'category': 'Masonry'},
            
            # PLASTERING
            {'item_code': '13.1', 'description': 'Cement plaster 12mm thick in CM 1:4', 
             'unit': 'Sqm', 'rate': 285.00, 'category': 'Finishing'},
            {'item_code': '13.2', 'description': 'Cement plaster 18mm thick in CM 1:4', 
             'unit': 'Sqm', 'rate': 380.00, 'category': 'Finishing'},
            
            # FLOORING
            {'item_code': '14.1', 'description': 'Ceramic tile flooring 600x600mm', 
             'unit': 'Sqm', 'rate': 1150.00, 'category': 'Finishing'},
            {'item_code': '14.2', 'description': 'Vitrified tile flooring 600x600mm', 
             'unit': 'Sqm', 'rate': 1280.00, 'category': 'Finishing'},
            {'item_code': '14.3', 'description': 'Marble flooring 600x600mm', 
             'unit': 'Sqm', 'rate': 2150.00, 'category': 'Finishing'},
            
            # WATERPROOFING
            {'item_code': '15.1', 'description': 'Waterproofing treatment 2 coats', 
             'unit': 'Sqm', 'rate': 420.00, 'category': 'Finishing'},
            
            # PAINTING
            {'item_code': '13.5', 'description': 'Cement paint 2 coats on walls', 
             'unit': 'Sqm', 'rate': 85.00, 'category': 'Finishing'},
            {'item_code': '13.6', 'description': 'Acrylic emulsion paint 2 coats', 
             'unit': 'Sqm', 'rate': 125.00, 'category': 'Finishing'},
            
            # MISCELLANEOUS
            {'item_code': '1.1', 'description': 'Carriage of materials by truck per km', 
             'unit': 'Cum', 'rate': 35.00, 'category': 'Transport'},
        ]
        
        df = pd.DataFrame(fallback_data)
        print(f"📊 Loaded {len(df)} fallback rates (CPWD DSR 2024-25 approximate)")
        return df
    
    def load_all_rates(self) -> pd.DataFrame:
        """
        Load rates from all DSR volumes and combine
        """
        all_rates = []
        
        if self.dsr_vol1_path:
            vol1_rates = self.parse_dsr_pdf(self.dsr_vol1_path, 'Vol1')
            all_rates.append(vol1_rates)
        
        if self.dsr_vol2_path:
            vol2_rates = self.parse_dsr_pdf(self.dsr_vol2_path, 'Vol2')
            all_rates.append(vol2_rates)
        
        # If no PDFs provided, use fallback
        if len(all_rates) == 0:
            all_rates.append(self._get_fallback_rates())
        
        self.rates_df = pd.concat(all_rates, ignore_index=True)
        return self.rates_df
    
    def search_rate(self, keyword: str, unit: str = None) -> pd.DataFrame:
        """
        Search for rates by keyword
        
        Args:
            keyword: Search term (e.g., 'excavation', 'RCC', 'brick')
            unit: Filter by unit (optional)
        
        Returns:
            DataFrame of matching rates
        """
        if self.rates_df is None:
            self.load_all_rates()
        
        # Case-insensitive search
        mask = self.rates_df['description'].str.contains(keyword, case=False, na=False)
        
        if unit:
            mask = mask & (self.rates_df['unit'] == unit)
        
        results = self.rates_df[mask]
        return results
    
    def get_rate_by_code(self, item_code: str) -> Optional[float]:
        """Get rate by DSR item code"""
        if self.rates_df is None:
            self.load_all_rates()
        
        match = self.rates_df[self.rates_df['item_code'] == item_code]
        
        if len(match) > 0:
            return float(match.iloc[0]['rate'])
        return None
    
    def export_rates_csv(self, filename: str = 'dsr_rates_cache.csv'):
        """Export extracted rates to CSV for caching"""
        if self.rates_df is not None:
            self.rates_df.to_csv(filename, index=False)
            print(f"✅ Rates exported to {filename}")

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Option 1: With DSR PDFs
    # parser = DSRParser(
    #     dsr_vol1_path='/content/drive/MyDrive/DSR_Vol_1_Civil.pdf',
    #     dsr_vol2_path='/content/drive/MyDrive/DSR_Vol_2_Civil.pdf'
    # )
    
    # Option 2: Without PDFs (fallback rates)
    parser = DSRParser()
    
    # Load all rates
    rates_df = parser.load_all_rates()
    print(f"\n📊 Total rates loaded: {len(rates_df)}")
    print(rates_df.head(10))
    
    # Search example
    print("\n🔍 Searching for 'RCC' rates:")
    rcc_rates = parser.search_rate('RCC', unit='Cum')
    print(rcc_rates)
    
    # Get specific rate
    rate = parser.get_rate_by_code('4.4')
    print(f"\n💰 Rate for item 4.4: ₹{rate}")
