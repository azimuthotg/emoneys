"""
QR Code Generation Utilities for Receipt Verification
"""
import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import json


def generate_qr_code_image(data, size=(200, 200), border=4):
    """
    สร้าง QR Code image จากข้อมูล
    
    Args:
        data (str): ข้อมูลที่จะใส่ใน QR Code
        size (tuple): ขนาดของภาพ QR Code
        border (int): ขนาด border
        
    Returns:
        PIL.Image: QR Code image
    """
    qr = qrcode.QRCode(
        version=1,  # ควบคุมขนาด QR Code (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 7% error correction
        box_size=10,  # ขนาดของแต่ละ box
        border=border,  # ขนาด border
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    # สร้างภาพ QR Code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # ปรับขนาดภาพ
    img = img.resize(size, Image.Resampling.LANCZOS)
    
    return img


def generate_qr_code_base64(data, size=(200, 200)):
    """
    สร้าง QR Code เป็น base64 string สำหรับแสดงใน HTML
    
    Args:
        data (str): ข้อมูลที่จะใส่ใน QR Code
        size (tuple): ขนาดของภาพ QR Code
        
    Returns:
        str: Base64 encoded image string
    """
    img = generate_qr_code_image(data, size)
    
    # แปลงเป็น base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def create_verification_qr_for_receipt(receipt):
    """
    สร้าง QR Code สำหรับใบสำคัญรับเงิน
    
    Args:
        receipt: Receipt model instance
        
    Returns:
        str: Base64 encoded QR Code image
    """
    if not receipt.verification_hash:
        receipt.verification_hash = receipt.generate_verification_hash()
        
    if not receipt.qr_code_data:
        receipt.qr_code_data = receipt.generate_qr_code_data()
    
    # ใช้ URL เป็นข้อมูลหลักใน QR Code
    verification_url = receipt.get_verification_url()
    
    return generate_qr_code_base64(verification_url, size=(150, 150))


def create_qr_with_logo(data, logo_path=None, size=(200, 200)):
    """
    สร้าง QR Code พร้อม logo ตรงกลาง
    
    Args:
        data (str): ข้อมูลที่จะใส่ใน QR Code  
        logo_path (str): path ของ logo image
        size (tuple): ขนาดของภาพ QR Code
        
    Returns:
        PIL.Image: QR Code image พร้อม logo
    """
    # สร้าง QR Code พื้นฐาน
    qr_img = generate_qr_code_image(data, size, border=2)
    
    if logo_path:
        try:
            # เปิดภาพ logo
            logo = Image.open(logo_path)
            
            # คำนวณขนาด logo (ประมาณ 1/5 ของ QR Code)
            logo_size = min(size) // 5
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # สร้างพื้นหลังสีขาวสำหรับ logo
            logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
            logo_bg.paste(logo, (10, 10))
            
            # วาง logo ตรงกลาง QR Code
            pos = ((size[0] - logo_bg.size[0]) // 2, (size[1] - logo_bg.size[1]) // 2)
            qr_img.paste(logo_bg, pos)
            
        except Exception as e:
            # ถ้าไม่สามารถใส่ logo ได้ ให้ใช้ QR Code เปล่า
            print(f"Warning: Cannot add logo to QR code: {e}")
    
    return qr_img


def parse_qr_data(qr_data_string):
    """
    แปลงข้อมูล JSON string จาก QR Code กลับเป็น dict
    
    Args:
        qr_data_string (str): JSON string จาก QR Code
        
    Returns:
        dict: ข้อมูลที่แปลงแล้ว หรือ None ถ้าไม่สามารถแปลงได้
    """
    try:
        return json.loads(qr_data_string)
    except (json.JSONDecodeError, TypeError):
        return None


def validate_receipt_qr_data(qr_data):
    """
    ตรวจสอบความถูกต้องของข้อมูล QR Code ของใบสำคัญรับเงิน
    
    Args:
        qr_data (dict): ข้อมูลจาก QR Code
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['url', 'receipt_number', 'amount', 'date', 'hash']
    
    if not isinstance(qr_data, dict):
        return False, "ข้อมูล QR Code ไม่ถูกต้อง"
    
    # ตรวจสอบ fields ที่จำเป็น
    for field in required_fields:
        if field not in qr_data:
            return False, f"ข้อมูล QR Code ขาด field: {field}"
    
    # ตรวจสอบรูปแบบข้อมูล
    if not qr_data['receipt_number']:
        return False, "เลขที่ใบสำคัญรับเงินไม่ถูกต้อง"
    
    try:
        float(qr_data['amount'])
    except ValueError:
        return False, "จำนวนเงินไม่ถูกต้อง"
    
    return True, "ข้อมูล QR Code ถูกต้อง"


# Helper functions for PDF generation
def get_qr_code_for_pdf(receipt, size_mm=(25, 25), dpi=300):
    """
    สร้าง QR Code สำหรับใส่ใน PDF
    
    Args:
        receipt: Receipt model instance  
        size_mm (tuple): ขนาดใน millimeters
        dpi (int): DPI ของภาพ
        
    Returns:
        PIL.Image: QR Code image สำหรับ PDF
    """
    # คำนวณขนาดเป็น pixels
    mm_to_inch = 0.0393701
    width_px = int(size_mm[0] * mm_to_inch * dpi)
    height_px = int(size_mm[1] * mm_to_inch * dpi)
    
    return generate_qr_code_image(
        receipt.get_verification_url(), 
        size=(width_px, height_px),
        border=2
    )