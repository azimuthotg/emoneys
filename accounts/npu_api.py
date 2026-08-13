"""
NPU API Integration Module
Handles communication with NPU AD/LDAP API
"""
import requests
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import NPUApiLog


class NPULookupError(Exception):
    """
    ดึงข้อมูลจาก NPU lookup endpoint ไม่สำเร็จ

    ข้อความใน exception เขียนให้แอดมินอ่านเข้าใจได้เลย เพราะสาเหตุแต่ละแบบ
    แก้คนละทาง — token หมดอายุต้องไปต่ออายุ ส่วนไม่พบข้อมูลแปลว่าคนนั้นอาจพ้นสภาพแล้ว
    """
    pass


class NPUApiClient:
    """Client for NPU AD/LDAP API"""

    def __init__(self):
        self.base_url = settings.NPU_API_SETTINGS['base_url']
        self.auth_endpoint = settings.NPU_API_SETTINGS['auth_endpoint']
        self.lookup_base_url = settings.NPU_API_SETTINGS['lookup_base_url']
        self.headers = settings.NPU_API_SETTINGS['headers']
        self.timeout = settings.NPU_API_SETTINGS['timeout']
    
    def authenticate_user(self, ldap_uid, password):
        """
        Authenticate user with NPU API
        
        Args:
            ldap_uid (str): รหัสบัตรประชาชน 13 หลัก
            password (str): รหัสผ่าน
            
        Returns:
            dict: API response หรือ None หากล้มเหลว
        """
        start_time = time.time()
        
        url = f"{self.base_url}{self.auth_endpoint}"
        payload = {
            "userLdap": ldap_uid,
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
                    user_ldap_uid=ldap_uid,
                    action='auth',
                    status='success',
                    request_data=payload,
                    response_data=response_data,
                    response_time_ms=response_time_ms
                )
                
                if response_data.get('success'):
                    return response_data
                else:
                    self._log_api_call(
                        user_ldap_uid=ldap_uid,
                        action='auth',
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
                    user_ldap_uid=ldap_uid,
                    action='auth',
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
                user_ldap_uid=ldap_uid,
                action='auth',
                status='error',
                request_data=payload,
                error_message=error_msg,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            print(f"NPU API Timeout: {error_msg}")
            return None
            
        except requests.exceptions.ConnectionError:
            error_msg = 'Connection error to NPU API'
            self._log_api_call(
                user_ldap_uid=ldap_uid,
                action='auth',
                status='error',
                request_data=payload,
                error_message=error_msg,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            print(f"NPU API Connection Error: {error_msg}")
            return None
            
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            self._log_api_call(
                user_ldap_uid=ldap_uid,
                action='auth',
                status='error',
                request_data=payload,
                error_message=error_msg,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            print(f"NPU API Error: {error_msg}")
            return None
    
    def lookup_personnel(self, ldap_uid):
        """
        ดึงข้อมูลบุคลากรจากเลขบัตรประชาชน ด้วย JWT อย่างเดียว **ไม่ต้องใช้รหัสผ่านของเจ้าตัว**

        ใช้ตอนแอดมินสั่ง re-sync ให้ผู้ใช้ที่ย้ายหน่วยงาน — ข้อมูล NPU ถูกดึงมาแค่ครั้งเดียว
        ตอนสร้างบัญชี (`_create_staff_user()` ใน backends.py) หลังจากนั้นไม่เคยอัปเดตอีกเลย

        endpoint นี้คืน JSON **แบบแบน** ต่างจาก `authenticate_user()` ที่ห่อด้วย
        `success` / `personnel_info` แต่ชื่อฟิลด์ข้างในเหมือนกันทุกตัว
        จึงห่อให้เป็นรูปเดียวกันก่อนคืนค่า เพื่อให้ `extract_user_data()` ใช้ต่อได้โดยไม่ต้องแก้

        Args:
            ldap_uid (str): รหัสบัตรประชาชน 13 หลัก

        Returns:
            dict: รูปเดียวกับ authenticate_user() — {'success', 'personnel_info', 'additional_info'}

        Raises:
            NPULookupError: พร้อมข้อความภาษาไทยที่บอกสาเหตุให้แอดมินอ่าน
        """
        start_time = time.time()
        url = f"{self.lookup_base_url}personnel/{ldap_uid}/"
        # ไม่ log ตัว token — log แค่ URL ที่เรียก
        request_data = {'method': 'GET', 'url': url}

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response_time_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                personnel_info = response.json()

                self._log_api_call(
                    user_ldap_uid=ldap_uid,
                    action='lookup',
                    status='success',
                    request_data=request_data,
                    response_data=personnel_info,
                    response_time_ms=response_time_ms
                )

                # ห่อให้เป็นรูปเดียวกับ endpoint auth เพื่อส่งต่อให้ extract_user_data()
                return {
                    'success': True,
                    'personnel_info': personnel_info,
                    'additional_info': {},
                }

            # ตอบกลับมาแต่ไม่ใช่ 200 — แยกสาเหตุให้แอดมินรู้ว่าต้องแก้ทางไหน
            if response.status_code == 404:
                message = f'ไม่พบเลขบัตรประชาชน {ldap_uid} ในระบบ NPU (อาจพ้นสภาพแล้ว)'
            elif response.status_code in (401, 403):
                message = 'NPU API ปฏิเสธสิทธิ์ — โทเคนน่าจะหมดอายุ ต้องต่ออายุ NPU_API_TOKEN'
            else:
                message = f'NPU API ตอบกลับ HTTP {response.status_code}'

            self._log_api_call(
                user_ldap_uid=ldap_uid,
                action='lookup',
                status='failed' if response.status_code == 404 else 'error',
                request_data=request_data,
                response_data={'status_code': response.status_code, 'response_text': response.text[:1000]},
                response_time_ms=response_time_ms,
                error_message=message
            )
            raise NPULookupError(message)

        except requests.exceptions.Timeout:
            message = f'NPU API ไม่ตอบสนองภายใน {self.timeout} วินาที'
            self._log_api_call(
                user_ldap_uid=ldap_uid, action='lookup', status='error',
                request_data=request_data, error_message=message,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            raise NPULookupError(message)

        except requests.exceptions.ConnectionError:
            message = 'เชื่อมต่อ NPU API ไม่ได้'
            self._log_api_call(
                user_ldap_uid=ldap_uid, action='lookup', status='error',
                request_data=request_data, error_message=message,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            raise NPULookupError(message)

        except ValueError:
            # ตอบ 200 มาแต่ body ไม่ใช่ JSON
            message = 'NPU API ตอบกลับในรูปแบบที่อ่านไม่ได้ (ไม่ใช่ JSON)'
            self._log_api_call(
                user_ldap_uid=ldap_uid, action='lookup', status='error',
                request_data=request_data, error_message=message,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            raise NPULookupError(message)

    def _log_api_call(self, user_ldap_uid, action, status, request_data=None,
                     response_data=None, error_message="", response_time_ms=None):
        """Log API call for monitoring and debugging"""
        try:
            NPUApiLog.objects.create(
                user_ldap_uid=user_ldap_uid,
                action=action,
                status=status,
                request_data=request_data,
                response_data=response_data,
                error_message=error_message,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            # Don't let logging errors break the authentication flow
            print(f"Failed to log NPU API call: {e}")


def extract_user_data(npu_response):
    """
    Extract and format user data from NPU API response
    
    Args:
        npu_response (dict): NPU API response
        
    Returns:
        dict: Formatted user data for User model
    """
    if not npu_response or not npu_response.get('success'):
        return None
    
    personnel_info = npu_response.get('personnel_info', {})
    additional_info = npu_response.get('additional_info', {})
    
    # Parse birth date
    birth_date = None
    if personnel_info.get('staffbirthdate'):
        try:
            birth_date = datetime.strptime(personnel_info['staffbirthdate'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            birth_date = None
    
    # Parse login time
    npu_last_login = None
    if additional_info.get('login_time'):
        try:
            npu_last_login = timezone.datetime.fromisoformat(additional_info['login_time'])
        except (ValueError, TypeError):
            npu_last_login = timezone.now()
    
    return {
        # Basic identification
        'ldap_uid': personnel_info.get('staffcitizenid', ''),
        'username': personnel_info.get('staffcitizenid', ''),
        
        # NPU Staff Information
        'npu_staff_id': personnel_info.get('staffid', ''),
        
        # Personal Information
        'prefix_name': personnel_info.get('prefixfullname', ''),
        'first_name_th': personnel_info.get('staffname', ''),
        'last_name_th': personnel_info.get('staffsurname', ''),
        'full_name': personnel_info.get('fullname', ''),
        'birth_date': birth_date,
        'gender': personnel_info.get('gendernameth', ''),
        
        # Organization Information
        'department': personnel_info.get('departmentname', ''),
        'position_title': personnel_info.get('posnameth', ''),
        'staff_type': personnel_info.get('stftypename', ''),
        'staff_sub_type': personnel_info.get('substftypename', '') or '',
        'employment_status': personnel_info.get('stfstaname', ''),
        
        # Sync metadata
        'last_npu_sync': timezone.now(),
        'npu_last_login': npu_last_login,
        
        # Default status for new users
        'approval_status': 'pending',
        'is_active': False,  # Will be activated after approval
        
        # Default permissions (can be changed by admin later)
        'is_document_staff': False,
        'can_forward_documents': False,
    }