#!/usr/bin/env python
"""
Back Test Script - ทดสอบระบบ DocumentVolume และ Receipt
ตรวจสอบว่า code ที่แก้ไขทำงานถูกต้องกับข้อมูลที่มีอยู่
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

from accounts.models import DocumentVolume, Receipt, Department
from utils.fiscal_year import get_volume_code, get_current_fiscal_year, get_fiscal_year_from_date
from datetime import datetime

def test_volume_code_format():
    """ทดสอบว่า volume_code มีรูปแบบถูกต้อง (MIT69, PO69)"""
    print("\n" + "="*80)
    print("TEST 1: ตรวจสอบรูปแบบ volume_code")
    print("="*80)

    volumes = DocumentVolume.objects.all()
    passed = 0
    failed = 0

    for vol in volumes:
        # ตรวจสอบว่า volume_code ไม่มี prefix ปีงบ (ไม่มี 2569-)
        expected_code = get_volume_code(vol.department.code, vol.fiscal_year)

        if vol.volume_code == expected_code:
            print(f"  ✅ {vol.volume_code} - {vol.department.name}")
            passed += 1
        else:
            print(f"  ❌ {vol.volume_code} ≠ {expected_code} - {vol.department.name}")
            failed += 1

    print(f"\n  ผลลัพธ์: ✅ {passed} / ❌ {failed}")
    return failed == 0

def test_volume_counts_accuracy():
    """ทดสอบว่า last_document_number ตรงกับจำนวนใบสำคัญจริง"""
    print("\n" + "="*80)
    print("TEST 2: ตรวจสอบความถูกต้องของ last_document_number")
    print("="*80)

    volumes = DocumentVolume.objects.all()
    passed = 0
    failed = 0

    for vol in volumes:
        # นับใบสำคัญจริง
        actual_count = Receipt.objects.filter(
            department=vol.department,
            status='completed',
            receipt_date__gte=vol.fiscal_year_start,
            receipt_date__lte=vol.fiscal_year_end
        ).count()

        if vol.last_document_number == actual_count:
            print(f"  ✅ {vol.volume_code}: {vol.last_document_number} ใบสำคัญ")
            passed += 1
        else:
            print(f"  ❌ {vol.volume_code}: last_document_number={vol.last_document_number} แต่มีจริง={actual_count}")
            failed += 1

    print(f"\n  ผลลัพธ์: ✅ {passed} / ❌ {failed}")
    return failed == 0

def test_receipt_volume_code_property():
    """ทดสอบว่า Receipt.volume_code (@property) ทำงานถูกต้อง"""
    print("\n" + "="*80)
    print("TEST 3: ตรวจสอบ Receipt.volume_code (@property)")
    print("="*80)

    receipts = Receipt.objects.filter(status='completed').select_related('department')[:10]
    passed = 0
    failed = 0

    for receipt in receipts:
        # คำนวณ volume_code ที่ถูกต้อง
        if receipt.receipt_date:
            fiscal_year = get_fiscal_year_from_date(receipt.receipt_date)
            expected_code = get_volume_code(receipt.department.code, fiscal_year)

            if receipt.volume_code == expected_code:
                print(f"  ✅ {receipt.receipt_number}: volume_code={receipt.volume_code}")
                passed += 1
            else:
                print(f"  ❌ {receipt.receipt_number}: {receipt.volume_code} ≠ {expected_code}")
                failed += 1

    print(f"\n  ผลลัพธ์: ✅ {passed} / ❌ {failed}")
    return failed == 0

def test_departments_without_volumes():
    """ทดสอบว่ามีหน่วยงานที่มีใบสำคัญแต่ไม่มีเล่มหรือไม่"""
    print("\n" + "="*80)
    print("TEST 4: ตรวจสอบหน่วยงานที่ขาดเล่ม")
    print("="*80)

    current_fy = get_current_fiscal_year()

    # หาหน่วยงานที่มีใบสำคัญ
    departments_with_receipts = Receipt.objects.filter(
        status='completed'
    ).values_list('department_id', flat=True).distinct()

    # หาหน่วยงานที่มีเล่ม
    departments_with_volumes = DocumentVolume.objects.filter(
        fiscal_year=current_fy
    ).values_list('department_id', flat=True)

    # หาหน่วยงานที่มีใบสำคัญแต่ไม่มีเล่ม
    missing = set(departments_with_receipts) - set(departments_with_volumes)

    if len(missing) == 0:
        print("  ✅ ทุกหน่วยงานที่มีใบสำคัญมีเล่มครบแล้ว")
        return True
    else:
        print(f"  ⚠️  พบ {len(missing)} หน่วยงานที่มีใบสำคัญแต่ไม่มีเล่ม:")
        for dept_id in missing:
            dept = Department.objects.get(id=dept_id)
            count = Receipt.objects.filter(department=dept, status='completed').count()
            print(f"     - {dept.name} ({dept.code}): {count} ใบสำคัญ")
        print("\n  💡 รัน: python fix_missing_volumes.py เพื่อสร้างเล่มให้")
        return False

def test_receipt_number_format():
    """ทดสอบว่าเลขที่ใบสำคัญมีรูปแบบถูกต้อง (ddmmyy/xxxx)"""
    print("\n" + "="*80)
    print("TEST 5: ตรวจสอบรูปแบบเลขที่ใบสำคัญ")
    print("="*80)

    receipts = Receipt.objects.filter(status='completed').exclude(receipt_number__isnull=True)[:10]
    passed = 0
    failed = 0

    import re
    pattern = re.compile(r'^\d{6}/\d{4}$')

    for receipt in receipts:
        if pattern.match(receipt.receipt_number):
            print(f"  ✅ {receipt.receipt_number} - {receipt.department.code}")
            passed += 1
        else:
            print(f"  ❌ {receipt.receipt_number} - รูปแบบไม่ถูกต้อง")
            failed += 1

    print(f"\n  ผลลัพธ์: ✅ {passed} / ❌ {failed}")
    return failed == 0

def main():
    print("="*80)
    print("🧪 BACK TEST - ทดสอบระบบ DocumentVolume และ Receipt")
    print("="*80)
    print(f"วันที่ทดสอบ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"ปีงบประมาณปัจจุบัน: {get_current_fiscal_year()}")

    # รัน tests
    test_results = []

    test_results.append(("รูปแบบ volume_code", test_volume_code_format()))
    test_results.append(("ความถูกต้อง last_document_number", test_volume_counts_accuracy()))
    test_results.append(("Receipt.volume_code property", test_receipt_volume_code_property()))
    test_results.append(("หน่วยงานที่ขาดเล่ม", test_departments_without_volumes()))
    test_results.append(("รูปแบบเลขที่ใบสำคัญ", test_receipt_number_format()))

    # สรุปผล
    print("\n" + "="*80)
    print("📊 สรุปผลการทดสอบ")
    print("="*80)

    passed_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print("\n" + "-"*80)
    print(f"  ผ่าน: {passed_count}/{total_count} tests")

    if passed_count == total_count:
        print("\n  🎉 ทุก tests ผ่านหมด! ระบบทำงานถูกต้อง")
    else:
        print("\n  ⚠️  มี tests ที่ไม่ผ่าน กรุณาตรวจสอบและแก้ไข")

    print("="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
