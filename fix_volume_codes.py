#!/usr/bin/env python
"""
Script สำหรับแก้ไข volume_code ใน database
จาก "2569-MIT" เป็น "MIT69" (ตามฟังก์ชัน get_volume_code)
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
from utils.fiscal_year import get_volume_code
from django.db import transaction

def main():
    print("="*80)
    print("แก้ไข volume_code ใน Database")
    print("="*80)
    print()

    volumes = DocumentVolume.objects.all().select_related('department').order_by('fiscal_year', 'department__code')

    if not volumes.exists():
        print("❌ ไม่พบข้อมูล DocumentVolume ในระบบ")
        return

    print(f"พบ {volumes.count()} เล่มในระบบ")
    print()

    updates_needed = []

    # ตรวจสอบว่ามีเล่มไหนต้องแก้ไขบ้าง
    for vol in volumes:
        correct_code = get_volume_code(vol.department.code, vol.fiscal_year)
        current_code = vol.volume_code

        if current_code != correct_code:
            updates_needed.append({
                'volume': vol,
                'old_code': current_code,
                'new_code': correct_code
            })

    if not updates_needed:
        print("✅ ไม่พบปัญหา! volume_code ทั้งหมดถูกต้องแล้ว")
        return

    print(f"พบ {len(updates_needed)} เล่มที่ต้องแก้ไข:")
    print("-" * 80)
    for item in updates_needed:
        vol = item['volume']
        print(f"  📝 ID {vol.id}: {vol.department.name}")
        print(f"     {item['old_code']} → {item['new_code']}")
    print()

    # ถามผู้ใช้ว่าต้องการดำเนินการหรือไม่
    confirm = input("ต้องการดำเนินการแก้ไขหรือไม่? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("❌ ยกเลิกการแก้ไข")
        return

    print()
    print("🔄 กำลังดำเนินการแก้ไข...")
    print()

    try:
        with transaction.atomic():
            for item in updates_needed:
                vol = item['volume']
                old_code = item['old_code']
                new_code = item['new_code']

                # อัพเดท volume_code
                vol.volume_code = new_code
                vol.save(update_fields=['volume_code'])

                print(f"✅ อัพเดท ID {vol.id}: {old_code} → {new_code}")

            print()
            print("="*80)
            print(f"✅ แก้ไขสำเร็จ! อัพเดท {len(updates_needed)} เล่ม")
            print("="*80)
            print()
            print("📋 ขั้นตอนถัดไป:")
            print("  1. รีเฟรชหน้า Document Numbering เพื่อดูผลลัพธ์")
            print("  2. ตรวจสอบ PDF ใบเสร็จที่ http://localhost:8002/receipt/110/pdf/")
            print("  3. ตรวจสอบว่า เล่มที่ แสดงเป็น MIT69 หรือ PO69 อย่างถูกต้อง")
            print()
            print("💡 หมายเหตุ:")
            print("  - Receipt model ใช้ @property volume_code ที่คำนวณจาก department.code + ปีงบ")
            print("  - PDF และ template ควรแสดง receipt.volume_code (computed) ไม่ใช่ volume.volume_code")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ ยกเลิกการทำงานโดยผู้ใช้")
        sys.exit(1)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
