#!/usr/bin/env python
"""
Script สำหรับตรวจสอบ volume_code ใน database
และเปรียบเทียบกับรูปแบบที่ถูกต้อง
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

from accounts.models import DocumentVolume, Department
from utils.fiscal_year import get_volume_code

def main():
    print("="*80)
    print("ตรวจสอบ volume_code ใน Database")
    print("="*80)
    print()

    volumes = DocumentVolume.objects.all().select_related('department').order_by('fiscal_year', 'department__code')

    if not volumes.exists():
        print("❌ ไม่พบข้อมูล DocumentVolume ในระบบ")
        return

    print(f"พบ {volumes.count()} เล่มในระบบ\n")

    issues_found = []
    correct_count = 0

    for vol in volumes:
        # คำนวณ volume_code ที่ถูกต้องตามฟังก์ชัน get_volume_code()
        correct_code = get_volume_code(vol.department.code, vol.fiscal_year)
        current_code = vol.volume_code

        is_correct = current_code == correct_code
        status_icon = "✅" if is_correct else "❌"

        print(f"{status_icon} ID: {vol.id}")
        print(f"   หน่วยงาน: {vol.department.name} ({vol.department.code})")
        print(f"   ปีงบประมาณ: {vol.fiscal_year}")
        print(f"   Volume Code ปัจจุบัน: {current_code}")

        if not is_correct:
            print(f"   ❗ ควรเป็น: {correct_code}")
            issues_found.append({
                'id': vol.id,
                'current': current_code,
                'correct': correct_code,
                'department': vol.department.name
            })
        else:
            correct_count += 1

        print()

    print("="*80)
    print("สรุปผลการตรวจสอบ")
    print("="*80)
    print(f"✅ ถูกต้อง: {correct_count} เล่ม")
    print(f"❌ ผิดพลาด: {len(issues_found)} เล่ม")
    print()

    if issues_found:
        print("📋 รายการที่ต้องแก้ไข:")
        print("-" * 80)
        for issue in issues_found:
            print(f"  - ID {issue['id']}: {issue['department']}")
            print(f"    ปัจจุบัน: {issue['current']} → ควรเป็น: {issue['correct']}")
        print()
        print("💡 แนะนำ:")
        print("  1. รันสคริปต์ fix_volume_codes.py เพื่อแก้ไขอัตโนมัติ")
        print("  2. ตรวจสอบว่า Receipt ที่มีอยู่ใช้ @property volume_code (ดึงจาก function)")
        print("  3. ตรวจสอบว่า template แสดงจาก receipt.volume_code ไม่ใช่ volume.volume_code")
    else:
        print("🎉 ไม่พบปัญหา! volume_code ทั้งหมดถูกต้องแล้ว")

    print("="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
