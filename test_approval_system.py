#!/usr/bin/env python
"""
Script to test and understand the current approval system
Shows current roles, pending users, and helps plan the auto-approval feature
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
from datetime import datetime


def main():
    print("=" * 80)
    print("APPROVAL SYSTEM - CURRENT STATE")
    print("=" * 80)
    print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Show all available roles
    print("=" * 80)
    print("1. AVAILABLE ROLES IN SYSTEM:")
    print("=" * 80)
    roles = Role.objects.filter(is_active=True).order_by('name')
    if roles.exists():
        for role in roles:
            print(f"   - {role.name:<30} | {role.display_name}")
            if role.description:
                print(f"     คำอธิบาย: {role.description}")
    else:
        print("   ⚠️  ไม่มี Role ในระบบ!")

    # 2. Show user statistics
    print("\n" + "=" * 80)
    print("2. USER STATISTICS:")
    print("=" * 80)
    total_users = User.objects.count()
    pending_users = User.objects.filter(approval_status='pending').count()
    approved_users = User.objects.filter(approval_status='approved').count()
    rejected_users = User.objects.filter(approval_status='rejected').count()
    suspended_users = User.objects.filter(approval_status='suspended').count()

    print(f"   Total Users:      {total_users}")
    print(f"   Pending Approval: {pending_users}")
    print(f"   Approved:         {approved_users}")
    print(f"   Rejected:         {rejected_users}")
    print(f"   Suspended:        {suspended_users}")

    # 3. Show pending users with departments
    print("\n" + "=" * 80)
    print("3. PENDING USERS (รอการอนุมัติ):")
    print("=" * 80)
    pending = User.objects.filter(approval_status='pending').order_by('-date_joined')[:10]
    if pending.exists():
        print(f"   {'Username':<15} | {'Name':<30} | {'Department':<40}")
        print("   " + "-" * 90)
        for user in pending:
            username = user.username[:14]
            name = user.get_display_name()[:29]
            dept = (user.department or 'N/A')[:39]
            print(f"   {username:<15} | {name:<30} | {dept:<40}")
    else:
        print("   ✅ ไม่มีผู้ใช้รอการอนุมัติ")

    # 4. Show department statistics
    print("\n" + "=" * 80)
    print("4. DEPARTMENT STATISTICS (จากผู้ใช้ทั้งหมด):")
    print("=" * 80)
    from django.db.models import Count
    dept_stats = User.objects.values('department').annotate(
        total=Count('id'),
        pending=Count('id', filter=django.db.models.Q(approval_status='pending')),
        approved=Count('id', filter=django.db.models.Q(approval_status='approved'))
    ).order_by('-total')[:10]

    if dept_stats:
        print(f"   {'Department':<50} | {'Total':<6} | {'Pending':<8} | {'Approved':<8}")
        print("   " + "-" * 80)
        for stat in dept_stats:
            dept_name = (stat['department'] or 'N/A')[:49]
            print(f"   {dept_name:<50} | {stat['total']:<6} | {stat['pending']:<8} | {stat['approved']:<8}")
    else:
        print("   ⚠️  ไม่มีข้อมูลแผนก")

    # 5. Check for "มหาวิทยาลัยนครพนม" keyword in departments
    print("\n" + "=" * 80)
    print("5. NPU USERS DETECTION (ตรวจหาผู้ใช้จากมหาวิทยาลัยนครพนม):")
    print("=" * 80)

    # Search patterns for NPU
    npu_patterns = ['นครพนม', 'NPU', 'Nakhon Phanom University']

    for pattern in npu_patterns:
        npu_users = User.objects.filter(department__icontains=pattern)
        count = npu_users.count()
        print(f"   Pattern '{pattern}': พบ {count} คน")

        if count > 0 and count <= 5:
            for user in npu_users[:5]:
                print(f"      - {user.get_display_name()} | {user.department}")

    # 6. Show sample of approved users with roles
    print("\n" + "=" * 80)
    print("6. APPROVED USERS WITH ROLES (ตัวอย่าง 5 คนแรก):")
    print("=" * 80)
    approved = User.objects.filter(approval_status='approved').order_by('-approved_at')[:5]
    if approved.exists():
        for user in approved:
            roles = user.get_roles()
            role_names = ', '.join([r.display_name for r in roles]) if roles.exists() else 'ไม่มี Role'
            print(f"   {user.get_display_name():<30} | Roles: {role_names}")
            print(f"      Department: {user.department or 'N/A'}")
            print(f"      Approved: {user.approved_at.strftime('%Y-%m-%d %H:%M') if user.approved_at else 'N/A'}")
            print()
    else:
        print("   ⚠️  ไม่มีผู้ใช้ที่ได้รับการอนุมัติ")

    # 7. Implementation plan
    print("=" * 80)
    print("7. AUTO-APPROVAL IMPLEMENTATION PLAN:")
    print("=" * 80)
    print("""
   ตามความต้องการ:
   - ผู้ใช้ที่ login และมาจาก "มหาวิทยาลัยนครพนม" ให้ auto-approve
   - กำหนด Role เริ่มต้นเป็น "Basic User"

   จุดที่ต้องแก้ไข:
   1. File: accounts/backends.py
      Method: _create_pending_user()
      → ตรวจสอบ department ถ้าเป็น NPU ให้เปลี่ยนจาก 'pending' เป็น 'approved'
      → เพิ่มการ assign role "Basic User" อัตโนมัติ

   2. การตรวจสอบ NPU:
      - ตรวจสอบจาก field 'department' ว่ามีคำว่า "นครพนม" หรือไม่
      - หรือใช้ pattern matching อื่นๆ ที่เหมาะสม

   3. Role Assignment:
      - หา Role ชื่อ "Basic User"
      - ถ้าไม่มีต้องสร้างก่อน
      - ใช้ method user.assign_role(role)
    """)

    print("\n" + "=" * 80)
    print("END OF ANALYSIS")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
