from django.core.management.base import BaseCommand
from accounts.models import User, Role, UserRole

class Command(BaseCommand):
    help = 'Assign roles to existing users based on their current permissions'

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("ASSIGNING ROLES TO EXISTING USERS")
        self.stdout.write("=" * 50)
        
        # Get available roles
        basic_user_role = Role.objects.filter(name='basic_user').first()
        department_manager_role = Role.objects.filter(name='department_manager').first()
        
        if not basic_user_role:
            self.stdout.write(self.style.ERROR("Basic User role not found! Please run: python manage.py create_permissions"))
            return
        
        # Get all active users
        users = User.objects.filter(is_active=True)
        
        assigned_count = 0
        
        for user in users:
            self.stdout.write(f"\nProcessing user: {user.get_display_name()}")
            
            # Skip if user already has roles
            existing_roles = user.get_roles()
            if existing_roles.exists():
                role_names = [role.display_name for role in existing_roles]
                self.stdout.write(f"   - Already has roles: {', '.join(role_names)}")
                continue
            
            # Skip superusers and staff (they don't need application roles)
            if user.is_superuser:
                self.stdout.write("   - Superuser: No role assignment needed")
                continue
            
            if user.is_staff:
                self.stdout.write("   - Staff user: No role assignment needed")
                continue
            
            # Assign Department Manager role if user has management permissions
            if (user.is_document_staff or user.can_forward_documents) and department_manager_role:
                UserRole.objects.get_or_create(
                    user=user,
                    role=department_manager_role,
                    defaults={
                        'assigned_by': user,  # Self-assigned for migration
                        'is_active': True
                    }
                )
                self.stdout.write(f"   ✓ Assigned: {department_manager_role.display_name}")
                assigned_count += 1
                
            # Assign Basic User role to regular users
            else:
                UserRole.objects.get_or_create(
                    user=user,
                    role=basic_user_role,
                    defaults={
                        'assigned_by': user,  # Self-assigned for migration
                        'is_active': True
                    }
                )
                self.stdout.write(f"   ✓ Assigned: {basic_user_role.display_name}")
                assigned_count += 1
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("ROLE ASSIGNMENT SUMMARY")
        self.stdout.write("=" * 50)
        
        # Show final statistics
        self.stdout.write(f"Total users processed: {users.count()}")
        self.stdout.write(f"New role assignments: {assigned_count}")
        
        # Show role distribution
        basic_users = UserRole.objects.filter(role=basic_user_role, is_active=True).count()
        dept_managers = UserRole.objects.filter(role=department_manager_role, is_active=True).count() if department_manager_role else 0
        
        self.stdout.write(f"\nCurrent role distribution:")
        self.stdout.write(f"- Basic Users: {basic_users}")
        self.stdout.write(f"- Department Managers: {dept_managers}")
        self.stdout.write(f"- Superusers: {User.objects.filter(is_superuser=True, is_active=True).count()}")
        self.stdout.write(f"- Staff: {User.objects.filter(is_staff=True, is_active=True).count()}")
        
        self.stdout.write(self.style.SUCCESS("\n✓ Role assignment complete!"))
        self.stdout.write("Visit: http://localhost:8002/profile/ to see updated roles")