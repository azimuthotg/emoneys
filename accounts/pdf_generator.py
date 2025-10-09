# -*- coding: utf-8 -*-
"""
PDF Generator for Receipt System
สร้าง PDF ใบสำคัญรับเงินตามรูปแบบมาตรฐาน NPU
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics import renderPDF
import qrcode
from io import BytesIO
import os
from pythainlp import word_tokenize
from django.conf import settings
from django.http import HttpResponse
from bs4 import BeautifulSoup
import re


class DottedUnderline(Flowable):
    """
    Flowable สำหรับวาดเส้นจุดประใต้ข้อความ
    """
    def __init__(self, width, gap=3, y_offset=0, x_offset=0, gray_level=0):
        Flowable.__init__(self)
        self.width = width
        self.gap = gap  # ระยะห่างระหว่างจุด
        self.y_offset = y_offset  # ปรับตำแหน่งขึ้น-ลง (+ = ขึ้น, - = ลง)
        self.x_offset = x_offset  # ระยะห่างจากขอบซ้าย
        self.gray_level = gray_level  # สีเทา (0=ดำ, 0.5=เทากลาง, 1=ขาว)
        self.height = 0.1 * cm

    def draw(self):
        """วาดเส้นจุดประ"""
        canvas = self.canv
        canvas.saveState()

        # วาดจุดประ
        x = self.x_offset  # เริ่มจากตำแหน่ง x_offset
        y = self.y_offset  # ใช้ y_offset ปรับตำแหน่ง
        canvas.setStrokeGray(self.gray_level)  # ตั้งสีเทา (0=ดำ, 1=ขาว)
        canvas.setLineWidth(0.5)
        canvas.setDash(1, self.gap)  # จุดยาว 1, เว้น gap
        canvas.line(x, y, x + self.width, y)

        canvas.restoreState()


class ReceiptPDFGenerator:
    """
    Generator สำหรับสร้าง PDF ใบสำคัญรับเงิน
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin_left = 2 * cm
        self.margin_right = 2 * cm
        self.margin_top = 1.5 * cm # ลดเหลือ 1.5 cm หรือ 1 cm
        self.margin_bottom = 2 * cm
        
        # ลงทะเบียนฟอนต์ไทย (ถ้ามี)
        self.setup_fonts()
        
    def setup_fonts(self):
        """ตั้งค่าฟอนต์สำหรับภาษาไทย"""
        try:
            # ลำดับความสำคัญ: THSarabunNew -> System fonts
            font_base_path = os.path.join(settings.BASE_DIR, 'static', 'fonts')
            
            # THSarabunNew font family
            thsarabun_fonts = {
                'THSarabunNew': 'THSarabunNew.ttf',
                'THSarabunNew-Bold': 'THSarabunNew Bold.ttf',
                'THSarabunNew-Italic': 'THSarabunNew Italic.ttf',
                'THSarabunNew-BoldItalic': 'THSarabunNew BoldItalic.ttf'
            }
            
            # ลงทะเบียนฟอนต์ THSarabunNew
            fonts_registered = 0
            for font_name, font_file in thsarabun_fonts.items():
                font_path = os.path.join(font_base_path, font_file)
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    fonts_registered += 1
            
            # ถ้าลงทะเบียนฟอนต์ THSarabunNew ได้
            if fonts_registered > 0:
                self.thai_font = 'THSarabunNew'
                self.thai_font_bold = 'THSarabunNew-Bold' if fonts_registered >= 2 else 'THSarabunNew'
                self.thai_font_italic = 'THSarabunNew-Italic' if fonts_registered >= 3 else 'THSarabunNew'
                return
            
            # Fallback: ลองหาฟอนต์ไทยในระบบ
            system_font_paths = [
                '/System/Library/Fonts/Thonburi.ttc',  # macOS
                'C:/Windows/Fonts/tahoma.ttf',  # Windows
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            ]
            
            for font_path in system_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ThaiFont', font_path))
                    self.thai_font = 'ThaiFont'
                    self.thai_font_bold = 'ThaiFont'
                    self.thai_font_italic = 'ThaiFont'
                    break
            else:
                self.thai_font = 'Helvetica'  # Final fallback
                self.thai_font_bold = 'Helvetica-Bold'
                self.thai_font_italic = 'Helvetica-Oblique'
                
        except Exception as e:
            print(f"Font setup error: {e}")
            self.thai_font = 'Helvetica'  # Final fallback
            self.thai_font_bold = 'Helvetica-Bold'
            self.thai_font_italic = 'Helvetica-Oblique'
    
    def prepare_thai_text(self, text):
        """
        ไม่ตัดคำอัตโนมัติ ให้แสดงตามที่ผู้ใช้พิมพ์
        รองรับ HTML formatting จาก WYSIWYG Editor
        """
        try:
            # ตรวจสอบว่ามี HTML tags หรือไม่
            if '<' in text and '>' in text:
                return self.prepare_html_text(text)

            # ไม่ตัดคำ แค่แทนที่ newline ด้วย <br/>
            text = text.replace('\n', '<br/>')
            return text

        except Exception as e:
            print(f"Text processing error: {e}")
            return text

    def prepare_html_text(self, html_text):
        """
        แปลง HTML จาก WYSIWYG Editor เป็น plain text
        ไม่ตัดคำอัตโนมัติ ให้แสดงตามที่ผู้ใช้พิมพ์
        """
        try:
            # Parse HTML และดึง plain text ออกมา
            soup = BeautifulSoup(html_text, 'html.parser')

            # แทนที่ <br> และ <p> ด้วย newline
            for br in soup.find_all('br'):
                br.replace_with('\n')

            for p in soup.find_all('p'):
                p.insert_after('\n')

            # แทนที่ <li> ด้วย bullet/number
            for ul in soup.find_all('ul'):
                for li in ul.find_all('li', recursive=False):
                    li.insert(0, '• ')
                    li.append('\n')

            for ol in soup.find_all('ol'):
                for idx, li in enumerate(ol.find_all('li', recursive=False), 1):
                    li.insert(0, f'{idx}. ')
                    li.append('\n')

            # ดึง plain text
            plain_text = soup.get_text()

            # ไม่ตัดคำ เก็บข้อความตามที่พิมพ์ แค่แทนที่ newline ด้วย <br/>
            plain_text = plain_text.replace('\n', '<br/>')

            return plain_text

        except Exception as e:
            print(f"HTML parsing error: {e}")
            # Fallback: ส่งกลับข้อความตามเดิม
            return html_text
    
    def generate_receipt_pdf(self, receipt, response=None, inline=True):
        """
        สร้าง PDF ใบสำคัญรับเงิน
        
        Args:
            receipt: Receipt object จากฐานข้อมูล
            response: HttpResponse object (optional)
            inline: True = แสดงในเบราว์เซอร์, False = download
            
        Returns:
            HttpResponse หรือ bytes ของ PDF
        """
        if response is None:
            response = HttpResponse(content_type='application/pdf')
            
            # ตั้งค่าให้แสดงแบบ inline หรือ download
            filename_number = receipt.receipt_number if receipt.receipt_number else f'draft_{receipt.id}'
            if inline:
                response['Content-Disposition'] = f'inline; filename="receipt_{filename_number}.pdf"'
            else:
                response['Content-Disposition'] = f'attachment; filename="receipt_{filename_number}.pdf"'
        
        # สร้าง PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.margin_left,
            rightMargin=self.margin_right,
            topMargin=self.margin_top,
            bottomMargin=self.margin_bottom
        )
        
        # สร้างเนื้อหา
        story = []
        
        # หัวเอกสาร
        story.extend(self._create_header())
        story.append(Spacer(1, 0.3 * cm))
        
        # ข้อมูลใบสำคัญ
        story.extend(self._create_receipt_info(receipt))
        story.append(Spacer(1, 0.3 * cm))
        
        # ข้อมูลผู้รับเงิน
        story.extend(self._create_recipient_info(receipt))
        story.append(Spacer(1, 0.3 * cm))
        
        # รายการรับเงิน (รวมแถวรวมเป็นเงินแล้ว)
        story.extend(self._create_items_table(receipt))
        story.append(Spacer(1, 0.3 * cm))
        
        # ลายเซ็นและ QR Code
        story.extend(self._create_signature_section(receipt))

        # สร้าง PDF พร้อม callback สำหรับ QR Code มุมซ้ายล่าง
        doc.build(story, onFirstPage=lambda canvas, doc: self._draw_floating_qr(canvas, doc, receipt))
        pdf = buffer.getvalue()
        buffer.close()
        
        response.write(pdf)
        return response
    
    def _create_header(self):
        """สร้างหัวเอกสาร"""
        styles = getSampleStyleSheet()
        
        # สร้าง style สำหรับหัวเอกสาร
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.thai_font_bold,
            fontSize=18,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=0.3 * cm
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=14,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=0.2 * cm
        )
        
        content = []
        
        # Logo และหัวเอกสาร
        try:
            # ลองหา logo
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
            if not os.path.exists(logo_path):
                logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')
            
            if os.path.exists(logo_path):
                # สร้าง style สำหรับหัวเอกสารพร้อม logo
                receipt_title_style = ParagraphStyle(
                    'ReceiptTitle',
                    parent=styles['Heading1'],
                    fontName=self.thai_font_bold,
                    fontSize=20,
                    textColor=colors.black,
                    alignment=TA_CENTER,
                    spaceAfter=0.2 * cm
                )
                
                # สร้างตารางที่มี logo และหัวเอกสาร
                logo_img = Image(logo_path, width=2*cm, height=2*cm)
                
                header_data = [[
                    logo_img,
                    Paragraph("ใบสำคัญรับเงิน", receipt_title_style),
                    ""  # คอลัมน์ว่างทางขวา
                ]]
                
                header_table = Table(header_data, colWidths=[3*cm, 11*cm, 3*cm])
                header_table.setStyle(TableStyle([
                    # ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    # ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                    # ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # ('GRID', (0, 0), (-1, -1), 1, colors.black),  # ← เพิ่มบรรทัดนี้

                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),      # โลโก้ชิดซ้าย
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),    # หัวเรื่องกึ่งกลาง
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING',  (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING',   (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
                    # ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                content.append(header_table)
            else:
                # ไม่มี logo ให้ใช้แบบเดิม
                receipt_title_style = ParagraphStyle(
                    'ReceiptTitle',
                    parent=styles['Heading1'],
                    fontName=self.thai_font_bold,
                    fontSize=20,
                    textColor=colors.black,
                    alignment=TA_CENTER,
                    spaceAfter=0.3 * cm
                )
                content.append(Paragraph("ใบสำคัญรับเงิน", receipt_title_style))
        except Exception as e:
            # มีปัญหา ให้ใช้แบบเดิม
            receipt_title_style = ParagraphStyle(
                'ReceiptTitle',
                parent=styles['Heading1'],
                fontName=self.thai_font_bold,
                fontSize=20,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=0.3 * cm
            )
            content.append(Paragraph("ใบสำคัญรับเงิน", receipt_title_style))
        
        return content
    
    def _create_receipt_info(self, receipt):
        """สร้างข้อมูลใบสำคัญ (ตามรูปแบบ Capture.JPG)"""
        styles = getSampleStyleSheet()
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            leading=16,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        
        right_style = ParagraphStyle(
            'RightStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            leading=16,
            textColor=colors.black,
            alignment=TA_RIGHT
        )
        
        content = []

        # แปลงวันที่เป็นพุทธศักราช ค.ศ. 2568 (ถ้าร่างจะแสดง xx/xx/xxxx)
        thai_date = self._convert_to_thai_date(receipt.receipt_date) if receipt.receipt_date else "xx/xx/xxxx"

        # สร้างตารางตามรูปแบบ Capture.JPG (สลับข้าง)
        # จัดการกรณีไม่มีเลขที่ (draft) - ใช้ format เดียวกับเลขที่จริงเพื่อให้ layout ไม่เปลี่ยน
        receipt_number_text = receipt.receipt_number if receipt.receipt_number else "xxxxx/xxxx"

        data = [
        # บรรทัด 1: รหัสเล่ม (ซ้าย) และ เลขที่ (ขวา)
        [Paragraph(f"เล่มที่: {receipt.volume_code}", info_style),
         Paragraph(f"เลขที่: {receipt_number_text}", info_style)],
        # บรรทัด 2: ชื่อหน่วยงาน
        [Paragraph("", info_style), Paragraph(f"{receipt.department.name} มหาวิทยาลัยนครพนม", info_style)],
        # บรรทัด 3: ที่อยู่หน่วยงาน - ใช้ Paragraph แทน empty string เพื่อให้ layout สม่ำเสมอ
            [Paragraph("", info_style), Paragraph(f"{receipt.department.get_full_address()}" or "ที่อยู่ไม่ระบุ", info_style)],
        # บรรทัด 4: วันที่ไทย
        [Paragraph("", info_style), Paragraph(f"วันที่ {thai_date}", info_style)]
        ]
        
        table = Table(data, colWidths=[9*cm, 8*cm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # ('LEFTPADDING', (0, 0), (-1, -1), 2),
            # ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            # ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        
        content.append(table)
        
        return content
    
    def _convert_to_thai_date(self, date):
        """แปลงวันที่เป็นพุทธศักราชไทย"""
        thai_months = [
            'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
            'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
        ]
        
        day = date.day
        month = thai_months[date.month - 1]
        year = date.year + 543  # แปลงเป็น พ.ศ.
        
        return f"{day} {month} {year}"
    
    def _create_recipient_info(self, receipt):
        """สร้างข้อมูลผู้รับเงิน"""
        styles = getSampleStyleSheet()
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            leading=16,
            textColor=colors.black,
            alignment=TA_LEFT,
            leftIndent=6  # ให้ตรงกับ LEFTPADDING ของตารางรายการ
        )

        # Style แยกสำหรับ line1 ที่มีข้อความยาว 2 บรรทัด
        line1_style = ParagraphStyle(
            'Line1Style',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            leading=18,  # เพิ่ม leading สำหรับข้อความ 2 บรรทัด
            textColor=colors.black,
            alignment=TA_LEFT,
            leftIndent=6
        )

        content = []

        # บรรทัด 1: ข้าพเจ้า + ที่อยู่เต็ม + รหัสไปรษณีย์ (จองพื้นที่ 2 บรรทัดเสมอ)
        address_with_postal = receipt.recipient_address
        if receipt.recipient_postal_code:
            address_with_postal += f" รหัสไปรษณีย์ {receipt.recipient_postal_code}"

        line1 = f"ข้าพเจ้า {receipt.recipient_name} อยู่บ้านเลขที่ {address_with_postal}"

        # ใช้ Table เพื่อกำหนดความสูงคงที่สำหรับ 2 บรรทัด
        line1_table = Table([[Paragraph(line1, line1_style)]], colWidths=[17*cm], rowHeights=[1.2*cm])
        line1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 6),  # ให้ตรงกับ LEFTPADDING ของตารางรายการ
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ]))
        content.append(line1_table)

        # เส้นจุดประใต้บรรทัด 1 (2 เส้นเพราะเว้นไว้ 2 บรรทัด)
        # เส้นที่ 1 - ใต้บรรทัดแรก
        content.append(DottedUnderline(15*cm, gap=1, y_offset=19, x_offset=42, gray_level=0.3))
        # เส้นที่ 2 - ใต้บรรทัดที่สอง (y_offset ต่ำกว่าเส้นแรก)
        content.append(DottedUnderline(16.3*cm, gap=1, y_offset=4, x_offset=6, gray_level=0.3))
        # content.append(Spacer(1, 0.1 * cm))

        # บรรทัด 2: เลขบัตรประชาชน + ได้รับเงินจาก (ใช้ &nbsp; เพื่อเว้นช่องว่างจริงๆ)
        line2 = f"เลขบัตรประชาชน&nbsp;&nbsp;&nbsp;{receipt.recipient_id_card}&nbsp;&nbsp;&nbsp;ได้รับเงินจาก&nbsp;&nbsp;&nbsp;มหาวิทยาลัยนครพนม"
        content.append(Paragraph(line2, info_style))

        # เส้นที่ 3 - ใต้เลขบัตรประชาชน
        content.append(DottedUnderline(3.3*cm, gap=1, y_offset=2 , x_offset=85, gray_level=0.3))
        # เส้นที่ 4 - ใต้มหาวิทยาลัยนครพนม
        content.append(DottedUnderline(8.3*cm, gap=1, y_offset=5, x_offset=233, gray_level=0.3))
        # content.append(Spacer(1, 0.05 * cm))
        # บรรทัด 3: ข้อความนำ
        line3 = "ดังรายการต่อไปนี้"
        content.append(Paragraph(line3, info_style))

        # content.append(Spacer(1, 0.05 * cm))

        return content
    
    def _create_items_table(self, receipt):
        """สร้างตารางรายการรับเงิน"""
        styles = getSampleStyleSheet()
        content = []
        
        # สร้าง style สำหรับ description (ไม่ justify ให้แสดงตามที่พิมพ์)
        description_style = ParagraphStyle(
            'DescriptionStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            leading=18,
            alignment=TA_LEFT,  # ชิดซ้าย ไม่ justify
            wordWrap='CJK',  # รองรับภาษาไทยและเอเชีย
            breakLongWords=0,  # ไม่ตัดคำยาว
            splitLongWords=0,  # ไม่แยกคำยาว
            spaceBefore=2,
            spaceAfter=2
        )
        
        # หัวตาราง
        data = [['ลำดับ', 'รายการ', 'จำนวนเงิน (บาท)']]
        
        # รายการ
        for idx, item in enumerate(receipt.items.all().order_by('order'), 1):
            # ใช้ PyThaiNLP รวมคำเป็นกลุ่มใหญ่ แล้วให้ ReportLab ตัดต่อ
            prepared_text = self.prepare_thai_text(item.description)
            description_text = prepared_text.replace('\n', '<br/>')
            
            data.append([
                str(idx),
                Paragraph(description_text, description_style),  # PyThaiNLP + ReportLab ร่วมมือกัน
                f"{item.amount:,.2f}"
            ])
        
        # แถวรวมเป็นเงิน
        data.append([
            "รวมเป็นเงิน",  # คอลัมน์ 1 จะ merge กับ 2
            "",  # คอลัมน์ 2 ว่าง (จะถูก merge)
            f"{receipt.total_amount:,.2f}"  # คอลัมน์ 3 จำนวนเงินรวม
        ])
        
        # สร้างตาราง (ไม่ระบุ rowHeights เพื่อให้ปรับอัตโนมัติ)
        table = Table(data, colWidths=[1.5*cm, 12*cm, 3.5*cm])
        # คำนวณ row index ของแถวสุดท้าย (แถวรวม)
        last_row = len(data) - 1
        
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.thai_font),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('LEADING', (0, 0), (-1, -1), 18),  # เพิ่ม leading ให้มากขึ้น
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # ลำดับ
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # รายการ
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # จำนวนเงิน
            # Header จัดกึ่งกลางทุกคอลัมน์
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # หัวตารางกึ่งกลาง
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),   # เปลี่ยนจาก MIDDLE เป็น TOP เพื่อให้ดูดีกับข้อความหลายบรรทัด
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # เส้นบาง
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),  # สีเทาอ่อนกว่า
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # ข้อความสีดำ
            
            # Padding สำหรับ cells เพื่อให้ข้อความไม่ติดขอบ
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # แถวรวมเป็นเงิน
            ('SPAN', (0, last_row), (1, last_row)),  # merge คอลัมน์ 1-2
            ('FONTNAME', (0, last_row), (1, last_row), self.thai_font_bold),  # ตัวหนา
            ('ALIGN', (0, last_row), (1, last_row), 'RIGHT'),  # ชิดขวา
            ('VALIGN', (0, last_row), (-1, last_row), 'MIDDLE'),  # แถวรวมให้อยู่กึ่งกลาง
            ('BACKGROUND', (0, last_row), (-1, last_row), colors.Color(0.9, 0.9, 0.9)),  # พื้นหลังเทาอ่อน
        ]))
        
        content.append(table)
        
        # จำนวนเงิน(ตัวอักษร) หลังตารางโดยตรง
        amount_text_style = ParagraphStyle(
            'AmountTextStyle',
            parent=styles['Normal'],
            fontName=self.thai_font_bold,
            fontSize=16,
            leading=16,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceBefore=0.2 * cm
        )
        
        amount_text_content = f"จำนวนเงิน(ตัวอักษร): {receipt.total_amount_text}"
        content.append(Paragraph(amount_text_content, amount_text_style))
        
        return content
    
    
    def _create_signature_section(self, receipt):
        """สร้างส่วนลายเซ็น (QR Code จะแสดงมุมซ้ายล่างแบบ fixed)"""
        styles = getSampleStyleSheet()

        signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER
        )

        content = []
        content.append(Spacer(1, 1 * cm))

        # ตารางลายเซ็น (ไม่มี QR Code)
        data = [
            ['ลงชื่อ ................................. ผู้รับเงิน'],
            [f'({receipt.recipient_name})'],
            [''],
            ['ลงชื่อ ................................. ผู้จ่ายเงิน'],
            [f'({receipt.created_by.get_display_name()})']
        ]

        table = Table(data, colWidths=[10*cm], rowHeights=[0.8*cm]*5)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.thai_font),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        # จัดตารางให้กึ่งกลาง
        signature_table = Table([["", table, ""]], colWidths=[3.5*cm, 10*cm, 3.5*cm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        content.append(signature_table)

        return content
    
    def _draw_floating_qr(self, canvas, doc, receipt):
        """วาด QR Code มุมซ้ายล่าง (รองรับทั้ง draft และใบสำคัญจริง)"""
        try:
            # สร้าง QR Code (รองรับทั้ง draft และใบสำคัญจริง)
            qr_img = self._generate_qr_code(receipt)

            # ถ้าสร้าง QR ไม่ได้ ก็ไม่ต้องวาด
            if not qr_img:
                return

            # แปลงวันที่สร้างเป็นไทย (timezone-aware)
            from django.utils import timezone

            # แปลง created_at เป็น timezone ของไทย
            local_time = timezone.localtime(receipt.created_at)
            created_thai = self._convert_to_thai_date(local_time)
            time_thai = local_time.strftime('%H:%M:%S')

            # ถ้าเป็น draft ใช้ข้อความตัวอย่าง
            if not receipt.receipt_number:
                footer_info = f"ร่าง | สร้างเมื่อ: {created_thai} เวลา {time_thai} น."
            else:
                verification_url = receipt.get_verification_url()
                if verification_url:
                    footer_info = f"URL ตรวจสอบ: {verification_url} | สร้างเมื่อ: {created_thai} เวลา {time_thai} น."
                else:
                    footer_info = f"สร้างเมื่อ: {created_thai} เวลา {time_thai} น."

            # วาง QR Code ที่มุมซ้าย-ล่าง (ตำแหน่งคงที่)
            qr_x = self.margin_left
            qr_y = self.margin_bottom

            # วาด QR Code ลงบน canvas
            qr_img.drawOn(canvas, qr_x, qr_y)

            # วาดข้อความข้างๆ QR Code (ชิดขอบล่าง)
            text_x = qr_x + 3.5*cm  # ข้างๆ QR Code (3cm + 0.5cm spacing)
            text_y = qr_y + 0.3*cm  # ชิดขอบล่าง

            canvas.setFont(self.thai_font, 12)
            canvas.drawString(text_x, text_y, footer_info)

        except Exception as e:
            # ถ้าวาด QR ไม่ได้ ไม่ต้องทำอะไร
            pass
    
    def _generate_qr_code(self, receipt):
        """สร้าง QR Code สำหรับตรวจสอบใบสำคัญ (รองรับทั้ง draft และใบสำคัญจริง)"""
        try:
            # ถ้าเป็น draft (ไม่มีเลขที่) ใช้ URL ตัวอย่าง
            if not receipt.receipt_number:
                qr_data = "https://example.com/receipt/draft"
            else:
                # ดึงข้อมูล QR Code จริง
                qr_data = receipt.generate_qr_code_data()

                # ถ้าไม่มีข้อมูล ใช้ URL ตัวอย่าง
                if not qr_data:
                    qr_data = "https://example.com/receipt/unknown"

            # สร้าง QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # สร้างรูปภาพ
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # แปลงเป็น BytesIO สำหรับ ReportLab
            img_buffer = BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # สร้าง Image object สำหรับ ReportLab
            img = Image(img_buffer, width=3*cm, height=3*cm)

            return img

        except Exception as e:
            # ถ้าสร้าง QR Code ไม่ได้ ให้ใช้ข้อความแทน
            styles = getSampleStyleSheet()
            style = ParagraphStyle(
                'QRStyle',
                parent=styles['Normal'],
                fontName=self.thai_font,
                fontSize=10,
                textColor=colors.black,
                alignment=TA_CENTER
            )
            return Paragraph("QR Code<br/>ไม่สามารถสร้างได้", style)


def generate_receipt_pdf(receipt, inline=True):
    """
    Helper function สำหรับสร้าง PDF ใบสำคัญรับเงิน
    
    Args:
        receipt: Receipt object
        inline: True = แสดงในเบราว์เซอร์, False = download
        
    Returns:
        HttpResponse ที่มี PDF content
    """
    generator = ReceiptPDFGenerator()
    return generator.generate_receipt_pdf(receipt, inline=inline)