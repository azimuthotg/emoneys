from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from accounts.models import Role, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'แต่งตั้งผู้ใช้เป็น Senior Manager'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ldap-uid',
            type=str,
            help='รหัสบัตรประชาชน (LDAP UID) ของผู้ใช้ที่จะแต่งตั้ง'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username ของผู้ใช้ที่จะแต่งตั้ง'
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='แสดงรายชื่อผู้ใช้ทั้งหมดในระบบ'
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='ถอดถอน Senior Manager role (แทนที่จะเพิ่ม)'
        )

    def handle(self, *args, **options):
        # แสดงรายชื่อผู้ใช้ทั้งหมด
        if options['list_users']:
            self.list_all_users()
            return

        # ตรวจสอบว่าระบุ user หรือไม่
        ldap_uid = options.get('ldap_uid')
        username = options.get('username')
        
        if not ldap_uid and not username:
            raise CommandError('กรุณาระบุ --ldap-uid หรือ --username หรือใช้ --list-users เพื่อดูรายชื่อผู้ใช้')

        # ค้นหาผู้ใช้
        user = self.find_user(ldap_uid, username)
        if not user:
            return

        # ดำเนินการ
        if options['remove']:
            self.remove_senior_manager_role(user)
        else:
            self.assign_senior_manager_role(user)

    def list_all_users(self):
        """แสดงรายชื่อผู้ใช้ทั้งหมด"""
        self.stdout.write('👥 รายชื่อผู้ใช้ในระบบ:')
        self.stdout.write('-' * 80)
        
        users = User.objects.filter(is_active=True).order_by('department', 'full_name')
        
        current_dept = None
        for user in users:
            if user.department != current_dept:
                current_dept = user.department
                self.stdout.write(f'\n🏢 หน่วยงาน: {current_dept or "ไม่ระบุ"}')
                self.stdout.write('-' * 40)
            
            # แสดงข้อมูลผู้ใช้
            display_name = user.full_name or user.username
            roles = list(user.get_roles().values_list('display_name', flat=True))
            roles_str = ', '.join(roles) if roles else 'ไม่มีบทบาท'
            
            self.stdout.write(f'👤 {display_name}')
            self.stdout.write(f'   📧 Username: {user.username}')
            if user.ldap_uid:
                self.stdout.write(f'   🆔 LDAP UID: {user.ldap_uid}')
            self.stdout.write(f'   🎭 บทบาท: {roles_str}')
            self.stdout.write('')

    def find_user(self, ldap_uid, username):
        """ค้นหาผู้ใช้"""
        try:
            if ldap_uid:
                user = User.objects.get(ldap_uid=ldap_uid, is_active=True)
                self.stdout.write(f'🔍 พบผู้ใช้: {user.full_name or user.username} (LDAP: {ldap_uid})')
            else:
                user = User.objects.get(username=username, is_active=True)
                self.stdout.write(f'🔍 พบผู้ใช้: {user.full_name or user.username} (Username: {username})')
            
            # แสดงข้อมูลผู้ใช้
            self.stdout.write(f'🏢 หน่วยงาน: {user.department or "ไม่ระบุ"}')
            
            current_roles = list(user.get_roles().values_list('display_name', flat=True))
            if current_roles:
                self.stdout.write(f'🎭 บทบาทปัจจุบัน: {", ".join(current_roles)}')
            else:
                self.stdout.write('🎭 บทบาทปัจจุบัน: ไม่มี')
            
            return user
            
        except User.DoesNotExist:
            identifier = ldap_uid or username
            self.stdout.write(f'❌ ไม่พบผู้ใช้: {identifier}')
            self.stdout.write('💡 ใช้ --list-users เพื่อดูรายชื่อผู้ใช้ทั้งหมด')
            return None

    def assign_senior_manager_role(self, user):
        """แต่งตั้งเป็น Senior Manager"""
        try:
            # ค้นหา Senior Manager role
            senior_manager_role = Role.objects.get(name='senior_manager')
            
            # ตรวจสอบว่ามี role นี้อยู่แล้วหรือไม่
            existing_role = UserRole.objects.filter(
                user=user,
                role=senior_manager_role,
                is_active=True
            ).first()
            
            if existing_role:
                self.stdout.write(f'⚠️  {user.full_name or user.username} เป็น Senior Manager อยู่แล้ว')
                return
            
            # สร้าง UserRole ใหม่
            UserRole.objects.create(
                user=user,
                role=senior_manager_role,
                is_active=True
            )
            
            self.stdout.write(f'✅ แต่งตั้ง {user.full_name or user.username} เป็น Senior Manager สำเร็จ!')
            self.stdout.write(f'🏢 หน่วยงาน: {user.department}')
            self.stdout.write('')
            self.stdout.write('🎯 สิทธิ์ที่ได้รับ:')
            self.stdout.write('   - อนุมัติการแก้ไขจาก Department Manager ในแผนกเดียวกัน')
            self.stdout.write('   - อนุมัติการแก้ไขจาก Basic User ในแผนกเดียวกัน')
            self.stdout.write('   - ดูใบสำคัญของหน่วยงานตัวเอง')
            self.stdout.write('   - สร้างและจัดการใบสำคัญรับเงิน')
            
        except Role.DoesNotExist:
            self.stdout.write('❌ ไม่พบ Senior Manager role')
            self.stdout.write('💡 รัน: python manage.py setup_senior_manager ก่อน')

    def remove_senior_manager_role(self, user):
        """ถอดถอน Senior Manager role"""
        try:
            senior_manager_role = Role.objects.get(name='senior_manager')
            
            user_role = UserRole.objects.filter(
                user=user,
                role=senior_manager_role,
                is_active=True
            ).first()
            
            if not user_role:
                self.stdout.write(f'⚠️  {user.full_name or user.username} ไม่ได้เป็น Senior Manager')
                return
            
            user_role.is_active = False
            user_role.save()
            
            self.stdout.write(f'✅ ถอดถอน {user.full_name or user.username} จาก Senior Manager แล้ว')
            
        except Role.DoesNotExist:
            self.stdout.write('❌ ไม่พบ Senior Manager role')