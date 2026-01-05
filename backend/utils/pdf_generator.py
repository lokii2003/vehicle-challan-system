"""
PDF Generator Module for Vehicle Challan System

This module provides functionality to generate PDF documents for challans and receipts
with customizable formatting, styling, and data embedding.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from io import BytesIO
import json

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        PageBreak, Image, KeepTogether
    )
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFGenerator:
    """
    A comprehensive PDF generation class for creating challans and receipts
    with professional formatting and layout.
    """

    # Configuration constants
    DEFAULT_PAGE_SIZE = A4
    MARGIN = 0.5 * inch
    CONTENT_WIDTH = DEFAULT_PAGE_SIZE[0] - (2 * MARGIN)
    
    # Color scheme
    HEADER_COLOR = HexColor("#1f4788")
    ACCENT_COLOR = HexColor("#e74c3c")
    TABLE_HEADER_COLOR = HexColor("#34495e")
    TABLE_ROW_COLOR = HexColor("#ecf0f1")
    TEXT_COLOR = HexColor("#2c3e50")

    def __init__(self, title: str = "Vehicle Challan System", logo_path: Optional[str] = None):
        """
        Initialize the PDF Generator.
        
        Args:
            title: Document title/header
            logo_path: Path to logo image file (optional)
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab library is required. Install it with: pip install reportlab")
        
        self.title = title
        self.logo_path = logo_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the document."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=self.HEADER_COLOR,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.HEADER_COLOR,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_COLOR,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_COLOR,
            spaceAfter=8
        ))

    def generate_challan_pdf(
        self,
        challan_data: Dict,
        output_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generate a PDF for a traffic challan.
        
        Args:
            challan_data: Dictionary containing challan information
            output_path: Path to save the PDF (optional, returns bytes if not specified)
            
        Returns:
            Bytes of PDF if output_path is None, else None
        """
        required_fields = [
            'challan_number', 'date', 'vehicle_number', 'owner_name',
            'violation_description', 'amount', 'location'
        ]
        
        if not all(field in challan_data for field in required_fields):
            raise ValueError(f"Missing required fields. Required: {required_fields}")

        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=self.DEFAULT_PAGE_SIZE,
                                   rightMargin=self.MARGIN, leftMargin=self.MARGIN,
                                   topMargin=self.MARGIN, bottomMargin=self.MARGIN)
        else:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=self.DEFAULT_PAGE_SIZE,
                                   rightMargin=self.MARGIN, leftMargin=self.MARGIN,
                                   topMargin=self.MARGIN, bottomMargin=self.MARGIN)

        story = []
        
        # Add header
        story.extend(self._create_challan_header())
        story.append(Spacer(1, 0.2 * inch))
        
        # Add challan details section
        story.extend(self._create_challan_details_section(challan_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Add vehicle information section
        story.extend(self._create_vehicle_info_section(challan_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Add violation details section
        story.extend(self._create_violation_section(challan_data))
        story.append(Spacer(1, 0.3 * inch))
        
        # Add amount and notes section
        story.extend(self._create_amount_section(challan_data))
        story.append(Spacer(1, 0.3 * inch))
        
        # Add signature section
        story.extend(self._create_signature_section())
        
        # Build PDF
        doc.build(story)
        
        if not output_path:
            buffer.seek(0)
            return buffer.getvalue()
        return None

    def generate_receipt_pdf(
        self,
        receipt_data: Dict,
        output_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generate a PDF receipt for challan payment.
        
        Args:
            receipt_data: Dictionary containing receipt information
            output_path: Path to save the PDF (optional, returns bytes if not specified)
            
        Returns:
            Bytes of PDF if output_path is None, else None
        """
        required_fields = [
            'receipt_number', 'challan_number', 'date', 'amount',
            'payment_method', 'vehicle_number', 'owner_name'
        ]
        
        if not all(field in receipt_data for field in required_fields):
            raise ValueError(f"Missing required fields. Required: {required_fields}")

        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=self.DEFAULT_PAGE_SIZE,
                                   rightMargin=self.MARGIN, leftMargin=self.MARGIN,
                                   topMargin=self.MARGIN, bottomMargin=self.MARGIN)
        else:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=self.DEFAULT_PAGE_SIZE,
                                   rightMargin=self.MARGIN, leftMargin=self.MARGIN,
                                   topMargin=self.MARGIN, bottomMargin=self.MARGIN)

        story = []
        
        # Add receipt header
        story.extend(self._create_receipt_header())
        story.append(Spacer(1, 0.2 * inch))
        
        # Add receipt details
        story.extend(self._create_receipt_details_section(receipt_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Add payment information
        story.extend(self._create_payment_info_section(receipt_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Add challan reference
        story.extend(self._create_challan_reference_section(receipt_data))
        story.append(Spacer(1, 0.3 * inch))
        
        # Add footer
        story.extend(self._create_receipt_footer())
        
        # Build PDF
        doc.build(story)
        
        if not output_path:
            buffer.seek(0)
            return buffer.getvalue()
        return None

    def _create_challan_header(self) -> List:
        """Create header section for challan."""
        return [
            Paragraph(self.title.upper(), self.styles['CustomTitle']),
            Paragraph("TRAFFIC VIOLATION CHALLAN", self.styles['SectionHeading']),
        ]

    def _create_receipt_header(self) -> List:
        """Create header section for receipt."""
        return [
            Paragraph(self.title.upper(), self.styles['CustomTitle']),
            Paragraph("PAYMENT RECEIPT", self.styles['SectionHeading']),
        ]

    def _create_challan_details_section(self, data: Dict) -> List:
        """Create challan details section."""
        elements = [Paragraph("Challan Details", self.styles['SectionHeading'])]
        
        details_data = [
            ['Challan Number', data.get('challan_number', 'N/A')],
            ['Date Issued', data.get('date', 'N/A')],
            ['Location', data.get('location', 'N/A')],
            ['Officer ID', data.get('officer_id', 'N/A')],
        ]
        
        table = Table(details_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements

    def _create_vehicle_info_section(self, data: Dict) -> List:
        """Create vehicle information section."""
        elements = [Paragraph("Vehicle Information", self.styles['SectionHeading'])]
        
        vehicle_data = [
            ['Vehicle Number', data.get('vehicle_number', 'N/A')],
            ['Owner Name', data.get('owner_name', 'N/A')],
            ['Contact Number', data.get('contact_number', 'N/A')],
            ['Address', data.get('address', 'N/A')],
        ]
        
        table = Table(vehicle_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements

    def _create_violation_section(self, data: Dict) -> List:
        """Create violation details section."""
        elements = [Paragraph("Violation Details", self.styles['SectionHeading'])]
        
        violation_data = [
            ['Violation Type', data.get('violation_type', 'N/A')],
            ['Description', data.get('violation_description', 'N/A')],
            ['Section', data.get('section', 'N/A')],
            ['Remarks', data.get('remarks', '')],
        ]
        
        table = Table(violation_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements

    def _create_amount_section(self, data: Dict) -> List:
        """Create amount and total section."""
        elements = [Paragraph("Amount Due", self.styles['SectionHeading'])]
        
        amount_data = [
            ['Base Fine', f"₹{data.get('base_fine', 0)}"],
            ['Additional Fine', f"₹{data.get('additional_fine', 0)}"],
            ['Total Amount', f"₹{data.get('amount', 0)}"],
            ['Due Date', data.get('due_date', 'N/A')],
        ]
        
        table = Table(amount_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_amount_table_style())
        elements.append(table)
        
        if data.get('notes'):
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("Notes:", self.styles['FieldLabel']))
            elements.append(Paragraph(data.get('notes', ''), self.styles['FieldValue']))
        
        return elements

    def _create_receipt_details_section(self, data: Dict) -> List:
        """Create receipt details section."""
        elements = [Paragraph("Receipt Information", self.styles['SectionHeading'])]
        
        details_data = [
            ['Receipt Number', data.get('receipt_number', 'N/A')],
            ['Challan Number', data.get('challan_number', 'N/A')],
            ['Date', data.get('date', 'N/A')],
            ['Transaction ID', data.get('transaction_id', 'N/A')],
        ]
        
        table = Table(details_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements

    def _create_payment_info_section(self, data: Dict) -> List:
        """Create payment information section."""
        elements = [Paragraph("Payment Information", self.styles['SectionHeading'])]
        
        payment_data = [
            ['Vehicle Number', data.get('vehicle_number', 'N/A')],
            ['Owner Name', data.get('owner_name', 'N/A')],
            ['Payment Method', data.get('payment_method', 'N/A')],
            ['Amount Paid', f"₹{data.get('amount', 0)}"],
        ]
        
        table = Table(payment_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements

    def _create_challan_reference_section(self, data: Dict) -> List:
        """Create challan reference section in receipt."""
        elements = [Paragraph("Challan Reference", self.styles['SectionHeading'])]
        
        reference_data = [
            ['Original Amount', f"₹{data.get('original_amount', 0)}"],
            ['Amount Paid', f"₹{data.get('amount', 0)}"],
            ['Remaining Balance', f"₹{data.get('balance', 0)}"],
            ['Payment Status', data.get('status', 'Completed')],
        ]
        
        table = Table(reference_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(self._get_table_style())
        elements.append(table)
        
        return elements

    def _create_signature_section(self) -> List:
        """Create signature section for challan."""
        elements = [Spacer(1, 0.3 * inch)]
        
        signature_data = [
            ['Issued By', '', 'Acknowledged By'],
            ['________________', '', '________________'],
            ['Officer Signature', '', 'Owner/Driver Signature'],
        ]
        
        table = Table(signature_data, colWidths=[2*inch, 0.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
        ]))
        elements.append(table)
        
        return elements

    def _create_receipt_footer(self) -> List:
        """Create footer section for receipt."""
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Please retain this receipt for your records"
        return [
            Paragraph(footer_text, self.styles['Normal']),
        ]

    def _get_table_style(self) -> TableStyle:
        """Get standard table style."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.TABLE_HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (0, -1), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.TABLE_ROW_COLOR]),
        ])

    def _get_amount_table_style(self) -> TableStyle:
        """Get table style for amount section with highlighting."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.TABLE_HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (0, -1), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (1, 2), (1, 2), 12),
            ('TEXTCOLOR', (1, 2), (1, 2), self.ACCENT_COLOR),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, grey),
            ('BACKGROUND', (0, 2), (-1, 2), self.TABLE_ROW_COLOR),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, self.TABLE_ROW_COLOR]),
        ])

    @staticmethod
    def validate_challan_data(data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate challan data before PDF generation.
        
        Args:
            data: Challan data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_fields = {
            'challan_number': 'Challan Number',
            'date': 'Date',
            'vehicle_number': 'Vehicle Number',
            'owner_name': 'Owner Name',
            'violation_description': 'Violation Description',
            'amount': 'Amount',
            'location': 'Location',
        }
        
        for field, label in required_fields.items():
            if field not in data or not data[field]:
                errors.append(f"{label} is required")
        
        if data.get('amount') and not isinstance(data['amount'], (int, float)):
            errors.append("Amount must be a number")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_receipt_data(data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate receipt data before PDF generation.
        
        Args:
            data: Receipt data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required_fields = {
            'receipt_number': 'Receipt Number',
            'challan_number': 'Challan Number',
            'date': 'Date',
            'amount': 'Amount',
            'payment_method': 'Payment Method',
            'vehicle_number': 'Vehicle Number',
            'owner_name': 'Owner Name',
        }
        
        for field, label in required_fields.items():
            if field not in data or not data[field]:
                errors.append(f"{label} is required")
        
        if data.get('amount') and not isinstance(data['amount'], (int, float)):
            errors.append("Amount must be a number")
        
        return len(errors) == 0, errors


# Convenience functions
def generate_challan(challan_data: Dict, output_path: Optional[str] = None) -> Optional[bytes]:
    """
    Generate a challan PDF document.
    
    Args:
        challan_data: Dictionary with challan details
        output_path: File path to save PDF
        
    Returns:
        PDF bytes if output_path is None, else None
    """
    generator = PDFGenerator()
    return generator.generate_challan_pdf(challan_data, output_path)


def generate_receipt(receipt_data: Dict, output_path: Optional[str] = None) -> Optional[bytes]:
    """
    Generate a receipt PDF document.
    
    Args:
        receipt_data: Dictionary with receipt details
        output_path: File path to save PDF
        
    Returns:
        PDF bytes if output_path is None, else None
    """
    generator = PDFGenerator()
    return generator.generate_receipt_pdf(receipt_data, output_path)
