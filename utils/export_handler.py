"""
Export Handler Module
Handles exporting medical reports to various formats (PDF, Text)
"""

import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class ExportHandler:
    """Handle export of medical reports to various formats"""
    
    def __init__(self):
        """Initialize export handler"""
        self.config = Config
        
    def export_to_pdf(
        self,
        report_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> io.BytesIO:
        """
        Export medical report to PDF format
        
        Args:
            report_data: Dictionary containing report information
            filename: Optional filename for the PDF
            
        Returns:
            BytesIO object containing PDF data
        """
        try:
            logger.info("Generating PDF export")
            
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Container for PDF elements
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E88E5'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1E88E5'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            title = Paragraph("Medical Report Summary", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Generation timestamp
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            timestamp_text = Paragraph(f"<i>Generated: {timestamp}</i>", styles['Normal'])
            elements.append(timestamp_text)
            elements.append(Spacer(1, 0.3*inch))
            
            # Patient Information
            if report_data.get('patient_info'):
                elements.append(Paragraph("Patient Information", heading_style))
                patient_info = report_data['patient_info']
                
                patient_data = []
                if patient_info.get('name'):
                    patient_data.append(['Name:', patient_info['name']])
                if patient_info.get('age'):
                    patient_data.append(['Age:', str(patient_info['age'])])
                if patient_info.get('gender'):
                    patient_data.append(['Gender:', patient_info['gender']])
                if patient_info.get('date'):
                    patient_data.append(['Report Date:', patient_info['date']])
                
                if patient_data:
                    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
                    patient_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                    ]))
                    elements.append(patient_table)
                    elements.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            if report_data.get('summary'):
                elements.append(Paragraph("Executive Summary", heading_style))
                summary_text = Paragraph(report_data['summary'][:500], styles['BodyText'])
                elements.append(summary_text)
                elements.append(Spacer(1, 0.2*inch))
            
            # Abnormal Values
            if report_data.get('abnormal_values'):
                elements.append(Paragraph("Abnormal Values", heading_style))
                
                abnormal_data = [['Test Name', 'Value', 'Normal Range', 'Severity']]
                for value in report_data['abnormal_values'][:10]:  # Limit to 10
                    abnormal_data.append([
                        value.get('test_name', 'N/A'),
                        f"{value.get('value', 'N/A')} {value.get('unit', '')}",
                        value.get('normal_range', 'N/A'),
                        value.get('severity', 'N/A')
                    ])
                
                abnormal_table = Table(abnormal_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                abnormal_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E53935')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(abnormal_table)
                elements.append(Spacer(1, 0.3*inch))
            
            # Risk Assessment
            if report_data.get('risk_assessment'):
                elements.append(Paragraph("Risk Assessment", heading_style))
                risk_text = Paragraph(report_data['risk_assessment'], styles['BodyText'])
                elements.append(risk_text)
                elements.append(Spacer(1, 0.2*inch))
            
            # Health Insights
            if report_data.get('health_insights'):
                elements.append(Paragraph("Health Insights & Recommendations", heading_style))
                insights_text = Paragraph(report_data['health_insights'], styles['BodyText'])
                elements.append(insights_text)
                elements.append(Spacer(1, 0.2*inch))
            
            # Disclaimer
            elements.append(Spacer(1, 0.3*inch))
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_JUSTIFY
            )
            disclaimer = Paragraph(
                "<b>Disclaimer:</b> This report is generated by an AI system for informational purposes only. "
                "It is not a substitute for professional medical advice, diagnosis, or treatment. "
                "Always seek the advice of your physician or other qualified health provider with any questions "
                "you may have regarding a medical condition.",
                disclaimer_style
            )
            elements.append(disclaimer)
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF data
            buffer.seek(0)
            logger.info("PDF export completed successfully")
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def export_to_text(
        self,
        report_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Export medical report to plain text format
        
        Args:
            report_data: Dictionary containing report information
            filename: Optional filename for the text file
            
        Returns:
            String containing formatted text report
        """
        try:
            logger.info("Generating text export")
            
            lines = []
            lines.append("=" * 80)
            lines.append("MEDICAL REPORT SUMMARY")
            lines.append("=" * 80)
            lines.append("")
            
            # Timestamp
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            lines.append(f"Generated: {timestamp}")
            lines.append("")
            
            # Patient Information
            if report_data.get('patient_info'):
                lines.append("-" * 80)
                lines.append("PATIENT INFORMATION")
                lines.append("-" * 80)
                patient_info = report_data['patient_info']
                
                if patient_info.get('name'):
                    lines.append(f"Name: {patient_info['name']}")
                if patient_info.get('age'):
                    lines.append(f"Age: {patient_info['age']}")
                if patient_info.get('gender'):
                    lines.append(f"Gender: {patient_info['gender']}")
                if patient_info.get('date'):
                    lines.append(f"Report Date: {patient_info['date']}")
                lines.append("")
            
            # Executive Summary
            if report_data.get('summary'):
                lines.append("-" * 80)
                lines.append("EXECUTIVE SUMMARY")
                lines.append("-" * 80)
                lines.append(report_data['summary'])
                lines.append("")
            
            # Abnormal Values
            if report_data.get('abnormal_values'):
                lines.append("-" * 80)
                lines.append("ABNORMAL VALUES")
                lines.append("-" * 80)
                
                for value in report_data['abnormal_values']:
                    lines.append(f"\n• {value.get('test_name', 'N/A')}")
                    lines.append(f"  Value: {value.get('value', 'N/A')} {value.get('unit', '')}")
                    lines.append(f"  Normal Range: {value.get('normal_range', 'N/A')}")
                    lines.append(f"  Severity: {value.get('severity', 'N/A')}")
                lines.append("")
            
            # Risk Assessment
            if report_data.get('risk_assessment'):
                lines.append("-" * 80)
                lines.append("RISK ASSESSMENT")
                lines.append("-" * 80)
                lines.append(report_data['risk_assessment'])
                lines.append("")
            
            # Health Insights
            if report_data.get('health_insights'):
                lines.append("-" * 80)
                lines.append("HEALTH INSIGHTS & RECOMMENDATIONS")
                lines.append("-" * 80)
                lines.append(report_data['health_insights'])
                lines.append("")
            
            # Disclaimer
            lines.append("-" * 80)
            lines.append("DISCLAIMER")
            lines.append("-" * 80)
            lines.append(
                "This report is generated by an AI system for informational purposes only. "
                "It is not a substitute for professional medical advice, diagnosis, or treatment. "
                "Always seek the advice of your physician or other qualified health provider."
            )
            lines.append("")
            lines.append("=" * 80)
            
            text_content = "\n".join(lines)
            logger.info("Text export completed successfully")
            return text_content
            
        except Exception as e:
            logger.error(f"Error generating text export: {str(e)}")
            raise
    
    def generate_filename(self, format_type: str = "pdf") -> str:
        """
        Generate filename with timestamp
        
        Args:
            format_type: File format (pdf or txt)
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"medical_report_{timestamp}.{format_type}"

# Made with Bob
