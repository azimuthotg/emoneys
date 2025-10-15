from django.core.management.base import BaseCommand
from accounts.models import Permission, Role


class Command(BaseCommand):
    help = 'Create initial permissions and roles for the receipt system'

    def handle(self, *args, **options):
        self.stdout.write('Creating Permission...')

        # Create Permission data
        permissions_data = [
            # Basic permissions
            ('receipt_create', 'Create receipt', 'Can create new receipts'),
            ('receipt_view_own', 'View own receipts', 'Can view own receipts'),
            
            # Edit request permissions (for Basic Users)
            ('receipt_edit_request', 'Submit edit request', 'Can submit edit request for receipts'),
            ('receipt_edit_request_view', 'View edit requests', 'Can view own edit requests'),
            ('receipt_edit_withdraw', 'Withdraw edit request', 'Can withdraw own edit requests'),
            
            # Cancel request permissions (for Basic Users)
            ('receipt_cancel_request', 'Submit cancel request', 'Can submit cancel request for receipts'),
            ('receipt_cancel_request_view', 'View cancel requests', 'Can view own cancel requests'),
            ('receipt_cancel_withdraw', 'Withdraw cancel request', 'Can withdraw own cancel requests'),
            
            # Department level permissions  
            ('receipt_edit_approve', 'Approve receipt edits', 'Can approve receipt edit requests'),
            ('receipt_cancel_approve', 'Approve cancel requests', 'Can approve cancel requests from basic users'),
            ('receipt_cancel_department', 'Cancel department receipts', 'Can cancel receipts in own department'),
            ('receipt_view_department', 'View department receipts', 'Can view all receipts in own department'),
            
            # Senior Manager level permissions
            ('receipt_edit_approve_manager', 'Approve manager edit requests', 'Can approve edit requests from department managers'),
            ('receipt_cancel_approve_manager', 'Approve manager cancel requests', 'Can approve cancel requests from department managers'),
            
            # System permissions
            ('receipt_view_all', 'View all receipts', 'Can view all receipts in system'),
            ('receipt_export', 'Export receipt data', 'Can export receipt data to files'),
            ('user_manage', 'Manage users', 'Can manage user accounts'),
            ('role_manage', 'Manage roles and permissions', 'Can manage roles and permissions'),
            ('report_view', 'View reports', 'Can view system reports'),
            ('system_config', 'System configuration', 'Can configure system settings'),
        ]

        created_count = 0
        for name, display_name, description in permissions_data:
            permission, created = Permission.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✓ Created Permission: {display_name}")
            else:
                self.stdout.write(f"- Permission exists: {display_name}")

        self.stdout.write(f"\nPermission creation complete! Created {created_count} new permissions")
        self.stdout.write(f"Total active permissions: {Permission.objects.filter(is_active=True).count()}")

        # Create sample roles
        self.stdout.write("\nCreating sample roles...")

        # Role: Basic User
        basic_user_role, created = Role.objects.get_or_create(
            name='basic_user',
            defaults={
                'display_name': 'Basic User',
                'description': 'Regular user who can create receipts and view own receipts',
                'is_active': True
            }
        )

        if created:
            # Add permissions for Basic User (รวม Edit & Cancel Request permissions)
            basic_permissions = Permission.objects.filter(
                name__in=[
                    'receipt_create', 'receipt_view_own',
                    'receipt_edit_request', 'receipt_edit_request_view', 'receipt_edit_withdraw',
                    'receipt_cancel_request', 'receipt_cancel_request_view', 'receipt_cancel_withdraw'
                ],
                is_active=True
            )
            basic_user_role.permissions.set(basic_permissions)
            self.stdout.write("✓ Created Role: Basic User")
        else:
            self.stdout.write("- Role exists: Basic User")

        # Role: Department Manager
        dept_manager_role, created = Role.objects.get_or_create(
            name='department_manager',
            defaults={
                'display_name': 'Department Manager',
                'description': 'Department manager who can manage receipts in own department',
                'is_active': True
            }
        )

        if created:
            # Add permissions for Department Manager
            # ⚠️ ลบ 'receipt_cancel_department' ออก - Dep Manager ต้องขออนุมัติยกเลิกจาก Senior Manager
            manager_permissions = Permission.objects.filter(
                name__in=[
                    'receipt_create',
                    'receipt_view_own',
                    'receipt_edit_approve',
                    'receipt_cancel_approve',
                    'receipt_view_department',
                    'receipt_cancel_request', 'receipt_cancel_request_view', 'receipt_cancel_withdraw'
                ],
                is_active=True
            )
            dept_manager_role.permissions.set(manager_permissions)
            self.stdout.write("✓ Created Role: Department Manager")
        else:
            self.stdout.write("- Role exists: Department Manager")

        # Role: Student (นักศึกษา)
        student_role, created = Role.objects.get_or_create(
            name='student',
            defaults={
                'display_name': 'Student (นักศึกษา)',
                'description': 'Student users who can only view their own documents',
                'is_active': True
            }
        )

        if created:
            # Add permissions for Student (create and view own receipts)
            student_permissions = Permission.objects.filter(
                name__in=['receipt_create', 'receipt_view_own'],
                is_active=True
            )
            student_role.permissions.set(student_permissions)
            self.stdout.write("✓ Created Role: Student (นักศึกษา)")
        else:
            # Update existing Student role permissions
            student_permissions = Permission.objects.filter(
                name__in=['receipt_create', 'receipt_view_own'],
                is_active=True
            )
            student_role.permissions.set(student_permissions)
            self.stdout.write("- Role exists: Student (นักศึกษา) - Updated permissions")

        self.stdout.write(f"\nRole creation complete!")
        self.stdout.write(f"Total active roles: {Role.objects.filter(is_active=True).count()}")

        self.stdout.write(self.style.SUCCESS('\nAll permissions and roles have been created successfully!'))