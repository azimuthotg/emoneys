#!/usr/bin/env python
"""
Script สำหรับตรวจสอบใบสำคัญที่มีแต่ไม่มีเล่มใน DocumentVolume
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

from accounts.models import Receipt, DocumentVolume, Department
from utils.fiscal_year import get_current_fiscal_year

def main():
    print("="*80)
    print("ตรวจสอบใบสำคัญและเล่มเอกสาร")
    print("="*80)
    print()

    current_fy = get_current_fiscal_year()
    print(f"ปีงบประมาณปัจจุบัน: {current_fy}\n")

    # ตรวจสอบเล่มทั้งหมด
    volumes = DocumentVolume.objects.filter(fiscal_year=current_fy).select_related('department')
    print(f"📚 เล่มในระบบ ({volumes.count()} เล่ม):")
    print("-" * 80)
    for vol in volumes:
        print(f"  ✅ {vol.volume_code} - {vol.department.name} ({vol.department.code})")
        print(f"     เอกสารล่าสุด: {vol.last_document_number}/{vol.max_documents}")

    print()

    # ตรวจสอบใบสำคัญทั้งหมด
    receipts = Receipt.objects.filter(status='completed').select_related('department').order_by('-created_at')[:20]

    print(f"📄 ใบสำคัญล่าสุด ({receipts.count()} ใบ):")
    print("-" * 80)

    departments_with_receipts = set()
    for receipt in receipts:
        dept = receipt.department
        departments_with_receipts.add(dept.code)

        # เช็คว่ามีเล่มหรือไม่
        volume_exists = DocumentVolume.objects.filter(
            department=dept,
            fiscal_year=current_fy
        ).exists()

        status = "✅" if volume_exists else "❌"
        print(f"  {status} {receipt.receipt_number} - {dept.name} ({dept.code})")
        print(f"     เล่มที่: {receipt.volume_code} - มีในระบบ: {'ใช่' if volume_exists else 'ไม่'}")

    print()
    print("="*80)
    print("สรุป")
    print("="*80)

    # หาหน่วยงานที่มีใบสำคัญแต่ไม่มีเล่ม
    departments_with_volumes = set(volumes.values_list('department__code', flat=True))
    departments_missing_volumes = departments_with_receipts - departments_with_volumes

    if departments_missing_volumes:
        print(f"\n⚠️  หน่วยงานที่มีใบสำคัญแต่ไม่มีเล่ม ({len(departments_missing_volumes)} หน่วยงาน):")
        for dept_code in departments_missing_volumes:
            try:
                dept = Department.objects.get(code=dept_code)
                receipt_count = Receipt.objects.filter(
                    department=dept,
                    status='completed'
                ).count()
                print(f"  ❌ {dept.name} ({dept_code}) - มี {receipt_count} ใบสำคัญ")
            except Department.DoesNotExist:
                print(f"  ❌ {dept_code} - หาข้อมูลไม่เจอ")

        print("\n💡 วิธีแก้:")
        print("  1. รัน fix_missing_volumes.py เพื่อสร้างเล่มให้หน่วยงานที่ขาด")
        print("  2. หรือระบบจะสร้างเล่มอัตโนมัติเมื่อออกใบสำคัญใหม่")
    else:
        print("\n✅ ทุกหน่วยงานที่มีใบสำคัญมีเล่มครบแล้ว")

    print("="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
