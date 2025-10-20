"""
Test script for checking permissions and roles
Run: python test_permissions.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import User, Role, Permission, UserRole

def main():
    print("=" * 80)
    print("Permission and Role Testing Script")
    print("=" * 80)
    print()

    # 1. แสดง Permissions ทั้งหมด
    print("1. รายการ Permissions ทั้งหมด:")
    print("-" * 80)
    permissions = Permission.objects.all().order_by('name')
    for perm in permissions:
        print(f"   - {perm.name} (active: {perm.is_active})")
    print(f"\nTotal: {permissions.count()} permissions")
    print()

    # 2. แสดง Role "Aadmin" และ permissions ที่มี
    print("2. Role 'Aadmin' และ Permissions:")
    print("-" * 80)
    try:
        aadmin_role = Role.objects.get(name='Aadmin')
        print(f"   Role: {aadmin_role.name}")
        print(f"   Description: {aadmin_role.description}")
        print(f"   Active: {aadmin_role.is_active}")
        print(f"\n   Permissions ของ Role นี้:")
        for perm in aadmin_role.permissions.all():
            print(f"      - {perm.name}")
    except Role.DoesNotExist:
        print("   ❌ ไม่พบ Role 'Aadmin'")
    print()

    # 3. แสดง User ที่มี Role "Aadmin"
    print("3. Users ที่มี Role 'Aadmin':")
    print("-" * 80)
    try:
        aadmin_role = Role.objects.get(name='Aadmin')
        user_roles = UserRole.objects.filter(role=aadmin_role, is_active=True)
        if user_roles.exists():
            for ur in user_roles:
                user = ur.user
                print(f"   - {user.username} ({user.full_name})")
                print(f"     is_staff: {user.is_staff}")
                print(f"     is_superuser: {user.is_superuser}")
                print(f"     user_type: {user.user_type}")
        else:
            print("   ไม่มี User ที่มี Role นี้")
    except Role.DoesNotExist:
        print("   ❌ ไม่พบ Role 'Aadmin'")
    print()

    # 4. ทดสอบ has_permission() กับ User ที่มี Role Aadmin
    print("4. ทดสอบ has_permission() method:")
    print("-" * 80)
    try:
        aadmin_role = Role.objects.get(name='Aadmin')
        user_roles = UserRole.objects.filter(role=aadmin_role, is_active=True).first()

        if user_roles:
            user = user_roles.user
            print(f"   User: {user.username}")
            print()

            # ทดสอบ permissions ต่างๆ
            test_perms = [
                'จัดการผู้ใช้งาน',
                'จัดการบทบาทและสิทธิ์',
                'ดูสำระบบ',
                'ตั้งค่าระบบ',
                'สร้างใบสำคัญรับเงิน',
            ]

            for perm_name in test_perms:
                result = user.has_permission(perm_name)
                status = "✅ มีสิทธิ์" if result else "❌ ไม่มีสิทธิ์"
                print(f"   {status} - {perm_name}")

                # แสดงรายละเอียดว่าทำไมมีหรือไม่มีสิทธิ์
                if user.is_superuser:
                    print(f"      → เพราะเป็น superuser")
                elif user.is_staff:
                    print(f"      → เพราะเป็น staff")
                else:
                    # เช็คจาก role
                    has_in_role = aadmin_role.has_permission(perm_name)
                    if has_in_role:
                        print(f"      → เพราะ Role 'Aadmin' มีสิทธิ์นี้")
                    else:
                        print(f"      → เพราะ Role 'Aadmin' ไม่มีสิทธิ์นี้")
        else:
            print("   ไม่มี User ที่มี Role 'Aadmin'")
    except Role.DoesNotExist:
        print("   ❌ ไม่พบ Role 'Aadmin'")
    print()

    # 5. แสดง User ID 1411200103739 (จากรูป)
    print("5. ตรวจสอบ User ID: 1411200103739")
    print("-" * 80)
    try:
        user = User.objects.get(ldap_uid='1411200103739')
        print(f"   Username: {user.username}")
        print(f"   Full Name: {user.full_name}")
        print(f"   is_staff: {user.is_staff}")
        print(f"   is_superuser: {user.is_superuser}")
        print(f"   user_type: {user.user_type}")
        print()

        print("   Roles:")
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        if user_roles.exists():
            for ur in user_roles:
                print(f"      - {ur.role.name}")
        else:
            print("      ไม่มี Role")
        print()

        print("   ทดสอบ Permission 'จัดการผู้ใช้งาน':")
        has_perm = user.has_permission('จัดการผู้ใช้งาน')
        print(f"      Result: {has_perm}")

    except User.DoesNotExist:
        print("   ❌ ไม่พบ User นี้")
    print()

    print("=" * 80)
    print("Testing Complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
