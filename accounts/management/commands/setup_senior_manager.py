from django.core.management.base import BaseCommand
from accounts.models import Role, Permission


class Command(BaseCommand):
    help = 'สร้าง Senior Manager role และกำหนดสิทธิ์'

    def handle(self, *args, **options):
        self.stdout.write('เริ่มสร้าง Senior Manager role...')
        
        # สร้าง/อัพเดท permissions ที่จำเป็น
        permissions_data = [
            ('receipt_edit_approve_manager', 'อนุมัติการแก้ไขจาก Department Manager'),
        ]
        
        for perm_name, perm_desc in permissions_data:
            permission, created = Permission.objects.get_or_create(
                name=perm_name,
                defaults={'description': perm_desc}
            )
            if created:
                self.stdout.write(f'✅ สร้าง Permission: {perm_desc}')
            else:
                self.stdout.write(f'📋 Permission มีอยู่แล้ว: {perm_desc}')
        
        # สร้าง Senior Manager role
        senior_manager_role, created = Role.objects.get_or_create(
            name='senior_manager',
            defaults={
                'display_name': 'Senior Manager',
                'description': 'ผู้จัดการระดับสูง สามารถอนุมัติการแก้ไขจาก Department Manager'
            }
        )
        
        if created:
            self.stdout.write('✅ สร้าง Senior Manager role สำเร็จ')
        else:
            self.stdout.write('📋 Senior Manager role มีอยู่แล้ว')
        
        # กำหนดสิทธิ์สำหรับ Senior Manager
        senior_manager_permissions = [
            # สิทธิ์พื้นฐาน
            'receipt_create',
            'receipt_view_own',
            'receipt_edit_request',
            'receipt_edit_request_view',
            
            # สิทธิ์ cancel request
            'receipt_cancel_request',
            'receipt_cancel_request_view', 
            'receipt_cancel_withdraw',
            
            # สิทธิ์ระดับแผนก
            'receipt_view_department',
            'receipt_edit_approve',  # อนุมัติ Basic User
            'receipt_edit_approve_manager',  # อนุมัติ Department Manager
            'receipt_cancel_approve',  # อนุมัติ Basic User cancel requests
            'receipt_cancel_approve_manager',  # อนุมัติ Department Manager cancel requests
            'receipt_cancel_department',
            
            # สิทธิ์เพิ่มเติม
            'report_view',
        ]
        
        # เพิ่มสิทธิ์ให้ Senior Manager
        added_permissions = []
        for perm_name in senior_manager_permissions:
            try:
                permission = Permission.objects.get(name=perm_name)
                senior_manager_role.permissions.add(permission)
                added_permissions.append(permission.get_name_display())
            except Permission.DoesNotExist:
                self.stdout.write(f'⚠️  ไม่พบ Permission: {perm_name}')
        
        if added_permissions:
            self.stdout.write('✅ เพิ่มสิทธิ์ให้ Senior Manager:')
            for perm in added_permissions:
                self.stdout.write(f'   - {perm}')
        
        # แสดงข้อมูล Role Structure
        self.stdout.write('\n📊 Role Structure ปัจจุบัน:')
        self.stdout.write('System Admin → อนุมัติได้ทุกอย่าง')
        self.stdout.write('Senior Manager → อนุมัติ Department Manager ในแผนกเดียวกัน')
        self.stdout.write('Department Manager → อนุมัติ Basic User ในแผนกเดียวกัน')
        self.stdout.write('Basic User → ขออนุมัติแก้ไขเท่านั้น')
        
        self.stdout.write('\n🎉 Setup Senior Manager role เสร็จสิ้น!')
        self.stdout.write('📝 ขั้นตอนต่อไป: ใช้ Admin Panel เพื่อกำหนด UserRole ให้ผู้ใช้')