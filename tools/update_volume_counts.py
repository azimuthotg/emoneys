#!/usr/bin/env python
"""
Script สำหรับอัพเดท last_document_number ในทุก DocumentVolume
โดยนับจากใบสำคัญที่มีอยู่จริง
"""
import os
import django
import sys

# เพิ่ม project directory เข้าไปใน Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import DocumentVolume, Receipt
from django.db.models import Count, Q

def main():
    print("="*80)
    print("อัพเดท last_document_number ในทุก DocumentVolume")
    print("="*80)
    print()

    volumes = DocumentVolume.objects.all().select_related('department')

    if not volumes.exists():
        print("❌ ไม่พบ DocumentVolume ในระบบ")
        return

    print(f"พบ {volumes.count()} เล่มในระบบ\n")

    updated_count = 0
    no_change_count = 0

    for volume in volumes:
        # นับใบสำคัญที่เสร็จสิ้นแล้วในช่วงปีงบประมาณนี้
        receipt_count = Receipt.objects.filter(
            department=volume.department,
            status='completed',
            receipt_date__gte=volume.fiscal_year_start,
            receipt_date__lte=volume.fiscal_year_end
        ).count()

        old_count = volume.last_document_number

        if old_count != receipt_count:
            volume.last_document_number = receipt_count
            volume.save(update_fields=['last_document_number'])

            print(f"✅ อัพเดท: {volume.volume_code} ({volume.department.name})")
            print(f"   {old_count} → {receipt_count} ใบสำคัญ")
            updated_count += 1
        else:
            print(f"⚪ ไม่เปลี่ยนแปลง: {volume.volume_code} ({receipt_count} ใบสำคัญ)")
            no_change_count += 1

    print()
    print("="*80)
    print("สรุปผล")
    print("="*80)
    print(f"✅ อัพเดทแล้ว: {updated_count} เล่ม")
    print(f"⚪ ไม่เปลี่ยนแปลง: {no_change_count} เล่ม")
    print(f"📊 รวมทั้งหมด: {volumes.count()} เล่ม")
    print()
    print("✅ เสร็จสิ้น! ตอนนี้ข้อมูลในหน้า Document Numbering จะถูกต้องแล้ว")
    print("="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
