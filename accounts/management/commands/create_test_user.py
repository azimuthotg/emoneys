from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Department

User = get_user_model()


class Command(BaseCommand):
    help = 'สร้าง test user สำหรับทดสอบระบบ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='usertest1',
            help='Username ของ test user (default: usertest1)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='usertest1',
            help='Password ของ test user (default: usertest1)'
        )
        parser.add_argument(
            '--department',
            type=str,
            default='สำนักวิทยบริการ',
            help='หน่วยงานของ test user (default: สำนักวิทยบริการ)'
        )
        parser.add_argument(
            '--full-name',
            type=str,
            help='ชื่อ-นามสกุล (ถ้าไม่ระบุจะใช้ Test User + username)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        department_name = options['department']
        full_name = options.get('full_name') or f'Test User {username}'
        
        self.stdout.write(f'🔧 สร้าง Test User: {username}')
        
        # ตรวจสอบว่า username ซ้ำหรือไม่
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'⚠️  Username "{username}" มีอยู่แล้ว')
            
            # เสนอทางเลือก
            self.stdout.write('🔄 ต้องการอัพเดทข้อมูลผู้ใช้นี้หรือไม่? (y/n): ', ending='')
            choice = input()
            
            if choice.lower() == 'y':
                self.update_existing_user(username, password, department_name, full_name)
            else:
                self.stdout.write('❌ ยกเลิกการสร้าง user')
            return
        
        # สร้าง Department ถ้ายังไม่มี
        department = self.get_or_create_department(department_name)
        
        # สร้าง Test User
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f'{username}@test.local',
                first_name='Test',
                last_name='User',
                full_name=full_name,
                department=department_name,
                ldap_uid=f'1234567890{username[-1:]}23',  # สร้าง fake LDAP UID (13 หลัก)
                npu_staff_id=f'TEST{username[-1:]}001',
                prefix_name='นาย',
                first_name_th='ทดสอบ',
                last_name_th=f'ผู้ใช้{username[-1:]}',
                position_title='เจ้าหน้าที่ทดสอบระบบ',
                staff_type='ข้าราชการ',
                employment_status='ปฏิบัติงานปกติ',
                approval_status='approved',  # อนุมัติแล้วเพื่อให้ login ได้
                is_active=True
            )
            
            self.stdout.write(f'✅ สร้าง Test User สำเร็จ!')
            self.stdout.write(f'👤 Username: {username}')
            self.stdout.write(f'🔑 Password: {password}')
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'👨‍💼 ชื่อ: {full_name}')
            self.stdout.write(f'🏢 หน่วยงาน: {department_name}')
            self.stdout.write(f'🆔 LDAP UID: {user.ldap_uid}')
            self.stdout.write('')
            self.stdout.write('🎯 ขั้นตอนต่อไป:')
            self.stdout.write(f'   1. Login ด้วย username: {username}, password: {password}')
            self.stdout.write(f'   2. ใช้คำสั่ง: python manage.py assign_senior_manager --username {username}')
            self.stdout.write('   3. ทดสอบ Hierarchical Approval System')
            
        except Exception as e:
            self.stdout.write(f'❌ เกิดข้อผิดพลาด: {str(e)}')

    def update_existing_user(self, username, password, department_name, full_name):
        """อัพเดทข้อมูลผู้ใช้ที่มีอยู่แล้ว"""
        try:
            user = User.objects.get(username=username)
            
            # อัพเดทข้อมูล
            user.set_password(password)
            user.full_name = full_name
            user.department = department_name
            user.is_active = True
            user.approval_status = 'approved'
            user.save()
            
            self.stdout.write(f'✅ อัพเดท User "{username}" สำเร็จ!')
            self.stdout.write(f'🔑 Password ใหม่: {password}')
            self.stdout.write(f'🏢 หน่วยงาน: {department_name}')
            
        except User.DoesNotExist:
            self.stdout.write(f'❌ ไม่พบ User: {username}')

    def get_or_create_department(self, department_name):
        """สร้าง Department ถ้ายังไม่มี"""
        try:
            department, created = Department.objects.get_or_create(
                name=department_name,
                defaults={
                    'code': department_name[:10].upper(),
                    'description': f'แผนก{department_name}',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'✅ สร้างหน่วยงาน: {department_name}')
            else:
                self.stdout.write(f'📋 หน่วยงานมีอยู่แล้ว: {department_name}')
                
            return department
            
        except Exception as e:
            self.stdout.write(f'⚠️  ไม่สามารถสร้างหน่วยงานได้: {str(e)}')
            self.stdout.write('💡 ใช้ข้อมูลหน่วยงานจาก string แทน')
            return None