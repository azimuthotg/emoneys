"""
Create 3 test users from Academic Service Department for testing approval workflow.

Usage:
python manage.py create_academic_service_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Department, Role, Permission
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 3 test users from Academic Service Department for testing approval workflow'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write("🔍 Creating Academic Service Department users...")
                
                # Get or create Academic Service Department
                academic_dept, created = Department.objects.get_or_create(
                    code='AS',
                    defaults={
                        'name': 'สำนักวิทยบริการและเทคโนโลยีสารสนเทศ',
                        'name_en': 'Office of Academic Service and Information Technology',
                        'is_active': True,
                        'address': 'มหาวิทยาลัยนเรศวร จ.พิษณุโลก',
                        'parent_department_id': None
                    }
                )
                
                if created:
                    self.stdout.write(f"✅ Created department: {academic_dept.name}")
                else:
                    self.stdout.write(f"✅ Using existing department: {academic_dept.name}")

                # Get roles
                try:
                    basic_role = Role.objects.get(name='basic_user')
                    manager_role = Role.objects.get(name='department_manager')
                    senior_role = Role.objects.get(name='senior_manager')
                except Role.DoesNotExist as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Required role not found: {e}")
                    )
                    self.stdout.write("Please run: python manage.py create_permissions first")
                    return

                # Define test users
                test_users = [
                    {
                        'username': 'as_basic',
                        'password': 'test123',
                        'personal_id': '1234567890123',
                        'full_name': 'นายสมชาย ใจดี',
                        'first_name': 'สมชาย',
                        'last_name': 'ใจดี',
                        'email': 'somchai@npu.ac.th',
                        'position_title': 'เจ้าหน้าที่บริหารงานทั่วไป',
                        'role': basic_role,
                        'description': 'Basic User - สามารถสร้างและแก้ไขเอกสารร่างของตัวเอง'
                    },
                    {
                        'username': 'as_manager',
                        'password': 'test123',
                        'personal_id': '2345678901234',
                        'full_name': 'นายสมพงษ์ บริหาร',
                        'first_name': 'สมพงษ์',
                        'last_name': 'บริหาร',
                        'email': 'sompong@npu.ac.th',
                        'position_title': 'หัวหน้างานบริหารทั่วไป',
                        'role': manager_role,
                        'description': 'Department Manager - อนุมัติคำขอแก้ไขของ Basic User'
                    },
                    {
                        'username': 'as_senior',
                        'password': 'test123',
                        'personal_id': '3456789012345',
                        'full_name': 'นายสมเกียรติ บริหารสูง',
                        'first_name': 'สมเกียรติ',
                        'last_name': 'บริหารสูง',
                        'email': 'somkiat@npu.ac.th',
                        'position_title': 'รองผู้อำนวยการสำนักวิทยบริการฯ',
                        'role': senior_role,
                        'description': 'Senior Manager - อนุมัติคำขอแก้ไขของ Department Manager'
                    }
                ]

                # Create users
                created_users = []
                for user_data in test_users:
                    username = user_data['username']
                    
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        self.stdout.write(f"⚠️ User {username} already exists, skipping...")
                        continue
                    
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        password=user_data['password'],
                        personal_id=user_data['personal_id'],
                        full_name=user_data['full_name'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        email=user_data['email'],
                        position_title=user_data['position_title'],
                        department=academic_dept.name,
                        is_active=True,
                        approval_status='approved'
                    )
                    
                    # Assign role
                    user.roles.add(user_data['role'])
                    
                    created_users.append({
                        'user': user,
                        'role': user_data['role'].name,
                        'description': user_data['description']
                    })
                    
                    self.stdout.write(f"✅ Created user: {username} ({user_data['role'].name})")

                # Display summary
                self.stdout.write("\n" + "="*60)
                self.stdout.write("🎉 ACADEMIC SERVICE DEPARTMENT TEST USERS CREATED")
                self.stdout.write("="*60)
                
                for user_info in created_users:
                    user = user_info['user']
                    self.stdout.write(f"""
📋 Username: {user.username}
👤 Name: {user.full_name}
🏢 Department: {user.department}
🎭 Role: {user_info['role']}
📝 Description: {user_info['description']}
🔑 Password: test123
📧 Email: {user.email}
""")

                self.stdout.write("="*60)
                self.stdout.write("🔬 TESTING WORKFLOW:")
                self.stdout.write("1. Login as 'as_basic' → Create document → Save as draft → Edit directly")
                self.stdout.write("2. Complete document → Request edit → as_manager approves")
                self.stdout.write("3. as_manager creates edit request → as_senior approves")
                self.stdout.write("="*60)

                if not created_users:
                    self.stdout.write("⚠️ No new users created (all users already exist)")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creating users: {str(e)}")
            )
            raise