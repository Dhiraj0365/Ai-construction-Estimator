# 🔥 DRAWING INTELLIGENCE ENGINE v3.0 - CPWD Ready
import ezdxf
import streamlit as st
from typing import Dict, List

class AutoCADDrawingScanner:
    def __init__(self):
        self.components = []
    
    def analyze_dwg(self, uploaded_file):
        """Main analysis function"""
        try:
            doc = ezdxf.readfile(uploaded_file)
            msp = doc.modelspace()
            
            # Extract key components
            slabs = self.extract_slabs(msp)
            columns = self.extract_columns(msp)
            
            st.success(f"✅ Found {len(slabs)} slabs, {len(columns)} columns")
            
            return {
                'slabs': slabs,
                'columns': columns,
                'total_volume': sum(s['volume'] for s in slabs)
            }
        except:
            st.error("❌ DWG parsing failed")
            return {}
    
    def extract_slabs(self, msp):
        slabs = []
        for entity in msp.query('LWPOLYLINE[layer=="SLAB*"]'):
            # Calculate slab volume (150mm thick)
            area = entity.get_area()
            slabs.append({
                'dsr_code': '13.4.1',
                'area_sqm': area,
                'volume_cum': area * 0.15,
                'rate': 8927
            })
        return slabs
