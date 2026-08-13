"""
Seed script to create initial receipt templates
Run this script from the project root: python seed_templates.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import ReceiptTemplate

def create_templates():
    """สร้าง template 4 แบบเริ่มต้น"""

    # 1. รับเงินอื่น ๆ (textarea + amount)
    template1, created1 = ReceiptTemplate.objects.update_or_create(
        name="รับเงินอื่น ๆ",
        defaults={
            'input_type': 'textarea',
            'max_amount': None,  # ไม่จำกัด
            'sub_items': None,
            'is_active': True
        }
    )
    if created1:
        print("✓ สร้าง template: รับเงินอื่น ๆ")
    else:
        print("✓ อัพเดต template: รับเงินอื่น ๆ")

    # 2. รับคืนเงินเงินรับฝากอื่น (เงินส่วนเกิน) (textarea + amount)
    template2, created2 = ReceiptTemplate.objects.update_or_create(
        name="รับคืนเงินเงินรับฝากอื่น (เงินส่วนเกิน)",
        defaults={
            'input_type': 'textarea',
            'max_amount': None,  # ไม่จำกัด
            'sub_items': None,
            'is_active': True
        }
    )
    if created2:
        print("✓ สร้าง template: รับคืนเงินเงินรับฝากอื่น (เงินส่วนเกิน)")
    else:
        print("✓ อัพเดต template: รับคืนเงินเงินรับฝากอื่น (เงินส่วนเกิน)")

    # 3. รับคืนเงินค่าประกันของเสียหาย (amount only, max 1000)
    template3, created3 = ReceiptTemplate.objects.update_or_create(
        name="รับคืนเงินค่าประกันของเสียหาย",
        defaults={
            'input_type': 'simple',
            'max_amount': 1000.00,  # จำกัดไม่เกิน 1000 บาท
            'sub_items': None,
            'is_active': True
        }
    )
    if created3:
        print("✓ สร้าง template: รับคืนเงินค่าประกันของเสียหาย (max 1,000 บาท)")
    else:
        print("✓ อัพเดต template: รับคืนเงินค่าประกันของเสียหาย (max 1,000 บาท)")

    # 4. รับเงินค่าอาหาร (food calculation with 4 sub-items, max 2000)
    food_sub_items = {
        "items": [
            {
                "id": "breakfast",
                "name": "ค่าอาหารเช้า",
                "label": "อาหารเช้า",
                "fields": [
                    {"name": "meals", "label": "จำนวนมื้อ", "type": "number"},
                    {"name": "price_per_meal", "label": "มื้อละ", "type": "number"},
                    {"name": "people", "label": "จำนวนคน", "type": "number"},
                    {"name": "date", "label": "วันที่", "type": "date"}
                ]
            },
            {
                "id": "lunch",
                "name": "ค่าอาหารกลางวัน",
                "label": "อาหารกลางวัน",
                "fields": [
                    {"name": "meals", "label": "จำนวนมื้อ", "type": "number"},
                    {"name": "price_per_meal", "label": "มื้อละ", "type": "number"},
                    {"name": "people", "label": "จำนวนคน", "type": "number"},
                    {"name": "date", "label": "วันที่", "type": "date"}
                ]
            },
            {
                "id": "dinner",
                "name": "ค่าอาหารเย็น",
                "label": "อาหารเย็น",
                "fields": [
                    {"name": "meals", "label": "จำนวนมื้อ", "type": "number"},
                    {"name": "price_per_meal", "label": "มื้อละ", "type": "number"},
                    {"name": "people", "label": "จำนวนคน", "type": "number"},
                    {"name": "date", "label": "วันที่", "type": "date"}
                ]
            },
            {
                "id": "snack",
                "name": "ค่าอาหารว่าง",
                "label": "อาหารว่าง",
                "fields": [
                    {"name": "meals", "label": "จำนวนมื้อ", "type": "number"},
                    {"name": "price_per_meal", "label": "มื้อละ", "type": "number"},
                    {"name": "people", "label": "จำนวนคน", "type": "number"},
                    {"name": "date", "label": "วันที่", "type": "date"}
                ]
            }
        ],
        "calculation_formula": "meals * price_per_meal * people"
    }

    template4, created4 = ReceiptTemplate.objects.update_or_create(
        name="รับเงินค่าอาหาร",
        defaults={
            'input_type': 'food_calculation',
            'max_amount': 2000.00,  # จำกัดรวมไม่เกิน 2000 บาท
            'sub_items': food_sub_items,
            'is_active': True
        }
    )
    if created4:
        print("✓ สร้าง template: รับเงินค่าอาหาร (max 2,000 บาท)")
    else:
        print("✓ อัพเดต template: รับเงินค่าอาหาร (max 2,000 บาท)")

    print("\n" + "=" * 60)
    print("สรุป: สร้าง template ทั้งหมด 4 แบบเรียบร้อยแล้ว")
    print("=" * 60)
    print("\nรายการ template ทั้งหมด:")
    for template in ReceiptTemplate.objects.filter(is_active=True):
        print(f"  - {template.name} ({template.get_input_type_display()})")
        if template.max_amount:
            print(f"    Max: {template.max_amount:,.0f} บาท")

if __name__ == "__main__":
    print("=" * 60)
    print("เริ่มสร้างข้อมูล Receipt Templates")
    print("=" * 60)
    create_templates()
