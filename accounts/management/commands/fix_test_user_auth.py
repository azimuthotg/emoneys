from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'แก้ไข authentication สำหรับ test user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='usertest1',
            help='Username ของ test user ที่จะแก้ไข'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            
            self.stdout.write(f'🔧 กำลังแก้ไข authentication สำหรับ: {username}')
            
            # แก้ไขข้อมูลเพื่อให้ bypass NPU authentication
            user.ldap_uid = None  # ลบ LDAP UID เพื่อให้ใช้ Django authentication
            user.npu_staff_id = None
            user.is_staff = False  # ไม่ใช่ staff
            user.approval_status = 'approved'
            user.is_active = True
            
            # ตั้งรหัสผ่านใหม่
            user.set_password('usertest1')
            user.save()
            
            self.stdout.write(f'✅ แก้ไข {username} สำเร็จ!')
            self.stdout.write(f'🔑 ตอนนี้ login ด้วย:')
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Password: usertest1')
            self.stdout.write('')
            self.stdout.write('💡 ระบบจะใช้ Django authentication แทน NPU')
            
        except User.DoesNotExist:
            self.stdout.write(f'❌ ไม่พบ user: {username}')
            
        except Exception as e:
            self.stdout.write(f'❌ เกิดข้อผิดพลาด: {str(e)}')