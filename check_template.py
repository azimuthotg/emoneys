"""
Check template data in database
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import ReceiptTemplate

print("=" * 80)
print("ตรวจสอบข้อมูล Templates ในฐานข้อมูล")
print("=" * 80)

templates = ReceiptTemplate.objects.filter(is_active=True).order_by('name')

for template in templates:
    print(f"\nTemplate: {template.name}")
    print(f"  ID: {template.id}")
    print(f"  Input Type: {template.input_type}")
    print(f"  Max Amount: {template.max_amount}")
    print(f"  Sub Items Type: {type(template.sub_items)}")
    print(f"  Sub Items: {template.sub_items}")

    if template.input_type == 'food_calculation':
        print("\n  >>> Food Calculation Template Details:")
        if template.sub_items:
            print(f"      Raw sub_items: {json.dumps(template.sub_items, indent=6, ensure_ascii=False)}")
            if 'items' in template.sub_items:
                print(f"      Number of items: {len(template.sub_items['items'])}")
                for item in template.sub_items['items']:
                    print(f"        - {item.get('id')}: {item.get('name')}")
        else:
            print("      ❌ No sub_items data!")

print("\n" + "=" * 80)
