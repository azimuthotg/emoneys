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
from reportlab.pdfgen import canvas as pdfgen_canvas
import qrcode
from io import BytesIO
import os
from pythainlp import word_tokenize
from django.conf import settings
from django.http import HttpResponse
from bs4 import BeautifulSoup
import re
from accounts.utils import convert_to_thai_date


class WatermarkCanvas(pdfgen_canvas.Canvas):
    """
    Custom Canvas ที่วาด watermark หลังจาก render เนื้อหาเสร็จแล้ว
    เพื่อให้ watermark ทับบนเนื้อหา
    """
    def __init__(self, *args, **kwargs):
        # เก็บข้อมูลที่จำเป็นสำหรับ watermark
        self.receipt = kwargs.pop('receipt', None)
        self.page_width = kwargs.pop('page_width', A4[0])
        self.page_height = kwargs.pop('page_height', A4[1])
        self.thai_font_bold = kwargs.pop('thai_font_bold', 'Helvetica-Bold')
        self.qr_callback = kwargs.pop('qr_callback', None)
        pdfgen_canvas.Canvas.__init__(self, *args, **kwargs)

    def showPage(self):
        """
        Override showPage เพื่อวาด watermark ก่อน flush page
        Method นี้ถูกเรียกหลังจาก content ถูก render เสร็จแล้ว
        """
        # วาด QR Code ก่อน (ด้านล่าง)
        if self.qr_callback and self.receipt:
            self.qr_callback(self, None, self.receipt)

        # วาด watermark ทับบนสุด
        if self.receipt and self.receipt.status == 'cancelled':
            self._draw_watermark()

        # เรียก parent's showPage เพื่อ flush page
        pdfgen_canvas.Canvas.showPage(self)

    def _draw_watermark(self):
        """วาดตราประทับ 'ยกเลิก' สีแดงทับบนเนื้อหา พร้อมเงาและวันที่ยกเลิก"""
        try:
            self.saveState()

            # ตำแหน่งกึ่งกลางหน้ากระดาษ
            center_x = self.page_width / 2
            center_y = self.page_height / 2

            # ย้ายจุดกึ่งกลาง (origin) ของ canvas ไปที่กึ่งกลางหน้ากระดาษ
            self.translate(center_x, center_y)

            # หมุน canvas -20 องศา (เอียงเฉียงเล็กน้อย)
            self.rotate(-20)

            # คำนวณขนาดกรอบ
            font_size = 140  # เพิ่มจาก 120 เป็น 140
            text = "ยกเลิก"
            text_width = self.stringWidth(text, self.thai_font_bold, font_size)
            rect_padding = 20

            # วาดเงาด้านหลัง (offset เล็กน้อย)
            shadow_offset = 5
            self.setFillColorRGB(0, 0, 0)  # สีดำ
            self.setStrokeColorRGB(0, 0, 0)  # เส้นขอบสีดำ
            self.setFillAlpha(0.1)  # โปร่งแสง 10%
            self.setStrokeAlpha(0.1)  # เส้นขอบโปร่งแสง 10%
            self.setLineWidth(4)
            self.rect(
                -text_width/2 - rect_padding + shadow_offset,
                -70 - rect_padding - shadow_offset,
                text_width + rect_padding * 2,
                font_size + rect_padding * 2,
                stroke=1,
                fill=1
            )

            # วาดกรอบสี่เหลี่ยมสีแดง (ด้านบน)
            self.setFillColorRGB(1, 0, 0)  # สีแดง
            self.setStrokeColorRGB(1, 0, 0)  # เส้นขอบสีแดง
            self.setFillAlpha(0.3)  # โปร่งแสง 30%
            self.setStrokeAlpha(0.5)  # เส้นขอบโปร่งแสง 50%
            self.setLineWidth(4)
            self.rect(
                -text_width/2 - rect_padding,
                -70 - rect_padding,
                text_width + rect_padding * 2,
                font_size + rect_padding * 2,
                stroke=1,
                fill=0
            )

            # วาดข้อความ "ยกเลิก" ขนาด 140 pt
            self.setFont(self.thai_font_bold, font_size)
            self.drawCentredString(0, -50, text)

            # เพิ่มวันที่ยกเลิกด้านล่างกรอบ (ตัวเล็ก)
            if self.receipt and self.receipt.updated_at:
                from django.utils import timezone
                local_time = timezone.localtime(self.receipt.updated_at)
                cancelled_date = convert_to_thai_date(local_time, 'full')

                # ตั้งค่าฟอนต์เล็ก
                date_font_size = 14
                self.setFont(self.thai_font_bold, date_font_size)
                self.setFillAlpha(0.5)  # โปร่งแสงมากขึ้น

                # วาดวันที่ชิดขอบล่างของกรอบ กึ่งกลางซ้ายขวา
                date_y = -70 - rect_padding + 8  # ชิดขอบล่างของกรอบ
                self.drawCentredString(0, date_y, f"วันที่ยกเลิก: {cancelled_date}")

            self.restoreState()

        except Exception as e:
            # ถ้าวาด watermark ไม่ได้ ไม่ต้องทำอะไร
            pass


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
        self.margin_top = 0.5 * cm # ลดลงจาก 1.5 cm เป็น 0.5 cm (ลดลง 1 cm)
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
        
        # สร้าง PDF ด้วย Custom Canvas
        buffer = BytesIO()

        # สร้าง custom canvas factory
        def canvas_factory(filename, **kwargs):
            return WatermarkCanvas(
                filename,
                receipt=receipt,
                page_width=self.page_width,
                page_height=self.page_height,
                thai_font_bold=self.thai_font_bold,
                qr_callback=self._draw_floating_qr,
                **kwargs  # ส่ง parameters อื่นๆ ต่อไปยัง Canvas
            )

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

        # หัวเอกสาร (รวมเล่มที่และเลขที่แล้ว)
        story.extend(self._create_header(receipt))
        story.append(Spacer(1, 0.3 * cm))

        # ข้อมูลใบสำคัญ (ชื่อหน่วยงาน + ที่อยู่ + วันที่)
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

        # สร้าง PDF ด้วย custom canvas (watermark จะถูกวาดโดย WatermarkCanvas.showPage())
        doc.build(story, canvasmaker=canvas_factory)
        pdf = buffer.getvalue()
        buffer.close()
        
        response.write(pdf)
        return response
    
    def _create_header(self, receipt):
        """สร้างหัวเอกสาร พร้อมเล่มที่และเลขที่ในบรรทัดเดียวกับ logo"""
        styles = getSampleStyleSheet()

        # สร้าง style สำหรับ เล่มที่/เลขที่
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            textColor=colors.black,
            alignment=TA_LEFT
        )

        right_info_style = ParagraphStyle(
            'RightInfoStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            textColor=colors.black,
            alignment=TA_RIGHT
        )

        content = []

        # เตรียมข้อมูลเล่มที่และเลขที่
        receipt_number_text = receipt.receipt_number if receipt.receipt_number else "xxxxx/xxxx"

        # Logo และหัวเอกสาร (โลโก้กึ่งกลางพร้อมเล่มที่และเลขที่ข้างๆ)
        try:
            # ลองหา logo
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
            if not os.path.exists(logo_path):
                logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')

            if os.path.exists(logo_path):
                # โลโก้กึ่งกลาง
                logo_img = Image(logo_path, width=2.5*cm, height=2.5*cm)

                # สร้างตารางแบบ 3 คอลัมน์: เล่มที่ | Logo | เลขที่
                header_data = [
                    [
                        Paragraph(f"เล่มที่: {receipt.volume_code}", info_style),
                        logo_img,
                        Paragraph(f"เลขที่: {receipt_number_text}", right_info_style)
                    ]
                ]

                header_table = Table(header_data, colWidths=[6*cm, 5*cm, 6*cm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),      # เล่มที่ ชิดซ้าย
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),    # Logo กึ่งกลาง
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),     # เลขที่ ชิดขวา
                    ('VALIGN', (0, 0), (-1, 0), 'TOP'),     # ทั้งหมดชิดบน
                    ('TOPPADDING', (0, 0), (-1, 0), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
                ]))

                content.append(header_table)

                # ใบสำคัญรับเงินอยู่ใต้โลโก้
                receipt_title_style = ParagraphStyle(
                    'ReceiptTitle',
                    parent=styles['Heading1'],
                    fontName=self.thai_font_bold,
                    fontSize=20,
                    textColor=colors.black,
                    alignment=TA_CENTER,
                )
                content.append(Paragraph("ใบสำคัญรับเงิน", receipt_title_style))
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
        """สร้างข้อมูลใบสำคัญ - ชื่อหน่วยงาน + ที่อยู่ + วันที่ (ชิดซ้ายตรงเส้นกั้นกลางหน้ากระดาษ)"""
        styles = getSampleStyleSheet()

        left_style = ParagraphStyle(
            'LeftStyle',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=16,
            leading=16,
            textColor=colors.black,
            alignment=TA_LEFT
        )

        content = []

        # แปลงวันที่เป็นพุทธศักราช ค.ศ. 2568 (ถ้าร่างจะแสดง xx/xx/xxxx)
        thai_date = convert_to_thai_date(receipt.receipt_date, 'full') if receipt.receipt_date else "xx/xx/xxxx"

        # สร้างตาราง 2 คอลัมน์ - คอลัมน์ซ้ายว่าง, คอลัมน์ขวาชิดซ้าย (ตามเส้นแดงในรูป)
        data = [
            # บรรทัด 1: ชื่อหน่วยงาน
            ["", Paragraph(f"{receipt.department.name} มหาวิทยาลัยนครพนม", left_style)],
            # บรรทัด 2: ที่อยู่หน่วยงาน
            ["", Paragraph(f"{receipt.department.get_full_address()}" or "ที่อยู่ไม่ระบุ", left_style)],
            # บรรทัด 3: วันที่ไทย
            ["", Paragraph(f"วันที่ {thai_date}", left_style)]
        ]

        # คอลัมน์ซ้ายกว้าง ~10cm, คอลัมน์ขวากว้าง ~7cm (ตรงกับเส้นกั้นในรูป)
        table = Table(data, colWidths=[10*cm, 7*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),      # คอลัมน์ขวาชิดซ้าย
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        content.append(table)

        return content
    
    def _convert_to_thai_date(self, date):
        """
        แปลงวันที่เป็นพุทธศักราชไทย
        (Deprecated: ใช้ convert_to_thai_date จาก accounts.utils แทน)
        """
        return convert_to_thai_date(date, 'full')
    
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

        # แยกข้อมูลเป็น 2 บรรทัดตามรูป Capture.JPG
        # บรรทัด 1: ข้าพเจ้า [ชื่อ]
        recipient_line1 = f"ข้าพเจ้า {receipt.recipient_name}"

        # บรรทัด 2: ที่อยู่ [ที่อยู่] รหัสไปรษณีย์ [รหัส]
        recipient_line2 = f"ที่อยู่ {receipt.recipient_address}"
        if receipt.recipient_postal_code:
            recipient_line2 += f" รหัสไปรษณีย์ {receipt.recipient_postal_code}"

        # รวม 2 บรรทัดด้วย <br/> เพื่อให้แสดงแยกบรรทัด
        full_text = f"{recipient_line1}<br/>{recipient_line2}"

        # ใช้ Table เพื่อกำหนดความสูงคงที่สำหรับ 2 บรรทัด
        line1_table = Table([[Paragraph(full_text, line1_style)]], colWidths=[17*cm], rowHeights=[1.2*cm])
        line1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 6),  # ให้ตรงกับ LEFTPADDING ของตารางรายการ
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ]))
        content.append(line1_table)

        # เส้นจุดประใต้บรรทัด (2 เส้นสำหรับ 2 บรรทัด)
        # เส้นที่ 1 - ใต้บรรทัดแรก (ข้าพเจ้า...)
        content.append(DottedUnderline(15*cm, gap=1, y_offset=19, x_offset=42, gray_level=0.3))
        # เส้นที่ 2 - ใต้บรรทัดที่สอง (ที่อยู่...)
        content.append(DottedUnderline(15.6*cm, gap=1, y_offset=4, x_offset=27, gray_level=0.3))
        # content.append(Spacer(1, 0.1 * cm))

        # บรรทัดถัดไป: เลขบัตรประชาชน + ได้รับเงินจาก (ใช้ &nbsp; เพื่อเว้นช่องว่างจริงๆ)
        id_card_line = f"เลขบัตรประชาชน&nbsp;&nbsp;&nbsp;{receipt.recipient_id_card}&nbsp;&nbsp;&nbsp;ได้รับเงินจาก&nbsp;&nbsp;&nbsp;มหาวิทยาลัยนครพนม"
        content.append(Paragraph(id_card_line, info_style))

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
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            
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
        """
        สร้างส่วนลายเซ็น (รองรับทั้งจ่ายปกติและยืมเงิน)

        Logic:
        - จ่ายปกติ (is_loan=False): ผู้รับเงิน=ชื่อผู้รับเงิน, ผู้จ่ายเงิน=ว่าง (จุด)
        - ยืมเงิน (is_loan=True): ผู้รับเงิน=ชื่อผู้รับเงิน, ผู้จ่ายเงิน=ชื่อผู้สร้าง
        """
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

        # กำหนดชื่อตาม is_loan
        if receipt.is_loan:
            # ยืมเงิน: แสดงชื่อผู้รับเงิน และ ผู้จ่ายเป็นชื่อผู้สร้าง
            recipient_name = receipt.recipient_name
            payer_name = receipt.created_by.get_display_name()
        else:
            # จ่ายปกติ: แสดงชื่อผู้รับเงิน, ผู้จ่ายเงินเป็นว่าง (จุด)
            recipient_name = receipt.recipient_name
            payer_name = '...........................................................'

        # ตารางลายเซ็น
        data = [
            ['ลงชื่อ ................................. ผู้รับเงิน'],
            [f'({recipient_name})'],
            [''],
            ['ลงชื่อ ................................. ผู้จ่ายเงิน'],
            [f'({payer_name})']
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
    
    def _is_food_receipt(self, receipt):
        """ตรวจสอบว่าเป็นใบสำคัญค่าอาหารหรือไม่"""
        # เช็คว่ามีรายการที่เกี่ยวข้องกับค่าอาหารหรือไม่
        food_keywords = ['ค่าอาหาร']
        for item in receipt.items.all():
            for keyword in food_keywords:
                if keyword in item.description:
                    return True
        return False

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
            created_thai = convert_to_thai_date(local_time, 'full')
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

            # ตรวจสอบว่าเป็นใบสำคัญค่าอาหารหรือไม่
            is_food = self._is_food_receipt(receipt)

            if is_food:
                # หมายเหตุสำหรับค่าอาหาร (อยู่เหนือ footer_info)
                note_x = qr_x + 3.5*cm
                note_y_start = qr_y + 2.5*cm  # เริ่มจากตำแหน่งสูงกว่า footer_info

                canvas.setFont(self.thai_font, 12)

                # บรรทัดที่ 1
                canvas.drawString(note_x, note_y_start, "1. ต้องแนบสำเนาบัตรประชาชนของผู้รับเงิน พร้อมเซ็นรับรองสำเนาถูกต้อง")

                # บรรทัด ที่ 2
                note_y_2 = note_y_start - 0.45*cm
                canvas.drawString(note_x, note_y_2, "2. ลายเซ็นรับรองสำเนาถูกต้องในสำเนาบัตรประชาชนของผู้รับเงิน ต้องตรงกับลายเซ็นในใบสำคัญรับเงิน")

                # บรรทัดที่ 3
                note_y_3 = note_y_2 - 0.45*cm
                canvas.drawString(note_x, note_y_3, "3. ต้องลงลายเซ็นด้วยปากกาสีน้ำเงินเท่านั้น")

                # วาดข้อความ footer_info (ชิดขอบล่าง)
                text_x = qr_x + 3.5*cm
                text_y = qr_y + 0.3*cm
                canvas.drawString(text_x, text_y, footer_info)
            else:
                # ไม่ใช่ค่าอาหาร แสดงแค่ footer_info
                text_x = qr_x + 3.5*cm
                text_y = qr_y + 0.3*cm
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