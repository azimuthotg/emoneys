"""
Script to create missing DocumentVolumes for all departments
Run: python fix_missing_volumes.py
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import Department, DocumentVolume
from django.utils import timezone

print("=" * 80)
print("สร้าง Document Volumes สำหรับทุก Department")
print("=" * 80)

# Get current fiscal year (ปีงบประมาณ เริ่ม 1 ตุลาคม)
from utils.fiscal_year import get_current_fiscal_year

current_fy = get_current_fiscal_year()
print(f"\nปีงบประมาณปัจจุบัน: {current_fy}")

# Get all departments
departments = Department.objects.all()
print(f"จำนวน Department: {departments.count()}\n")

if departments.count() == 0:
    print("⚠️  ไม่มี Department ในระบบ!")
    exit(1)

created_volumes = []
existing_volumes = []

for dept in departments:
    print(f"\nตรวจสอบ Department: {dept.name} (Code: {dept.code})")

    # สร้าง volume code จาก fiscal year และ department code
    # รูปแบบ: MIT69, ARC69 เป็นต้น (ใช้ function get_volume_code)
    from utils.fiscal_year import get_volume_code
    volume_code = get_volume_code(dept.code, current_fy)

    # ตรวจสอบว่ามี Volume นี้อยู่แล้วหรือไม่
    existing = DocumentVolume.objects.filter(
        department=dept,
        fiscal_year=current_fy
    ).first()

    if existing:
        print(f"  ✅ มี Volume อยู่แล้ว: {existing.volume_code}")
        print(f"     - เริ่มต้น: {existing.fiscal_year_start}")
        print(f"     - สิ้นสุด: {existing.fiscal_year_end}")
        print(f"     - เลขล่าสุด: {existing.last_document_number}")
        print(f"     - สถานะ: {existing.get_status_display()}")
        existing_volumes.append(existing)
    else:
        # สร้าง Volume ใหม่
        # ปีงบประมาณ 2568 = 1 ต.ค. 2567 ถึง 30 ก.ย. 2568
        # ปีงบประมาณ 2568 = 1 ต.ค. 2024 ถึง 30 ก.ย. 2025
        fiscal_year_start = datetime(current_fy - 544, 10, 1).date()  # 1 ตุลาคม (พ.ศ. -> ค.ศ.)
        fiscal_year_end = datetime(current_fy - 543, 9, 30).date()    # 30 กันยายน

        # Get first staff user as creator (or None if no staff)
        from accounts.models import User
        creator = User.objects.filter(user_type='staff', is_active=True).first()

        volume = DocumentVolume.objects.create(
            department=dept,
            fiscal_year=current_fy,
            volume_code=volume_code,
            fiscal_year_start=fiscal_year_start,
            fiscal_year_end=fiscal_year_end,
            status='active',
            is_auto_generated=True,
            last_document_number=0,
            max_documents=9999,
            created_by=creator
        )

        print(f"  ✨ สร้าง Volume ใหม่: {volume.volume_code}")
        print(f"     - เริ่มต้น: {volume.fiscal_year_start}")
        print(f"     - สิ้นสุด: {volume.fiscal_year_end}")
        print(f"     - สถานะ: {volume.get_status_display()}")
        print(f"     - เลขเริ่มต้น: {volume.last_document_number}")
        created_volumes.append(volume)

# สรุปผล
print("\n" + "=" * 80)
print("สรุปผลการสร้าง Document Volumes")
print("=" * 80)
print(f"✅ Volume ที่มีอยู่แล้ว: {len(existing_volumes)} เล่ม")
print(f"✨ Volume ที่สร้างใหม่: {len(created_volumes)} เล่ม")
print(f"📊 Volume ทั้งหมดในระบบ: {DocumentVolume.objects.count()} เล่ม")

if created_volumes:
    print("\nรายการ Volume ที่สร้างใหม่:")
    for vol in created_volumes:
        print(f"  - {vol.volume_code} ({vol.department.name})")

print("\n✅ เสร็จสิ้น! ตอนนี้สามารถออกใบสำคัญรับเงินได้แล้ว")
print("=" * 80)
