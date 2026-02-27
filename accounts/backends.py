import hashlib
import json
import os
import csv
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from .npu_api import NPUApiClient, extract_user_data
from .npu_student_api import NPUStudentApiClient, extract_student_data

User = get_user_model()


class HybridAuthBackend(BaseBackend):
    """
    Hybrid Authentication Backend for NPU System (Staff + Student)

    Authentication Flow:
    1. Auto-detect user type from username pattern (13 digits=staff, 12 digits=student)
    2. Try primary endpoint based on detection
    3. If failed, try secondary endpoint as fallback
    4. Create user with auto-approval and appropriate role (Basic User or Student)
    5. User can login immediately after first successful NPU authentication

    Features:
    - Smart user type detection (staff vs student)
    - Fallback strategy (try both endpoints if needed)
    - MySQL database lookup first
    - NPU Staff API + NPU Student API integration
    - Auto-approval for NPU-authenticated users
    - Automatic role assignment (Basic User for staff, Student for students)
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

        # NEW: Check for manual users first (before NPU API)
        manual_user = self._check_manual_user(username, password)
        if manual_user:
            return manual_user

        # Main smart authentication flow with fallback (NPU API)
        return self._smart_authenticate(username, password)

    def _smart_authenticate(self, username, password):
        """
        Smart authentication with auto-detect and fallback

        Strategy:
        1. Detect probable user type from username pattern
        2. Try primary endpoint first (based on detection)
        3. If failed, try secondary endpoint (fallback)
        4. Log unexpected patterns for monitoring
        """
        # Step 1: Detect probable user type
        probable_type = self._detect_probable_user_type(username)

        # Step 2: Try authentication in order of probability
        if probable_type == 'staff':
            # Try Staff API first
            user = self._try_staff_auth(username, password)
            if user:
                return user

            # Fallback: Try Student API
            print(f"Staff auth failed for {username}, trying Student API as fallback")
            user = self._try_student_auth(username, password)
            if user:
                self._log_unexpected_pattern(username, detected='staff', actual='student')
                return user

        elif probable_type == 'student':
            # Try Student API first
            user = self._try_student_auth(username, password)
            if user:
                return user

            # Fallback: Try Staff API
            print(f"Student auth failed for {username}, trying Staff API as fallback")
            user = self._try_staff_auth(username, password)
            if user:
                self._log_unexpected_pattern(username, detected='student', actual='staff')
                return user

        else:
            # Unknown pattern: try both
            print(f"Unknown username pattern: {username}, trying both endpoints")
            user = self._try_staff_auth(username, password)
            if user:
                return user
            user = self._try_student_auth(username, password)
            if user:
                return user

        return None

    def _detect_probable_user_type(self, username):
        """
        Detect probable user type from username pattern

        Rules:
        - 13 digits → probably staff (citizen ID)
        - 12 digits → probably student (student code)
        - Other → unknown
        """
        username_clean = username.strip()

        # All digits check
        if not username_clean.isdigit():
            return 'unknown'

        # Length-based detection
        if len(username_clean) == 13:
            return 'staff'
        elif len(username_clean) == 12:
            return 'student'

        return 'unknown'

    def _try_staff_auth(self, ldap_uid, password):
        """
        Try to authenticate as staff
        Returns User object if successful, None otherwise
        """
        try:
            # Check database first (staff users only)
            existing_user = self._check_database_staff(ldap_uid, password)
            if existing_user:
                return existing_user

            # Try NPU Staff API
            return self._authenticate_with_staff_api(ldap_uid, password)

        except Exception as e:
            print(f"Staff auth error for {ldap_uid}: {e}")
            return None

    def _try_student_auth(self, student_code, password):
        """
        Try to authenticate as student
        Returns User object if successful, None otherwise
        """
        try:
            # Check database first (student users only)
            existing_user = self._check_database_student(student_code, password)
            if existing_user:
                return existing_user

            # Try NPU Student API
            return self._authenticate_with_student_api(student_code, password)

        except Exception as e:
            print(f"Student auth error for {student_code}: {e}")
            return None

    def _log_unexpected_pattern(self, username, detected, actual):
        """
        Log cases where auto-detection was wrong
        This helps improve detection logic
        """
        print(f"⚠️ UNEXPECTED PATTERN: {username}")
        print(f"   Detected as: {detected}")
        print(f"   Actually is: {actual}")
        print(f"   Length: {len(username)} digits")

        # TODO: Save to database for analysis (future enhancement)

    def _check_manual_user(self, username, password):
        """
        Check if user is a manual user and authenticate with local password

        Manual users have:
        - source = 'manual'
        - usable password (set by admin)
        - Can be staff or student type

        Returns User object if authentication successful, None otherwise
        """
        try:
            # Try to find manual user by username, ldap_uid (staff), or student_code (student)
            manual_user = None

            # Try username first (most common for manual users)
            try:
                manual_user = User.objects.get(
                    username=username,
                    source='manual'
                )
            except User.DoesNotExist:
                pass

            # Try staff ldap_uid if not found by username
            if not manual_user:
                try:
                    manual_user = User.objects.get(
                        ldap_uid=username,
                        source='manual',
                        user_type='staff'
                    )
                except User.DoesNotExist:
                    pass

            # Try student_code if still not found
            if not manual_user:
                try:
                    manual_user = User.objects.get(
                        student_code=username,
                        source='manual',
                        user_type='student'
                    )
                except User.DoesNotExist:
                    pass

            # If found, verify password
            if manual_user:
                # Check approval status
                if manual_user.approval_status != 'approved' or not manual_user.is_active:
                    print(f"Manual user {username} is not approved or inactive")
                    return None

                # Verify password
                if manual_user.has_usable_password() and manual_user.check_password(password):
                    # Update last login
                    manual_user.last_login = timezone.now()
                    manual_user.save(update_fields=['last_login'])
                    print(f"✓ Manual user login successful: {username} ({manual_user.user_type})")
                    return manual_user
                else:
                    print(f"Invalid password for manual user: {username}")
                    return None

            return None

        except Exception as e:
            print(f"Error checking manual user {username}: {e}")
            return None

    # === STAFF AUTHENTICATION METHODS ===

    def _check_database_staff(self, ldap_uid, password):
        """Check if staff user exists in MySQL database and validate"""
        try:
            user = User.objects.get(ldap_uid=ldap_uid, user_type='staff')

            # User exists, but check their status
            if user.approval_status == 'pending':
                print(f"Staff user {ldap_uid} exists but pending approval")
                return None  # Block login until approved

            elif user.approval_status == 'rejected':
                print(f"Staff user {ldap_uid} has been rejected")
                return None  # Block rejected users

            elif user.approval_status == 'suspended':
                print(f"Staff user {ldap_uid} is suspended")
                return None  # Block suspended users

            elif user.approval_status == 'approved' and user.is_active:
                # Check if admin has set a local password override
                if user.has_usable_password():
                    # Use local password (NPU password may be forgotten/changed)
                    if user.check_password(password):
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        print(f"✓ Staff login via local override: {ldap_uid}")
                        return user
                    else:
                        print(f"Invalid local override password for staff: {ldap_uid}")
                        return None
                else:
                    # No local override — verify with NPU API as normal
                    if self._verify_npu_staff_password(ldap_uid, password):
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        print(f"✓ Staff login via NPU API: {ldap_uid}")
                        return user
                    else:
                        print(f"Invalid NPU password for staff: {ldap_uid}")
                        return None
            else:
                print(f"Staff user {ldap_uid} in invalid state: {user.approval_status}")
                return None

        except User.DoesNotExist:
            # Staff user doesn't exist in database, will try NPU API
            print(f"Staff user {ldap_uid} not found in database")
            return None
        except Exception as e:
            print(f"Error checking database staff user {ldap_uid}: {e}")
            return None
    
    def _verify_npu_staff_password(self, ldap_uid, password):
        """Verify staff password with NPU Staff API (for existing staff users)"""
        npu_client = NPUApiClient()
        result = npu_client.authenticate_user(ldap_uid, password)
        return result is not None and result.get('success', False)

    def _authenticate_with_staff_api(self, ldap_uid, password):
        """Authenticate with NPU Staff API and create new staff user if successful"""
        try:
            # Call NPU Staff API
            npu_client = NPUApiClient()
            npu_response = npu_client.authenticate_user(ldap_uid, password)

            if npu_response and npu_response.get('success'):
                # Extract user data from NPU response
                user_data = extract_user_data(npu_response)

                if user_data:
                    # Check if user was created between database check and now
                    try:
                        existing_user = User.objects.get(ldap_uid=ldap_uid, user_type='staff')
                        print(f"Staff user {ldap_uid} was just created, checking status")

                        if existing_user.approval_status == 'pending':
                            print(f"Staff user {ldap_uid} exists but pending approval")
                            return None  # Don't allow login until approved
                        elif existing_user.approval_status == 'approved':
                            print(f"Staff user {ldap_uid} is approved, allowing login")
                            return existing_user
                        else:
                            print(f"Staff user {ldap_uid} status: {existing_user.approval_status}")
                            return None

                    except User.DoesNotExist:
                        # User still doesn't exist, create new one with auto-approval
                        user = self._create_staff_user(user_data)
                        if user:
                            # User is auto-approved, allow immediate login
                            print(f"✓ New staff created: {ldap_uid}")
                            return user
                        else:
                            print(f"Failed to create staff user from NPU data: {ldap_uid}")
                            return None
                else:
                    print(f"Failed to extract staff user data from NPU response: {ldap_uid}")
                    return None
            else:
                print(f"NPU Staff API authentication failed for: {ldap_uid}")
                return None

        except Exception as e:
            print(f"Error during NPU Staff API authentication for {ldap_uid}: {e}")
            return None
    
    def _create_staff_user(self, user_data):
        """
        Create new staff user with auto-approval for NPU staff

        All staff authenticated via NPU Staff API are automatically
        approved with Basic User role.
        """
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                ldap_uid=user_data['ldap_uid'],

                # User type
                user_type='staff',

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

                # User status - AUTO-APPROVE NPU staff
                approval_status='approved',
                is_active=True,
                approved_at=timezone.now(),

                # Legacy fields (deprecated)
                is_document_staff=False,
                can_forward_documents=False,
            )

            # Don't set password - we always authenticate via NPU
            user.set_unusable_password()
            user.save()

            # Auto-assign "Basic User" role to new NPU staff
            try:
                from .models import Role
                basic_user_role = Role.objects.get(name='basic_user', is_active=True)
                user.assign_role(basic_user_role)
                print(f"Successfully created and auto-approved NPU staff: {user.ldap_uid} with Basic User role")
            except Role.DoesNotExist:
                print(f"Warning: 'basic_user' role not found. User {user.ldap_uid} created without role.")
            except Exception as role_error:
                print(f"Warning: Failed to assign role to {user.ldap_uid}: {role_error}")

            return user

        except Exception as e:
            print(f"Error creating staff user: {e}")
            return None

    # === STUDENT AUTHENTICATION METHODS ===

    def _check_database_student(self, student_code, password):
        """Check if student user exists in MySQL database and validate"""
        try:
            user = User.objects.get(student_code=student_code, user_type='student')

            # User exists, but check their status
            if user.approval_status == 'pending':
                print(f"Student user {student_code} exists but pending approval")
                return None  # Block login until approved

            elif user.approval_status == 'rejected':
                print(f"Student user {student_code} has been rejected")
                return None  # Block rejected users

            elif user.approval_status == 'suspended':
                print(f"Student user {student_code} is suspended")
                return None  # Block suspended users

            elif user.approval_status == 'approved' and user.is_active:
                # Check if admin has set a local password override
                if user.has_usable_password():
                    # Use local password (NPU password may be forgotten/changed)
                    if user.check_password(password):
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        print(f"✓ Student login via local override: {student_code}")
                        return user
                    else:
                        print(f"Invalid local override password for student: {student_code}")
                        return None
                else:
                    # No local override — verify with NPU Student API as normal
                    if self._verify_npu_student_password(student_code, password):
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        print(f"✓ Student login via NPU API: {student_code}")
                        return user
                    else:
                        print(f"Invalid NPU password for student: {student_code}")
                        return None
            else:
                print(f"Student user {student_code} in invalid state: {user.approval_status}")
                return None

        except User.DoesNotExist:
            # Student user doesn't exist in database, will try NPU API
            print(f"Student user {student_code} not found in database")
            return None
        except Exception as e:
            print(f"Error checking database student user {student_code}: {e}")
            return None

    def _verify_npu_student_password(self, student_code, password):
        """Verify student password with NPU Student API (for existing student users)"""
        try:
            student_client = NPUStudentApiClient()
            response = student_client.authenticate_student(student_code, password)
            return response and response.get('success', False)
        except Exception as e:
            print(f"Student password verification error: {e}")
            return False

    def _authenticate_with_student_api(self, student_code, password):
        """Authenticate with NPU Student API and create new student user if successful"""
        try:
            # Call NPU Student API
            student_client = NPUStudentApiClient()
            npu_response = student_client.authenticate_student(student_code, password)

            if npu_response and npu_response.get('success'):
                # Extract student data from NPU response
                student_data = extract_student_data(npu_response)

                if student_data:
                    # Check if user was created between database check and now
                    try:
                        existing_user = User.objects.get(student_code=student_code, user_type='student')
                        print(f"Student user {student_code} was just created, checking status")

                        if existing_user.approval_status == 'pending':
                            print(f"Student user {student_code} exists but pending approval")
                            return None
                        elif existing_user.approval_status == 'approved':
                            print(f"Student user {student_code} is approved, allowing login")
                            return existing_user
                        else:
                            print(f"Student user {student_code} status: {existing_user.approval_status}")
                            return None

                    except User.DoesNotExist:
                        # User still doesn't exist, create new one with auto-approval
                        user = self._create_student_user(student_data)
                        if user:
                            print(f"✓ New student created: {student_code}")
                            return user
                        else:
                            print(f"Failed to create student user: {student_code}")
                            return None
                else:
                    print(f"Failed to extract student data from NPU response: {student_code}")
                    return None
            else:
                print(f"NPU Student API authentication failed for: {student_code}")
                return None

        except Exception as e:
            print(f"Error during NPU Student API authentication for {student_code}: {e}")
            return None

    def _create_student_user(self, student_data):
        """
        Create new student user with auto-approval

        All students authenticated via NPU Student API are automatically
        approved with Student role.
        """
        try:
            user = User.objects.create_user(
                username=student_data['username'],

                # User type
                user_type='student',

                # Student Information
                student_code=student_data['student_code'],
                student_level=student_data.get('student_level', ''),
                student_program=student_data.get('student_program', ''),
                student_faculty=student_data.get('student_faculty', ''),
                student_degree=student_data.get('student_degree', ''),

                # Personal Information
                prefix_name=student_data.get('prefix_name', ''),
                first_name_th=student_data.get('first_name_th', ''),
                last_name_th=student_data.get('last_name_th', ''),
                full_name=student_data.get('full_name', ''),

                # Sync metadata
                last_npu_sync=student_data.get('last_npu_sync'),
                npu_last_login=student_data.get('npu_last_login'),

                # User status - AUTO-APPROVE NPU students
                approval_status='approved',
                is_active=True,
                approved_at=timezone.now(),
            )

            # Don't set password - we always authenticate via NPU
            user.set_unusable_password()
            user.save()

            # Auto-assign "Student" role to new NPU students
            try:
                from .models import Role
                student_role = Role.objects.get(name='student', is_active=True)
                user.assign_role(student_role)
                print(f"Successfully created and auto-approved NPU student: {user.student_code} with Student role")
            except Role.DoesNotExist:
                print(f"Warning: 'student' role not found. User {user.student_code} created without role.")
            except Exception as role_error:
                print(f"Warning: Failed to assign role to {user.student_code}: {role_error}")

            return user

        except Exception as e:
            print(f"Error creating student user: {e}")
            return None

    # === FILE-BASED AUTHENTICATION (Legacy) ===

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