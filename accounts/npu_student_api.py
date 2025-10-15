"""
NPU Student API Integration Module
Handles communication with NPU Student Authentication API
"""
import requests
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import NPUApiLog


class NPUStudentApiClient:
    """Client for NPU Student Authentication API"""

    def __init__(self):
        self.base_url = settings.NPU_STUDENT_API_SETTINGS['base_url']
        self.auth_endpoint = settings.NPU_STUDENT_API_SETTINGS['auth_endpoint']
        self.headers = settings.NPU_STUDENT_API_SETTINGS['headers']
        self.timeout = settings.NPU_STUDENT_API_SETTINGS['timeout']

    def authenticate_student(self, student_code, password):
        """
        Authenticate student with NPU Student API

        Args:
            student_code (str): รหัสนักศึกษา 12 หลัก
            password (str): รหัสผ่าน

        Returns:
            dict: API response หรือ None หากล้มเหลว
        """
        start_time = time.time()

        url = f"{self.base_url}{self.auth_endpoint}"
        payload = {
            "userLdap": student_code,
            "passLdap": password
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                response_data = response.json()

                # Log successful request
                self._log_api_call(
                    student_code=student_code,
                    action='student_auth',
                    status='success',
                    request_data=payload,
                    response_data=response_data,
                    response_time_ms=response_time_ms
                )

                if response_data.get('success'):
                    return response_data
                else:
                    self._log_api_call(
                        student_code=student_code,
                        action='student_auth',
                        status='failed',
                        request_data=payload,
                        response_data=response_data,
                        response_time_ms=response_time_ms,
                        error_message='Authentication failed - invalid credentials'
                    )
                    return None

            else:
                # Log failed request
                self._log_api_call(
                    student_code=student_code,
                    action='student_auth',
                    status='error',
                    request_data=payload,
                    response_data={'status_code': response.status_code, 'response_text': response.text},
                    response_time_ms=response_time_ms,
                    error_message=f'HTTP {response.status_code}: {response.text}'
                )
                return None

        except requests.exceptions.Timeout:
            error_msg = f'API timeout after {self.timeout} seconds'
            self._log_api_call(
                student_code=student_code,
                action='student_auth',
                status='error',
                request_data=payload,
                error_message=error_msg,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            print(f"NPU Student API Timeout: {error_msg}")
            return None

        except requests.exceptions.ConnectionError:
            error_msg = 'Connection error to NPU Student API'
            self._log_api_call(
                student_code=student_code,
                action='student_auth',
                status='error',
                request_data=payload,
                error_message=error_msg,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            print(f"NPU Student API Connection Error: {error_msg}")
            return None

        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            self._log_api_call(
                student_code=student_code,
                action='student_auth',
                status='error',
                request_data=payload,
                error_message=error_msg,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            print(f"NPU Student API Error: {error_msg}")
            return None

    def _log_api_call(self, student_code, action, status, request_data=None,
                     response_data=None, error_message="", response_time_ms=None):
        """Log API call for monitoring and debugging"""
        try:
            NPUApiLog.objects.create(
                user_ldap_uid=student_code,  # Reuse existing field for student_code
                action=action,
                status=status,
                request_data=request_data,
                response_data=response_data,
                error_message=error_message,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            # Don't let logging errors break the authentication flow
            print(f"Failed to log NPU Student API call: {e}")


def extract_student_data(npu_response):
    """
    Extract and format student data from NPU Student API response

    Args:
        npu_response (dict): NPU Student API response

    Returns:
        dict: Formatted student data for User model

    Example response format:
    {
        "success": true,
        "student_info": {
            "student_code": "666011010079",
            "fullname": "นางสาว ชยุดา ภูชุม",
            "prefix_name": "นางสาว",
            "student_name": "ชยุดา",
            "student_surname": "ภูชุม",
            "level_id": 6,
            "level_name": "ปริญญาโท",
            "program_name": "รัฐประศาสนศาสตร์",
            "degree_name": "รัฐประศาสนศาสตรมหาบัณฑิต",
            "faculty_name": "คณะศิลปศาสตร์และวิทยาศาสตร์",
            "apassword": "666011010079"
        }
    }
    """
    if not npu_response or not npu_response.get('success'):
        return None

    student_info = npu_response.get('student_info', {})

    # Build full name from prefix + first name + last name
    fullname = student_info.get('fullname', '')
    if not fullname:
        prefix = student_info.get('prefix_name', '')
        first_name = student_info.get('student_name', '')
        last_name = student_info.get('student_surname', '')
        fullname = f"{prefix} {first_name} {last_name}".strip()

    return {
        # Basic identification
        'username': student_info.get('student_code', ''),
        'user_type': 'student',

        # Student Information
        'student_code': student_info.get('student_code', ''),
        'student_level': student_info.get('level_name', ''),
        'student_program': student_info.get('program_name', ''),
        'student_faculty': student_info.get('faculty_name', ''),
        'student_degree': student_info.get('degree_name', ''),

        # Personal Information
        'prefix_name': student_info.get('prefix_name', ''),
        'first_name_th': student_info.get('student_name', ''),
        'last_name_th': student_info.get('student_surname', ''),
        'full_name': fullname,

        # Sync metadata
        'last_npu_sync': timezone.now(),
        'npu_last_login': timezone.now(),

        # Auto-approval for students (same as staff)
        'approval_status': 'approved',
        'is_active': True,

        # Student-specific permissions (read-only access to documents)
        'is_document_staff': False,
        'can_forward_documents': False,
    }
