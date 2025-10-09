from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Permission, Role, User, Receipt, ReceiptEditRequest, ReceiptChangeLog, UserRole, Department

class Command(BaseCommand):
    help = 'Test Edit Request System functionality'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("EDIT REQUEST SYSTEM TEST")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Test Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 60)
        
        test_results = []
        
        # Test 1: Create Edit Request Permissions
        self.stdout.write("\nTEST 1: Creating Edit Request Permissions")
        self.stdout.write("-" * 40)
        try:
            edit_permissions_data = [
                ('receipt_edit_request', 'Submit edit request for receipts'),
                ('receipt_edit_request_view', 'View own edit requests'),
                ('receipt_edit_withdraw', 'Withdraw edit requests')
            ]
            
            created_count = 0
            for perm_name, perm_desc in edit_permissions_data:
                permission, created = Permission.objects.get_or_create(
                    name=perm_name,
                    defaults={'description': perm_desc, 'is_active': True}
                )
                status = "CREATED" if created else "EXISTS"
                self.stdout.write(f"   {status}: {perm_name}")
                if created:
                    created_count += 1
            
            self.stdout.write(f"   Result: {created_count} new permissions created")
            test_results.append(("Permissions Creation", True, f"{created_count} created"))
            
        except Exception as e:
            self.stdout.write(f"   ERROR: {str(e)}")
            test_results.append(("Permissions Creation", False, str(e)))
        
        # Test 2: Update Basic User Role
        self.stdout.write("\nTEST 2: Updating Basic User Role")
        self.stdout.write("-" * 40)
        try:
            basic_role, created = Role.objects.get_or_create(
                name='basic_user',
                defaults={
                    'display_name': 'Basic User',
                    'description': 'User who can create receipts and submit edit requests',
                    'is_active': True
                }
            )
            
            # Add permissions to Basic User
            basic_permissions = Permission.objects.filter(
                name__in=[
                    'receipt_create', 'receipt_view_own',
                    'receipt_edit_request', 'receipt_edit_request_view', 'receipt_edit_withdraw'
                ],
                is_active=True
            )
            
            old_count = basic_role.permissions.count()
            basic_role.permissions.set(basic_permissions)
            new_count = basic_role.permissions.count()
            
            self.stdout.write(f"   Basic User Role: {old_count} -> {new_count} permissions")
            test_results.append(("Role Updates", True, f"Basic: {new_count} permissions"))
            
        except Exception as e:
            self.stdout.write(f"   ERROR: {str(e)}")
            test_results.append(("Role Updates", False, str(e)))
        
        # Test 3: Model Functionality
        self.stdout.write("\nTEST 3: Testing Model Functionality")
        self.stdout.write("-" * 40)
        try:
            # Test ReceiptEditRequest methods
            methods_to_test = [
                'generate_request_number',
                'can_be_approved_by',
                'approve',
                'reject',
                'withdraw'
            ]
            
            missing_methods = []
            for method in methods_to_test:
                if hasattr(ReceiptEditRequest, method):
                    self.stdout.write(f"   OK: ReceiptEditRequest.{method}() exists")
                else:
                    self.stdout.write(f"   MISSING: ReceiptEditRequest.{method}()")
                    missing_methods.append(method)
            
            # Test ReceiptChangeLog
            if hasattr(ReceiptChangeLog, 'log_change'):
                self.stdout.write("   OK: ReceiptChangeLog.log_change() exists")
            else:
                self.stdout.write("   MISSING: ReceiptChangeLog.log_change()")
                missing_methods.append('log_change')
            
            # Test request number generation
            test_request = ReceiptEditRequest()
            request_number = test_request.generate_request_number()
            self.stdout.write(f"   Generated Request Number: {request_number}")
            
            success = len(missing_methods) == 0
            result_msg = "All methods present" if success else f"Missing: {missing_methods}"
            test_results.append(("Model Functionality", success, result_msg))
            
        except Exception as e:
            self.stdout.write(f"   ERROR: {str(e)}")
            test_results.append(("Model Functionality", False, str(e)))
        
        # Test 4: Database Relationships
        self.stdout.write("\nTEST 4: Testing Database Relationships")
        self.stdout.write("-" * 40)
        try:
            receipt_count = Receipt.objects.count()
            edit_request_count = ReceiptEditRequest.objects.count()
            change_log_count = ReceiptChangeLog.objects.count()
            
            self.stdout.write(f"   Receipts: {receipt_count} records")
            self.stdout.write(f"   Edit Requests: {edit_request_count} records")
            self.stdout.write(f"   Change Logs: {change_log_count} records")
            
            # Test relationships if data exists
            if receipt_count > 0:
                receipt = Receipt.objects.first()
                edit_requests = receipt.edit_requests.all()
                change_logs = receipt.change_logs.all()
                self.stdout.write(f"   Sample Receipt Relations: {edit_requests.count()} edit requests, {change_logs.count()} logs")
            
            test_results.append(("Database Relationships", True, f"{receipt_count} receipts"))
            
        except Exception as e:
            self.stdout.write(f"   ERROR: {str(e)}")
            test_results.append(("Database Relationships", False, str(e)))
        
        # Test 5: User Permissions
        self.stdout.write("\nTEST 5: Testing User Permissions")
        self.stdout.write("-" * 40)
        try:
            active_users = User.objects.filter(is_active=True)[:3]
            
            if active_users.exists():
                edit_permissions = ['receipt_edit_request', 'receipt_edit_request_view', 'receipt_edit_withdraw']
                
                for user in active_users:
                    self.stdout.write(f"\n   User: {user.get_display_name()}")
                    
                    for perm in edit_permissions:
                        has_perm = user.has_permission(perm)
                        status = "YES" if has_perm else "NO"
                        self.stdout.write(f"      {perm}: {status}")
            else:
                self.stdout.write("   No active users found")
            
            test_results.append(("User Permissions", True, f"{active_users.count()} users tested"))
            
        except Exception as e:
            self.stdout.write(f"   ERROR: {str(e)}")
            test_results.append(("User Permissions", False, str(e)))
        
        # Test 6: Views Check
        self.stdout.write("\nTEST 6: Checking View Functions")
        self.stdout.write("-" * 40)
        try:
            from accounts import views
            
            view_functions = [
                'edit_request_create_view',
                'edit_request_list_view', 
                'edit_request_detail_view',
                'edit_request_approval_view',
                'edit_request_withdraw_view'
            ]
            
            missing_views = []
            for view_func in view_functions:
                if hasattr(views, view_func):
                    self.stdout.write(f"   OK: {view_func} exists")
                else:
                    self.stdout.write(f"   MISSING: {view_func}")
                    missing_views.append(view_func)
            
            views_success = len(missing_views) == 0
            views_msg = "All views present" if views_success else f"Missing: {missing_views}"
            test_results.append(("View Functions", views_success, views_msg))
            
        except Exception as e:
            self.stdout.write(f"   ERROR: {str(e)}")
            test_results.append(("View Functions", False, str(e)))
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TEST RESULTS SUMMARY")
        self.stdout.write("=" * 60)
        
        passed_tests = sum(1 for _, success, _ in test_results if success)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, success, detail in test_results:
            status = "PASS" if success else "FAIL"
            self.stdout.write(f"{status:6} | {test_name:25} | {detail}")
        
        self.stdout.write("-" * 60)
        self.stdout.write(f"SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            self.stdout.write(self.style.SUCCESS("\nALL TESTS PASSED! Edit Request System is READY!"))
            self.stdout.write("Next steps:")
            self.stdout.write("1. Run: python manage.py runserver")
            self.stdout.write("2. Visit: http://localhost:8002/edit-requests/")
        else:
            self.stdout.write(self.style.WARNING("\nSome tests failed. Please check the errors above."))
        
        # System Statistics
        self.stdout.write("\nSYSTEM STATISTICS")
        self.stdout.write("-" * 30)
        try:
            self.stdout.write(f"Permissions:        {Permission.objects.count()}")
            self.stdout.write(f"Edit Permissions:   {Permission.objects.filter(name__startswith='receipt_edit').count()}")
            self.stdout.write(f"Roles:              {Role.objects.count()}")
            self.stdout.write(f"Users:              {User.objects.count()}")
            self.stdout.write(f"Active Users:       {User.objects.filter(is_active=True).count()}")
            self.stdout.write(f"Receipts:           {Receipt.objects.count()}")
            self.stdout.write(f"Edit Requests:      {ReceiptEditRequest.objects.count()}")
            self.stdout.write(f"Change Logs:        {ReceiptChangeLog.objects.count()}")
        except Exception as e:
            self.stdout.write(f"Stats error: {e}")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TEST COMPLETE!")
        self.stdout.write("=" * 60)