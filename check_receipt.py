import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import Receipt

# ตรวจสอบใบสำคัญเลขที่ 091025/0003
receipt_number = '091025/0003'

receipts = Receipt.objects.filter(receipt_number=receipt_number)
print(f"\n=== ตรวจสอบใบสำคัญเลขที่: {receipt_number} ===")
print(f"พบทั้งหมด: {receipts.count()} ใบ\n")

if receipts.count() > 0:
    for idx, r in enumerate(receipts, 1):
        print(f"ใบที่ {idx}:")
        print(f"  - ID: {r.id}")
        print(f"  - หน่วยงาน: {r.department.name}")
        print(f"  - รหัสหน่วยงาน: {r.department.code}")
        print(f"  - สถานะ: {r.get_status_display()}")
        print(f"  - ผู้สร้าง: {r.created_by.get_display_name()}")
        print(f"  - วันที่: {r.receipt_date}")
        print(f"  - จำนวนเงิน: {r.total_amount} บาท")
        print(f"  - URL ใหม่: /check/{r.department.code}/{receipt_number}/")
        print()
else:
    print("ไม่พบใบสำคัญเลขที่นี้ในระบบ")

print("=" * 50)
