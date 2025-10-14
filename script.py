import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import Receipt

# ตรวจสอบข้อมูล Receipt ID 80
try:
    receipt = Receipt.objects.get(id=80)
    print("=" * 60)
    print("ข้อมูลใบสำคัญรับเงิน ID: 80")
    print("=" * 60)
    print(f"Receipt Number: {receipt.receipt_number}")
    print(f"Receipt Date: {receipt.receipt_date}")
    print(f"Receipt Date (raw): {repr(receipt.receipt_date)}")
    print(f"Created At: {receipt.created_at}")
    print(f"Status: {receipt.status}")
    print(f"Department: {receipt.department.name} ({receipt.department.code})")
    print(f"Recipient Name: {receipt.recipient_name}")
    print(f"Total Amount: {receipt.total_amount}")
    print("=" * 60)

    # ตรวจสอบว่ามีค่า None หรือไม่
    if receipt.receipt_date is None:
        print("⚠️ WARNING: receipt_date เป็น None!")
    else:
        print(f"✓ receipt_date มีค่า: {receipt.receipt_date}")
        print(f"✓ วันที่แบบไทย: {receipt.receipt_date.strftime('%d/%m/%Y')}")

except Receipt.DoesNotExist:
    print("❌ ไม่พบ Receipt ID: 80 ในฐานข้อมูล")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
