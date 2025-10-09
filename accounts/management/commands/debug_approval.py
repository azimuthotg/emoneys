from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import *

User = get_user_model()


class Command(BaseCommand):
    help = 'Debug approval system issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--request-id',
            type=int,
            default=3,
            help='Edit request ID to debug (default: 3)'
        )

    def handle(self, *args, **options):
        request_id = options['request_id']
        
        self.stdout.write("🔍 Debug Approval System")
        self.stdout.write("=" * 50)
        
        # 1. ดูข้อมูล Edit Request
        try:
            edit_request = ReceiptEditRequest.objects.get(id=request_id)
            self.stdout.write(f"📋 Edit Request ID: {edit_request.id}")
            self.stdout.write(f"📄 Receipt Number: {edit_request.receipt.receipt_number}")
            self.stdout.write(f"🏢 Receipt Department: {edit_request.receipt.department.name}")
            self.stdout.write(f"👤 Requested by: {edit_request.requested_by.username}")
            self.stdout.write(f"🎭 Requester has manager permission: {edit_request.requested_by.has_permission('receipt_edit_approve')}")
            self.stdout.write("")
        except ReceiptEditRequest.DoesNotExist:
            self.stdout.write(f"❌ ไม่พบ Edit Request ID {request_id}")
            return
        
        # 2. ดูข้อมูล Senior Manager users
        self.stdout.write("👥 Senior Manager Users:")
        self.stdout.write("-" * 30)
        
        senior_roles = UserRole.objects.filter(
            role__name='senior_manager',
            is_active=True
        )
        
        if not senior_roles:
            self.stdout.write("❌ ไม่พบ Senior Manager ในระบบ")
            self.stdout.write("💡 รัน: python manage.py assign_senior_manager --username USER_NAME")
            return
        
        for user_role in senior_roles:
            user = user_role.user
            self.stdout.write(f"👤 Username: {user.username}")
            self.stdout.write(f"📧 Full Name: {user.full_name}")
            self.stdout.write(f"🏢 Department: '{user.department}'")
            self.stdout.write(f"🔑 Has approve_manager permission: {user.has_permission('receipt_edit_approve_manager')}")
            self.stdout.write(f"🔑 Has approve permission: {user.has_permission('receipt_edit_approve')}")
            self.stdout.write(f"🔑 Has view_all permission: {user.has_permission('receipt_view_all')}")
            
            # ทดสอบการอนุมัติ
            can_approve = edit_request.can_be_approved_by(user)
            self.stdout.write(f"✅ Can approve Edit Request ID {request_id}: {can_approve}")
            
            # แสดงเหตุผลที่อนุมัติไม่ได้
            if not can_approve:
                self.stdout.write("❌ เหตุผลที่อนุมัติไม่ได้:")
                
                # ตรวจสอบแต่ละเงื่อนไข
                has_view_all = user.has_permission('receipt_view_all')
                has_approve_manager = user.has_permission('receipt_edit_approve_manager')
                dept_match = user.department == edit_request.receipt.department.name
                
                self.stdout.write(f"   - Has view_all permission: {has_view_all}")
                self.stdout.write(f"   - Has approve_manager permission: {has_approve_manager}")
                self.stdout.write(f"   - Department match: {dept_match}")
                self.stdout.write(f"     User dept: '{user.department}'")
                self.stdout.write(f"     Receipt dept: '{edit_request.receipt.department.name}'")
                
                if has_approve_manager and not dept_match:
                    self.stdout.write("   🎯 ปัญหา: Department ไม่ตรงกัน!")
                elif not has_approve_manager:
                    self.stdout.write("   🎯 ปัญหา: ไม่มี approve_manager permission!")
            
            self.stdout.write("-" * 30)
        
        # 3. ตรวจสอบ Permission ของ senior_manager role
        self.stdout.write("\n🎭 Senior Manager Role Permissions:")
        self.stdout.write("-" * 40)
        
        try:
            senior_role = Role.objects.get(name='senior_manager')
            permissions = senior_role.permissions.all()
            
            self.stdout.write(f"Role: {senior_role.display_name}")
            self.stdout.write("Permissions:")
            for perm in permissions:
                self.stdout.write(f"  ✅ {perm.get_name_display()}")
                
            # ตรวจสอบ permission ที่สำคัญ
            key_permissions = [
                'receipt_edit_approve_manager',
                'receipt_edit_approve',
                'receipt_view_department'
            ]
            
            self.stdout.write("\n🔍 Key Permissions Check:")
            for perm_name in key_permissions:
                has_perm = senior_role.has_permission(perm_name)
                status = "✅" if has_perm else "❌"
                self.stdout.write(f"  {status} {perm_name}")
                
        except Role.DoesNotExist:
            self.stdout.write("❌ ไม่พบ senior_manager role")
        
        # 4. แนะนำการแก้ไข
        self.stdout.write("\n🔧 การแก้ไขที่แนะนำ:")
        self.stdout.write("-" * 25)
        
        if senior_roles:
            user = senior_roles[0].user
            
            # แก้ไข Department
            if user.department != edit_request.receipt.department.name:
                self.stdout.write(f"1. แก้ไข Department ของ {user.username}:")
                self.stdout.write(f"   จาก: '{user.department}'")
                self.stdout.write(f"   เป็น: '{edit_request.receipt.department.name}'")
                self.stdout.write("   วิธี: เข้า Admin Panel แก้ไข User.department")
                
            # เพิ่ม Permission
            if not user.has_permission('receipt_edit_approve_manager'):
                self.stdout.write(f"2. เพิ่ม Permission ให้ {user.username}:")
                self.stdout.write(f"   รัน: python manage.py assign_senior_manager --username {user.username}")
                
        # 5. Quick Fix Commands
        self.stdout.write("\n⚡ Quick Fix Commands:")
        self.stdout.write("-" * 20)
        if senior_roles:
            user = senior_roles[0].user
            self.stdout.write(f"# แก้ไข Department")
            self.stdout.write(f"python manage.py shell -c \"")
            self.stdout.write(f"from django.contrib.auth import get_user_model; ")
            self.stdout.write(f"User = get_user_model(); ")
            self.stdout.write(f"user = User.objects.get(username='{user.username}'); ")
            self.stdout.write(f"user.department = '{edit_request.receipt.department.name}'; ")
            self.stdout.write(f"user.save(); ")
            self.stdout.write(f"print('Updated department to: {edit_request.receipt.department.name}')\"")
            
            self.stdout.write(f"\n# Re-assign Senior Manager role")
            self.stdout.write(f"python manage.py assign_senior_manager --username {user.username}")