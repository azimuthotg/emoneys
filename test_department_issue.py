"""
Script to debug department issue
Run: python test_department_issue.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edoc_system.settings')
django.setup()

from accounts.models import User, Department, DocumentVolume

print("=" * 80)
print("ตรวจสอบปัญหา Department")
print("=" * 80)

# 1. ตรวจสอบ User ที่เป็นเจ้าหน้าที่
print("\n### 1. เจ้าหน้าที่ที่ Approve แล้ว (5 คนแรก) ###")
staff_users = User.objects.filter(approval_status='approved', user_type='staff').exclude(is_superuser=True)[:5]
for user in staff_users:
    dept_field = user.department
    dept_method = user.get_department()
    print(f"\nUser: {user.username} ({user.full_name})")
    print(f"  - user.department = '{dept_field}' (type: {type(dept_field).__name__})")
    print(f"  - user.get_department() = '{dept_method}' (type: {type(dept_method).__name__})")

    # ลอง query Department
    if dept_method:
        try:
            dept_obj = Department.objects.get(name=dept_method)
            print(f"  ✅ พบ Department: {dept_obj.name} (ID: {dept_obj.id})")
        except Department.DoesNotExist:
            print(f"  ❌ ไม่พบ Department ที่ชื่อ '{dept_method}'")
        except Department.MultipleObjectsReturned:
            print(f"  ⚠️  พบ Department ซ้ำ!")

# 2. ตรวจสอบ Department ทั้งหมด
print("\n\n### 2. Department ในระบบทั้งหมด ###")
departments = Department.objects.all()
print(f"จำนวน Department: {departments.count()}")
for dept in departments:
    print(f"  ID: {dept.id:3d} | Name: '{dept.name}' | Code: {dept.code}")

# 3. ตรวจสอบ DocumentVolume
print("\n\n### 3. DocumentVolume ในระบบ ###")
volumes = DocumentVolume.objects.select_related('department').all()
print(f"จำนวน Volume: {volumes.count()}")
if volumes.exists():
    for vol in volumes[:10]:
        print(f"  Volume: {vol.volume_code:10s} | Department: {vol.department.name} (ID: {vol.department.id})")
else:
    print("  ไม่มี Volume ในระบบ")

# 4. ตรวจสอบการ match ระหว่าง User.department กับ Department.name
print("\n\n### 4. ตรวจสอบ Matching ระหว่าง User และ Department ###")
all_staff = User.objects.filter(user_type='staff', approval_status='approved').exclude(is_superuser=True)
dept_names_from_users = set()
for user in all_staff:
    dept = user.get_department()
    if dept and dept not in ['ไม่ระบุหน่วยงาน', 'ไม่ระบุคณะ']:
        dept_names_from_users.add(dept)

dept_names_from_dept_table = set(Department.objects.values_list('name', flat=True))

print(f"\nหน่วยงานจาก User.department: {len(dept_names_from_users)} หน่วยงาน")
print(f"หน่วยงานจาก Department table: {len(dept_names_from_dept_table)} หน่วยงาน")

missing = dept_names_from_users - dept_names_from_dept_table
if missing:
    print(f"\n⚠️  หน่วยงานที่มีใน User แต่ไม่มีใน Department table ({len(missing)} หน่วยงาน):")
    for m in list(missing)[:10]:
        print(f"  - '{m}'")
else:
    print("\n✅ ทุก User มี Department ในตาราง Department แล้ว")

# 5. ตรวจสอบ User ที่ login ล่าสุด
print("\n\n### 5. User ที่ Login ล่าสุด (5 คนล่าสุด) ###")
recent_users = User.objects.filter(last_login__isnull=False).order_by('-last_login')[:5]
for user in recent_users:
    print(f"\nUser: {user.username}")
    print(f"  Last Login: {user.last_login}")
    print(f"  User Type: {user.user_type}")
    print(f"  Department: '{user.get_department()}'")

print("\n" + "=" * 80)
print("สรุป:")
print("=" * 80)
print(f"- Staff Users: {User.objects.filter(user_type='staff').count()}")
print(f"- Student Users: {User.objects.filter(user_type='student').count()}")
print(f"- Departments: {Department.objects.count()}")
print(f"- Document Volumes: {DocumentVolume.objects.count()}")
print("=" * 80)
