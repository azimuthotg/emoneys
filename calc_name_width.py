#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""คำนวณความกว้างชื่อสำหรับเลือก template ข้อความรับรอง"""

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import os

# ลงทะเบียนฟอนต์
font_path = 'static/fonts/THSarabunNew.ttf'
font_bold_path = 'static/fonts/THSarabunNew Bold.ttf'

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))
    pdfmetrics.registerFont(TTFont('THSarabunNew-Bold', font_bold_path))
    thai_font = 'THSarabunNew'
    thai_font_bold = 'THSarabunNew-Bold'
else:
    thai_font = 'Helvetica'
    thai_font_bold = 'Helvetica-Bold'

print(f"ใช้ฟอนต์: {thai_font}\n")

# ชื่อคนธรรมดาแบบยาว
prefix_name = 'นายภูวเดช ขจรศักดิ์ขจรศักดิ์'
recipient_name = 'นางสาวรัตนา แสงเพชรแสงเพชร'

# คำนวณความกว้าง
prefix_width = pdfmetrics.stringWidth(prefix_name, thai_font_bold, 14)
recipient_width = pdfmetrics.stringWidth(recipient_name, thai_font_bold, 14)
intro_text_width = pdfmetrics.stringWidth('ข้าพเจ้า  ขอรับรองว่า  ', thai_font, 14)

total_width = prefix_width + recipient_width + intro_text_width

# พื้นที่ที่มี
available = (21 - 4 - 1.27) * cm

print("=" * 65)
print("คำนวณความกว้างชื่อ - คนธรรมดาแบบยาว")
print("=" * 65)
print(f"\nผู้รับรอง: {prefix_name}")
print(f"  ความกว้าง = {prefix_width:.2f} points ({prefix_width/cm:.2f} cm)")

print(f"\nผู้รับเงิน: {recipient_name}")
print(f"  ความกว้าง = {recipient_width:.2f} points ({recipient_width/cm:.2f} cm)")

print(f"\nข้อความนำ: 'ข้าพเจ้า  ขอรับรองว่า  '")
print(f"  ความกว้าง = {intro_text_width:.2f} points ({intro_text_width/cm:.2f} cm)")

print("\n" + "=" * 65)
print(f"รวมทั้งหมด = {total_width:.2f} points ({total_width/cm:.2f} cm)")
print("=" * 65)

print(f"\nพื้นที่บรรทัดแรกที่มี = {available:.2f} points ({available/cm:.2f} cm)")

if total_width > available:
    print(f"\n⚠️  ชื่อยาวเกิน {(total_width - available):.2f} points ({(total_width - available)/cm:.2f} cm)")
    percent = (total_width / available) * 100
    print(f"    ใช้พื้นที่ {percent:.1f}% ของบรรทัดแรก")
else:
    print(f"\n✓  พอดีในบรรทัดแรก")
    print(f"    เหลือที่ว่าง {(available - total_width):.2f} points ({(available - total_width)/cm:.2f} cm)")
    percent = (total_width / available) * 100
    print(f"    ใช้พื้นที่ {percent:.1f}% ของบรรทัดแรก")

print("\n" + "=" * 65)
