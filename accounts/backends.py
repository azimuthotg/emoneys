import hashlib
import json
import os
import csv
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from .npu_api import NPUApiClient, extract_user_data

User = get_user_model()


class HybridAuthBackend(BaseBackend):
    """
    Hybrid Authentication Backend for NPU System
    
    Authentication Flow:
    1. Check if user exists in MySQL database
    2. If exists and approved -> authenticate and allow login
    3. If not exists -> call NPU API for authentication
    4. If NPU auth success -> create user in pending status
    5. Admin approval required before user can login
    
    Features:
    - MySQL database lookup first
    - NPU API integration for new users
    - Admin approval workflow
    - Field lock system for local overrides
    - API call logging and monitoring
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
            
        # Special handling for superuser accounts (admin, etc.)
        admin_usernames = ['admin', 'superuser', 'admin_e', 'administrator']
        if username in admin_usernames or username.startswith('admin'):
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                pass
            return None
        
        # Main hybrid authentication flow
        return self._hybrid_authenticate(username, password)
    
    def _hybrid_authenticate(self, ldap_uid, password):
        """
        Hybrid authentication logic
        
        Step 1: Check MySQL database first
        Step 2: If not found, try NPU API
        Step 3: Create user if NPU auth successful
        """
        # Step 1: Check if user exists in database
        existing_user = self._check_database_user(ldap_uid, password)
        if existing_user:
            return existing_user
        
        # Step 2: User not in database, try NPU API
        npu_user = self._authenticate_with_npu_api(ldap_uid, password)
        return npu_user
    
    def _check_database_user(self, ldap_uid, password):
        """Check if user exists in MySQL database and validate"""
        try:
            user = User.objects.get(ldap_uid=ldap_uid)
            
            # User exists, but check their status
            if user.approval_status == 'pending':
                print(f"User {ldap_uid} exists but pending approval")
                return None  # Block login until approved
                
            elif user.approval_status == 'rejected':
                print(f"User {ldap_uid} has been rejected")
                return None  # Block rejected users
                
            elif user.approval_status == 'suspended':
                print(f"User {ldap_uid} is suspended")
                return None  # Block suspended users
                
            elif user.approval_status == 'approved' and user.is_active:
                # User is approved, verify password with NPU API
                # (We always verify with NPU for security, no local passwords)
                if self._verify_npu_password(ldap_uid, password):
                    # Update last login from NPU
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    print(f"Successful login for approved user: {ldap_uid}")
                    return user
                else:
                    print(f"Invalid password for user: {ldap_uid}")
                    return None
            else:
                print(f"User {ldap_uid} in invalid state: {user.approval_status}")
                return None
                
        except User.DoesNotExist:
            # User doesn't exist in database, will try NPU API
            print(f"User {ldap_uid} not found in database")
            return None
        except Exception as e:
            print(f"Error checking database user {ldap_uid}: {e}")
            return None
    
    def _verify_npu_password(self, ldap_uid, password):
        """Verify password with NPU API (for existing users)"""
        npu_client = NPUApiClient()
        result = npu_client.authenticate_user(ldap_uid, password)
        return result is not None and result.get('success', False)
    
    def _authenticate_with_npu_api(self, ldap_uid, password):
        """Authenticate with NPU API and create new user if successful"""
        try:
            # Call NPU API
            npu_client = NPUApiClient()
            npu_response = npu_client.authenticate_user(ldap_uid, password)
            
            if npu_response and npu_response.get('success'):
                # Extract user data from NPU response
                user_data = extract_user_data(npu_response)
                
                if user_data:
                    # Check if user was created between database check and now
                    try:
                        existing_user = User.objects.get(ldap_uid=ldap_uid)
                        print(f"User {ldap_uid} was just created, checking status")
                        
                        if existing_user.approval_status == 'pending':
                            print(f"User {ldap_uid} exists but pending approval")
                            return None  # Don't allow login until approved
                        elif existing_user.approval_status == 'approved':
                            print(f"User {ldap_uid} is approved, allowing login")
                            return existing_user
                        else:
                            print(f"User {ldap_uid} status: {existing_user.approval_status}")
                            return None
                            
                    except User.DoesNotExist:
                        # User still doesn't exist, create new one
                        user = self._create_pending_user(user_data)
                        if user:
                            print(f"Created new pending user from NPU: {ldap_uid}")
                            return None  # Don't allow login until approved
                        else:
                            print(f"Failed to create user from NPU data: {ldap_uid}")
                            return None
                else:
                    print(f"Failed to extract user data from NPU response: {ldap_uid}")
                    return None
            else:
                print(f"NPU authentication failed for: {ldap_uid}")
                return None
                
        except Exception as e:
            print(f"Error during NPU authentication for {ldap_uid}: {e}")
            return None
    
    def _create_pending_user(self, user_data):
        """Create new user in pending approval status"""
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                ldap_uid=user_data['ldap_uid'],
                
                # NPU Staff Information
                npu_staff_id=user_data.get('npu_staff_id', ''),
                
                # Personal Information
                prefix_name=user_data.get('prefix_name', ''),
                first_name_th=user_data.get('first_name_th', ''),
                last_name_th=user_data.get('last_name_th', ''),
                full_name=user_data.get('full_name', ''),
                birth_date=user_data.get('birth_date'),
                gender=user_data.get('gender', ''),
                
                # Organization Information
                department=user_data.get('department', ''),
                position_title=user_data.get('position_title', ''),
                staff_type=user_data.get('staff_type', ''),
                staff_sub_type=user_data.get('staff_sub_type', ''),
                employment_status=user_data.get('employment_status', ''),
                
                # Sync metadata
                last_npu_sync=user_data.get('last_npu_sync'),
                npu_last_login=user_data.get('npu_last_login'),
                
                # User status
                approval_status='pending',
                is_active=False,
                
                # Legacy fields (deprecated)
                is_document_staff=False,
                can_forward_documents=False,
            )
            
            # Don't set password - we always authenticate via NPU
            user.set_unusable_password()
            user.save()
            
            print(f"Successfully created pending user: {user.ldap_uid}")
            return user
            
        except Exception as e:
            print(f"Error creating pending user: {e}")
            return None
    
    def _authenticate_with_file(self, ldap_uid, password):
        """Authenticate with file data and sync user"""
        try:
            # Load user data from file
            user_data = self._load_user_from_file(ldap_uid)
            
            if user_data and self._verify_password(password, user_data.get('password_hash')):
                return self._create_or_update_user(user_data)
                    
        except Exception as e:
            print(f"File Auth Error: {e}")
            
        return None
    
    def _load_user_from_file(self, ldap_uid):
        """Load user data from CSV file"""
        users_file = getattr(settings, 'USERS_FILE_PATH', 'data/users.csv')
        
        if not os.path.exists(users_file):
            return None
            
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('ldap_uid') == ldap_uid:
                        return row
        except Exception as e:
            print(f"Error reading users file: {e}")
            
        return None
    
    def _verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        if not stored_hash:
            return False
            
        # Simple MD5 hash verification (use stronger hashing in production)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        return password_hash == stored_hash
    
    def _create_or_update_user(self, user_data):
        """Create or update user with file data"""
        ldap_uid = user_data.get('ldap_uid')
        
        try:
            # Get existing user or create new one
            user, created = User.objects.get_or_create(
                ldap_uid=ldap_uid,
                defaults={
                    'username': ldap_uid,
                    'is_active': True,
                }
            )
            
            # Check if user data has changed
            user_hash = self._generate_user_hash(user_data)
            stored_hash = getattr(user, '_last_file_hash', None)
            
            if created or user_hash != stored_hash:
                # Update user data from file (respecting field locks)
                self._sync_user_data(user, user_data)
                user._last_file_hash = user_hash
                user.save()
            
            # Check approval status
            if user.is_pending_approval:
                return None  # Block pending users
                
            return user if user.is_active else None
            
        except Exception as e:
            print(f"User sync error: {e}")
            return None
    
    def _sync_user_data(self, user, file_data):
        """Sync user data from file, respecting field locks"""
        # Get locked fields for this user
        locked_fields = []
        if hasattr(user, 'field_locks'):
            locked_fields = user.field_locks.locked_fields
        
        # Mapping of file fields to User model fields
        field_mapping = {
            'full_name': 'full_name',
            'department': 'department', 
            'position_title': 'position_title',
            'staff_type': 'staff_type',
            'employment_status': 'employment_status',
            'contact_email': 'contact_email',
            # Legacy fields (deprecated) - kept for backward compatibility
            # 'is_document_staff': 'is_document_staff',
            # 'can_forward_documents': 'can_forward_documents',
        }
        
        # Update non-locked fields
        for file_field, user_field in field_mapping.items():
            if user_field not in locked_fields:
                value = file_data.get(file_field, '')
                
                # Handle boolean fields (legacy code commented out)
                # if user_field in ['is_document_staff', 'can_forward_documents']:
                #     value = value.lower() in ['true', '1', 'yes', 'y']
                
                setattr(user, user_field, value)
    
    def _generate_user_hash(self, user_data):
        """Generate hash for change detection"""
        relevant_data = {
            'full_name': user_data.get('full_name', ''),
            'department': user_data.get('department', ''),
            'position_title': user_data.get('position_title', ''),
            'contact_email': user_data.get('contact_email', ''),
        }
        return hashlib.md5(json.dumps(relevant_data, sort_keys=True).encode()).hexdigest()
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def create_sample_users_file():
    """Create a sample users.csv file for testing"""
    import os
    
    # Create data directory if it doesn't exist
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    users_data = [
        {
            'ldap_uid': '1234567890123',
            'full_name': 'สมชาย ใจดี',
            'department': 'สำนักงานอธิการบดี',
            'position_title': 'เจ้าหน้าที่บริหารงานทั่วไป',
            'staff_type': 'พนักงานมหาวิทยาลัย',
            'employment_status': 'ปฏิบัติงาน',
            'contact_email': 'somchai@example.com',
            'is_document_staff': 'true',
            'can_forward_documents': 'true',
            'password_hash': hashlib.md5('password123'.encode()).hexdigest()
        },
        {
            'ldap_uid': '9876543210987',
            'full_name': 'สมหญิง รักงาน',
            'department': 'คณะวิทยาศาสตร์',
            'position_title': 'นักวิชาการ',
            'staff_type': 'ข้าราชการ',
            'employment_status': 'ปฏิบัติงาน',
            'contact_email': 'somying@example.com',
            'is_document_staff': 'false',
            'can_forward_documents': 'false',
            'password_hash': hashlib.md5('mypassword'.encode()).hexdigest()
        }
    ]
    
    users_file = os.path.join(data_dir, 'users.csv')
    with open(users_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = users_data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users_data)
    
    print(f"Sample users file created at: {users_file}")
    print("Test users:")
    print("1. ID: 1234567890123, Password: password123")
    print("2. ID: 9876543210987, Password: mypassword")