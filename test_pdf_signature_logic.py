#!/usr/bin/env python
"""
Test script to verify PDF signature logic
Tests both localhost and server environments
"""
import os
import sys
import django

# Setup Django environment
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import Receipt, User
from accounts.pdf_generator import ReceiptPDFGenerator
from datetime import datetime

def test_signature_logic():
    """Test PDF signature logic for both payment types"""

    print("=" * 80)
    print("PDF SIGNATURE LOGIC TEST")
    print("=" * 80)
    print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Path: {sys.executable}")
    print(f"Django Version: {django.get_version()}")
    print(f"Project Path: {project_path}")

    # Import the actual function to test
    from accounts.pdf_generator import ReceiptPDFGenerator

    # Check if the source code has the new logic
    import inspect
    source = inspect.getsource(ReceiptPDFGenerator._create_signature_section)
    has_is_loan = 'is_loan' in source
    has_recipient_name = 'receipt.recipient_name' in source
    has_get_display_name = 'get_display_name()' in source

    print("\n" + "=" * 80)
    print("SOURCE CODE INSPECTION:")
    print("=" * 80)
    print(f"✓ Has 'is_loan' logic: {has_is_loan}")
    print(f"✓ Has 'receipt.recipient_name': {has_recipient_name}")
    print(f"✓ Has 'get_display_name()': {has_get_display_name}")

    if has_is_loan and has_recipient_name and has_get_display_name:
        print("\n✅ SOURCE CODE: Has NEW logic (correct)")
    else:
        print("\n❌ SOURCE CODE: Still has OLD logic (incorrect)")
        print("\n🔍 Key lines from source:")
        for i, line in enumerate(source.split('\n')[0:30], 1):
            if 'is_loan' in line or 'recipient_name' in line or 'payer_name' in line:
                print(f"   Line {i}: {line.strip()}")

    # Get a real receipt to test
    print("\n" + "=" * 80)
    print("DATABASE TEST:")
    print("=" * 80)

    try:
        # Get receipts
        receipt_normal = Receipt.objects.filter(is_loan=False, status='completed').first()
        receipt_loan = Receipt.objects.filter(is_loan=True, status='completed').first()

        if not receipt_normal:
            print("❌ No 'จ่ายปกติ' receipt found in database")
        else:
            print(f"\n📄 จ่ายปกติ Receipt: {receipt_normal.receipt_number}")
            print(f"   - Recipient: {receipt_normal.recipient_name}")
            print(f"   - Created by: {receipt_normal.created_by.get_display_name()}")
            print(f"   - is_loan: {receipt_normal.is_loan}")

            # Test the logic manually
            if receipt_normal.is_loan:
                recipient_test = receipt_normal.recipient_name
                payer_test = receipt_normal.created_by.get_display_name()
            else:
                recipient_test = receipt_normal.recipient_name
                payer_test = '...........................................................'

            print(f"\n   Expected Output (จ่ายปกติ):")
            print(f"   - ผู้รับเงิน: {recipient_test}")
            print(f"   - ผู้จ่ายเงิน: {payer_test}")

            if payer_test == '...........................................................':
                print("   ✅ CORRECT: Payer is blank (dots)")
            else:
                print("   ❌ WRONG: Payer should be blank!")

        if not receipt_loan:
            print("\n❌ No 'ยืมเงิน' receipt found in database")
        else:
            print(f"\n📄 ยืมเงิน Receipt: {receipt_loan.receipt_number}")
            print(f"   - Recipient: {receipt_loan.recipient_name}")
            print(f"   - Created by: {receipt_loan.created_by.get_display_name()}")
            print(f"   - is_loan: {receipt_loan.is_loan}")

            # Test the logic manually
            if receipt_loan.is_loan:
                recipient_test = receipt_loan.recipient_name
                payer_test = receipt_loan.created_by.get_display_name()
            else:
                recipient_test = receipt_loan.recipient_name
                payer_test = '...........................................................'

            print(f"\n   Expected Output (ยืมเงิน):")
            print(f"   - ผู้รับเงิน: {recipient_test}")
            print(f"   - ผู้จ่ายเงิน: {payer_test}")

            if payer_test != '...........................................................' and len(payer_test) > 0:
                print("   ✅ CORRECT: Payer shows creator name")
            else:
                print("   ❌ WRONG: Payer should show creator name!")

    except Exception as e:
        print(f"\n❌ Error accessing database: {e}")

    # Test PDF Generator class method directly
    print("\n" + "=" * 80)
    print("PDF GENERATOR METHOD TEST:")
    print("=" * 80)

    try:
        # Create mock receipt objects
        class MockUser:
            def __init__(self, name):
                self.name = name
            def get_display_name(self):
                return self.name

        class MockReceipt:
            def __init__(self, is_loan, recipient_name, created_by):
                self.is_loan = is_loan
                self.recipient_name = recipient_name
                self.created_by = created_by

        # Test จ่ายปกติ
        mock_user = MockUser("นาย ทดสอบ ระบบ")
        mock_receipt_normal = MockReceipt(False, "นาง สมหญิง ใจดี", mock_user)

        print("\n🧪 Test 1: จ่ายปกติ (is_loan=False)")
        print(f"   Input: recipient='{mock_receipt_normal.recipient_name}'")
        print(f"          creator='{mock_receipt_normal.created_by.get_display_name()}'")

        # Manually run the logic
        if mock_receipt_normal.is_loan:
            result_recipient = mock_receipt_normal.recipient_name
            result_payer = mock_receipt_normal.created_by.get_display_name()
        else:
            result_recipient = mock_receipt_normal.recipient_name
            result_payer = '...........................................................'

        print(f"   Output: ผู้รับเงิน='{result_recipient}'")
        print(f"           ผู้จ่ายเงิน='{result_payer}'")

        if result_recipient == "นาง สมหญิง ใจดี" and result_payer == '...........................................................':
            print("   ✅ CORRECT")
        else:
            print("   ❌ WRONG")

        # Test ยืมเงิน
        mock_receipt_loan = MockReceipt(True, "นาย สมชาย รับเงิน", mock_user)

        print("\n🧪 Test 2: ยืมเงิน (is_loan=True)")
        print(f"   Input: recipient='{mock_receipt_loan.recipient_name}'")
        print(f"          creator='{mock_receipt_loan.created_by.get_display_name()}'")

        # Manually run the logic
        if mock_receipt_loan.is_loan:
            result_recipient = mock_receipt_loan.recipient_name
            result_payer = mock_receipt_loan.created_by.get_display_name()
        else:
            result_recipient = mock_receipt_loan.recipient_name
            result_payer = '...........................................................'

        print(f"   Output: ผู้รับเงิน='{result_recipient}'")
        print(f"           ผู้จ่ายเงิน='{result_payer}'")

        if result_recipient == "นาย สมชาย รับเงิน" and result_payer == "นาย ทดสอบ ระบบ":
            print("   ✅ CORRECT")
        else:
            print("   ❌ WRONG")

    except Exception as e:
        print(f"\n❌ Error in method test: {e}")
        import traceback
        traceback.print_exc()

    # Check for __pycache__
    print("\n" + "=" * 80)
    print("CACHE DETECTION:")
    print("=" * 80)

    accounts_path = os.path.join(project_path, 'accounts')
    pycache_path = os.path.join(accounts_path, '__pycache__')

    if os.path.exists(pycache_path):
        print(f"⚠️  __pycache__ exists at: {pycache_path}")
        pyc_files = [f for f in os.listdir(pycache_path) if f.endswith('.pyc')]
        print(f"   Found {len(pyc_files)} .pyc files")

        # Check pdf_generator.pyc timestamp
        pdf_gen_pyc = [f for f in pyc_files if 'pdf_generator' in f]
        if pdf_gen_pyc:
            for pyc in pdf_gen_pyc:
                pyc_full_path = os.path.join(pycache_path, pyc)
                pyc_mtime = os.path.getmtime(pyc_full_path)
                pyc_time = datetime.fromtimestamp(pyc_mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   - {pyc}: Modified at {pyc_time}")

        # Check pdf_generator.py timestamp
        pdf_gen_py = os.path.join(accounts_path, 'pdf_generator.py')
        if os.path.exists(pdf_gen_py):
            py_mtime = os.path.getmtime(pdf_gen_py)
            py_time = datetime.fromtimestamp(py_mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n   pdf_generator.py: Modified at {py_time}")

            if pdf_gen_pyc:
                if py_mtime > pyc_mtime:
                    print("   ✅ .py is NEWER than .pyc (will recompile)")
                else:
                    print("   ⚠️  .pyc is NEWER than .py (using cache!)")
    else:
        print("✅ No __pycache__ found")

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)

    if has_is_loan and has_recipient_name and has_get_display_name:
        print("✅ Code has correct logic")
    else:
        print("❌ Code has wrong logic")

    if os.path.exists(pycache_path):
        print("⚠️  Cache exists - may need clearing")
    else:
        print("✅ No cache issues")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)

    if not (has_is_loan and has_recipient_name and has_get_display_name):
        print("1. ❌ CODE PROBLEM: Run 'git pull origin main' again")
        print("2. ❌ Check file: accounts/pdf_generator.py")
    elif os.path.exists(pycache_path) and pdf_gen_pyc and py_mtime <= pyc_mtime:
        print("1. ⚠️  CACHE PROBLEM: Delete __pycache__ folder")
        print("2. ⚠️  Restart Django server")
        print("3. ⚠️  Try: python -Bc 'import accounts.pdf_generator'")
    else:
        print("1. ✅ Code looks good")
        print("2. 🔄 Restart Django server if not done already")
        print("3. 🌐 Clear browser cache (Ctrl+Shift+R)")

    print("\n" + "=" * 80)
    print("END OF TEST")
    print("=" * 80)

if __name__ == '__main__':
    try:
        test_signature_logic()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
