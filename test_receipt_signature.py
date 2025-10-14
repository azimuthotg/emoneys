#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script สำหรับทดสอบ signature logic ในใบสำคัญรับเงิน
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import Receipt

def test_receipt_signature():
    """ทดสอบ logic ของ signature section"""
    print("=" * 70)
    print("ทดสอบ Signature Logic ในใบสำคัญรับเงิน")
    print("=" * 70)
    print()

    # ดึงใบสำคัญล่าสุด 5 รายการ
    receipts = Receipt.objects.all().order_by('-id')[:5]

    if not receipts:
        print("❌ ไม่พบใบสำคัญรับเงินในระบบ")
        return

    print(f"พบใบสำคัญ {receipts.count()} รายการ")
    print()

    for receipt in receipts:
        print("-" * 70)
        print(f"📄 ใบสำคัญ #{receipt.id}")
        print(f"   เลขที่: {receipt.receipt_number or 'ร่าง'}")
        print(f"   หน่วยงาน: {receipt.department.name}")
        print(f"   ผู้รับเงิน: {receipt.recipient_name}")
        print(f"   จำนวนเงิน: {receipt.total_amount:,.2f} บาท")
        print()
        print(f"   ประเภท: {'🤝 ยืมเงิน' if receipt.is_loan else '💰 จ่ายปกติ'}")
        print(f"   is_loan = {receipt.is_loan}")
        print()

        # แสดง logic ตาม is_loan
        if receipt.is_loan:
            recipient_signature = "..............................."
            payer_signature = receipt.created_by.get_display_name()
            print(f"   ✅ ผู้รับเงิน: {recipient_signature} (ว่าง)")
            print(f"   ✅ ผู้จ่ายเงิน: {payer_signature} (ชื่อผู้สร้าง)")
        else:
            recipient_signature = "..............................."
            payer_signature = "..............................."
            print(f"   ✅ ผู้รับเงิน: {recipient_signature} (ว่าง)")
            print(f"   ✅ ผู้จ่ายเงิน: {payer_signature} (ว่าง)")

        print()
        print(f"   👤 สร้างโดย: {receipt.created_by.get_display_name()}")
        print(f"   📅 สร้างเมื่อ: {receipt.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print()

    print("=" * 70)
    print("✅ ทดสอบเสร็จสิ้น")
    print()
    print("📝 สรุป Logic:")
    print("   - จ่ายปกติ (is_loan=False): ชื่อว่างทั้ง 2 คน")
    print("   - ยืมเงิน (is_loan=True): ผู้รับเงินว่าง, ผู้จ่าย=ชื่อผู้สร้าง")
    print("=" * 70)

if __name__ == '__main__':
    try:
        test_receipt_signature()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
