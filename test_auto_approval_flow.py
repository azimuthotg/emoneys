#!/usr/bin/env python
"""
Test script to verify auto-approval functionality
Simulates the authentication flow and checks that users are auto-approved
"""
import os
import sys
import django

# Setup Django
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import User, Role, UserRole
from accounts.backends import HybridAuthBackend
from datetime import datetime


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_backend_logic():
    """Test the auto-approval logic in the backend"""
    print_header("AUTO-APPROVAL SYSTEM TEST")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Check if Basic User role exists
    print_header("1. CHECK BASIC USER ROLE")
    try:
        basic_role = Role.objects.get(name='basic_user', is_active=True)
        print(f"✅ Found 'basic_user' role: {basic_role.display_name}")
        print(f"   Description: {basic_role.description}")
    except Role.DoesNotExist:
        print("❌ ERROR: 'basic_user' role not found!")
        print("   Please create the role first.")
        return False

    # 2. Test the backend's _create_pending_user method
    print_header("2. TEST BACKEND CODE INSPECTION")
    backend = HybridAuthBackend()

    # Check if the method exists and has the right signature
    import inspect
    source = inspect.getsource(backend._create_pending_user)

    # Check for key changes
    has_approved_status = "approval_status='approved'" in source
    has_is_active_true = "is_active=True" in source
    has_approved_at = "approved_at=timezone.now()" in source
    has_role_assignment = "assign_role" in source
    has_basic_user = "basic_user" in source

    print("\nCode inspection results:")
    print(f"   {'✅' if has_approved_status else '❌'} approval_status='approved'")
    print(f"   {'✅' if has_is_active_true else '❌'} is_active=True")
    print(f"   {'✅' if has_approved_at else '❌'} approved_at=timezone.now()")
    print(f"   {'✅' if has_role_assignment else '❌'} Role assignment code present")
    print(f"   {'✅' if has_basic_user else '❌'} Basic User role reference")

    all_checks_pass = all([
        has_approved_status,
        has_is_active_true,
        has_approved_at,
        has_role_assignment,
        has_basic_user
    ])

    if all_checks_pass:
        print("\n✅ All code checks PASSED! Auto-approval logic is implemented.")
    else:
        print("\n❌ Some code checks FAILED! Please verify the implementation.")
        return False

    # 3. Check docstring
    print_header("3. CHECK DOCUMENTATION")
    class_source = inspect.getsource(HybridAuthBackend)
    if "auto-approval" in class_source.lower() or "auto-approve" in class_source.lower():
        print("✅ Documentation mentions auto-approval")
    else:
        print("⚠️  Documentation might need updating")

    # 4. Simulate user creation (without actual NPU API call)
    print_header("4. SIMULATE USER CREATION")
    print("\nThis test simulates what happens when a new user authenticates")
    print("via NPU API for the first time.\n")

    # Create mock user data (similar to what NPU API would return)
    mock_user_data = {
        'username': 'test_auto_approval_user',
        'ldap_uid': '9999999999999',
        'npu_staff_id': 'TEST001',
        'prefix_name': 'นาย',
        'first_name_th': 'ทดสอบ',
        'last_name_th': 'ระบบ',
        'full_name': 'นาย ทดสอบ ระบบอัตโนมัติ',
        'department': 'สำนักทดสอบระบบ',
        'position_title': 'เจ้าหน้าที่ทดสอบ',
        'staff_type': 'พนักงานทดสอบ',
        'employment_status': 'ปฏิบัติงาน',
    }

    # Check if test user already exists
    test_user = User.objects.filter(ldap_uid=mock_user_data['ldap_uid']).first()
    if test_user:
        print(f"⚠️  Test user already exists (ID: {test_user.id})")
        print(f"   Status: {test_user.approval_status}")
        print(f"   Active: {test_user.is_active}")
        print(f"   Approved at: {test_user.approved_at}")

        # Check roles
        roles = test_user.get_roles()
        role_names = ', '.join([r.display_name for r in roles])
        print(f"   Roles: {role_names or 'None'}")

        # Clean up
        print("\n   Deleting test user for fresh test...")
        UserRole.objects.filter(user=test_user).delete()
        test_user.delete()
        print("   ✅ Test user deleted")

    # Create user using backend method
    print("\nCreating new user via backend._create_pending_user()...")
    backend = HybridAuthBackend()
    new_user = backend._create_pending_user(mock_user_data)

    if not new_user:
        print("❌ Failed to create user!")
        return False

    print(f"✅ User created successfully (ID: {new_user.id})")

    # 5. Verify user properties
    print_header("5. VERIFY USER PROPERTIES")

    # Reload user from database
    test_user = User.objects.get(id=new_user.id)

    print(f"\nUser: {test_user.get_display_name()}")
    print(f"   LDAP UID: {test_user.ldap_uid}")
    print(f"   Department: {test_user.department}")
    print(f"   Approval Status: {test_user.approval_status}")
    print(f"   Is Active: {test_user.is_active}")
    print(f"   Approved At: {test_user.approved_at}")

    # Check approval status
    checks = []

    if test_user.approval_status == 'approved':
        print("\n   ✅ User is APPROVED (not pending)")
        checks.append(True)
    else:
        print(f"\n   ❌ User status is '{test_user.approval_status}' (should be 'approved')")
        checks.append(False)

    if test_user.is_active:
        print("   ✅ User is ACTIVE")
        checks.append(True)
    else:
        print("   ❌ User is NOT active (should be True)")
        checks.append(False)

    if test_user.approved_at:
        print(f"   ✅ User has approved_at timestamp: {test_user.approved_at}")
        checks.append(True)
    else:
        print("   ❌ User missing approved_at timestamp")
        checks.append(False)

    # 6. Verify role assignment
    print_header("6. VERIFY ROLE ASSIGNMENT")

    roles = test_user.get_roles()
    print(f"\nUser roles: {roles.count()}")

    has_basic_role = False
    for role in roles:
        print(f"   - {role.name}: {role.display_name}")
        if role.name == 'basic_user':
            has_basic_role = True

    if has_basic_role:
        print("\n   ✅ User has 'basic_user' role assigned")
        checks.append(True)
    else:
        print("\n   ❌ User does NOT have 'basic_user' role")
        checks.append(False)

    # 7. Test login capability
    print_header("7. TEST LOGIN CAPABILITY")

    if test_user.approval_status == 'approved' and test_user.is_active:
        print("\n✅ User should be able to login")
        print("   - Status is 'approved'")
        print("   - Account is active")
        checks.append(True)
    else:
        print("\n❌ User would NOT be able to login")
        print(f"   - Status: {test_user.approval_status}")
        print(f"   - Active: {test_user.is_active}")
        checks.append(False)

    # 8. Summary
    print_header("8. TEST SUMMARY")

    all_passed = all(checks)
    passed_count = sum(checks)
    total_count = len(checks)

    print(f"\nTests passed: {passed_count}/{total_count}")

    if all_passed:
        print("\n🎉 SUCCESS! Auto-approval system is working correctly!")
        print("\nWhat happens now:")
        print("1. New users authenticate via NPU API")
        print("2. System creates user account with 'approved' status")
        print("3. User is automatically activated (is_active=True)")
        print("4. User gets 'Basic User' role automatically")
        print("5. User can login immediately (no manual approval needed)")
    else:
        print("\n❌ FAILED! Some tests did not pass.")
        print("   Please review the implementation.")

    # 9. Cleanup
    print_header("9. CLEANUP")
    print("\nDeleting test user...")
    UserRole.objects.filter(user=test_user).delete()
    test_user.delete()
    print("✅ Test user cleaned up")

    print("\n" + "=" * 80)
    print("END OF TEST")
    print("=" * 80)

    return all_passed


if __name__ == '__main__':
    try:
        success = test_backend_logic()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
