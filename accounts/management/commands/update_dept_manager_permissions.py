from django.core.management.base import BaseCommand
from accounts.models import Permission, Role


class Command(BaseCommand):
    help = 'Update Department Manager role - remove receipt_cancel_department permission'

    def handle(self, *args, **options):
        self.stdout.write('Updating Department Manager permissions...')

        try:
            # Get Department Manager role
            dept_manager_role = Role.objects.get(name='department_manager')

            # Remove receipt_cancel_department permission
            try:
                cancel_dept_perm = Permission.objects.get(name='receipt_cancel_department')
                if dept_manager_role.permissions.filter(id=cancel_dept_perm.id).exists():
                    dept_manager_role.permissions.remove(cancel_dept_perm)
                    self.stdout.write(self.style.SUCCESS(
                        f"✓ Removed 'receipt_cancel_department' from Department Manager"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        "- 'receipt_cancel_department' was not assigned to Department Manager"
                    ))
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    "- Permission 'receipt_cancel_department' does not exist"
                ))

            # Display current permissions
            current_permissions = dept_manager_role.permissions.all()
            self.stdout.write(f"\n📋 Current Department Manager permissions ({current_permissions.count()}):")
            for perm in current_permissions:
                self.stdout.write(f"  - {perm.name}: {perm.get_name_display()}")

            self.stdout.write(self.style.SUCCESS(
                '\n✅ Department Manager permissions updated successfully!'
            ))

        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "❌ Department Manager role does not exist. Please run 'python manage.py create_permissions' first."
            ))
