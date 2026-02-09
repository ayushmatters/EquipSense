"""
PDF Report Generator Service

This module generates professional PDF reports using ReportLab.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
from datetime import datetime
from typing import Dict, List
import os


class PDFReportGenerator:
    """
    Service class for generating PDF reports with equipment data and analytics.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
    
    def _create_header(self, dataset_info: Dict) -> List:
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph("Chemical Equipment Parameter Report", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Dataset Information
        info_data = [
            ['Dataset:', dataset_info.get('filename', 'N/A')],
            ['Uploaded By:', dataset_info.get('uploaded_by', 'N/A')],
            ['Upload Date:', dataset_info.get('uploaded_at', 'N/A')],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_summary_section(self, statistics: Dict) -> List:
        """Create summary statistics section"""
        elements = []
        
        # Section Header
        header = Paragraph("Summary Statistics", self.heading_style)
        elements.append(header)
        
        # Statistics Table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Equipment', str(statistics.get('total_equipment', 0))],
            ['Average Flowrate', f"{statistics.get('avg_flowrate', 0):.2f}"],
            ['Average Pressure', f"{statistics.get('avg_pressure', 0):.2f}"],
            ['Average Temperature', f"{statistics.get('avg_temperature', 0):.2f}"],
            ['Max Flowrate', f"{statistics.get('max_flowrate', 0):.2f}"],
            ['Min Flowrate', f"{statistics.get('min_flowrate', 0):.2f}"],
            ['Max Pressure', f"{statistics.get('max_pressure', 0):.2f}"],
            ['Min Pressure', f"{statistics.get('min_pressure', 0):.2f}"],
            ['Max Temperature', f"{statistics.get('max_temperature', 0):.2f}"],
            ['Min Temperature', f"{statistics.get('min_temperature', 0):.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_type_distribution_section(self, type_distribution: Dict) -> List:
        """Create equipment type distribution section"""
        elements = []
        
        # Section Header
        header = Paragraph("Equipment Type Distribution", self.heading_style)
        elements.append(header)
        
        # Type Distribution Table
        type_data = [['Equipment Type', 'Count', 'Percentage']]
        total = sum(type_distribution.values())
        
        for equip_type, count in sorted(type_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            type_data.append([equip_type, str(count), f"{percentage:.1f}%"])
        
        type_table = Table(type_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(type_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_equipment_list_section(self, equipment_list: List[Dict]) -> List:
        """Create detailed equipment listing section"""
        elements = []
        
        # Section Header
        header = Paragraph("Equipment Details", self.heading_style)
        elements.append(header)
        
        # Equipment Table
        equip_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
        
        for equipment in equipment_list[:50]:  # Limit to first 50 for PDF size
            equip_data.append([
                str(equipment.get('Equipment Name', 'N/A'))[:30],  # Truncate long names
                str(equipment.get('Type', 'N/A'))[:20],
                f"{equipment.get('Flowrate', 0):.2f}",
                f"{equipment.get('Pressure', 0):.2f}",
                f"{equipment.get('Temperature', 0):.2f}"
            ])
        
        if len(equipment_list) > 50:
            equip_data.append(['...', f'(Showing 50 of {len(equipment_list)} items)', '', '', ''])
        
        equip_table = Table(equip_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        equip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        elements.append(equip_table)
        
        return elements
    
    def generate_report(self, summary_data: Dict) -> BytesIO:
        """
        Generate PDF report from summary data.
        
        Args:
            summary_data: Dictionary containing dataset summary
            
        Returns:
            BytesIO object containing PDF data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        
        # Add sections
        elements.extend(self._create_header(summary_data.get('dataset_info', {})))
        elements.extend(self._create_summary_section(summary_data.get('statistics', {})))
        elements.extend(self._create_type_distribution_section(summary_data.get('type_distribution', {})))
        elements.append(PageBreak())
        elements.extend(self._create_equipment_list_section(summary_data.get('equipment_list', [])))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
