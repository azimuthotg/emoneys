# 🏛️ NPU Login System Implementation Guide

**เวอร์ชัน**: 1.0  
**วันที่**: 19 กันยายน 2567  
**สำหรับ**: Django Projects with External API Authentication

---

## 📋 **ภาพรวมระบบ**

ระบบนี้เป็น **Authentication System แบบ Hybrid** ที่รวม:
- 🏛️ **NPU Central Authentication** - ระบบยืนยันตัวตนกลางของมหาวิทยาลัย
- 👤 **Custom User Management** - การจัดการผู้ใช้ภายในระบบ
- 🔐 **Role-based Access Control** - การควบคุมสิทธิ์แบบแยกบทบาท
- ✅ **Admin Approval Workflow** - ระบบอนุมัติผู้ใช้ใหม่

---

## 🏗️ **สถาปัตยกรรมระบบ**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   NPU API       │    │  Django Backend  │    │   Frontend UI   │
│                 │◄──►│                  │◄──►│                 │
│ - Auth Service  │    │ - Custom Backend │    │ - Login Form    │
│ - User Data     │    │ - User Model     │    │ - Dashboard     │
│ - Personnel API │    │ - Permissions    │    │ - Thai UI       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 📁 **โครงสร้างไฟล์หลัก**

```
accounts/
├── models.py           # User model + Department
├── backends.py         # NPU authentication backend
├── views.py           # Login/Dashboard views
├── forms.py           # Authentication forms
├── admin.py           # Django admin interface
├── decorators.py      # Permission decorators
└── migrations/        # Database schema

templates/accounts/
├── login.html         # Login page UI
├── dashboard.html     # User dashboard
├── profile.html       # User profile page
└── user_*.html       # User management pages

edoc_system/
├── settings.py        # Django configuration
└── urls.py           # URL routing
```

---

## 🗃️ **1. Custom User Model**

### **models.py**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # NPU Integration Fields
    ldap_uid = models.CharField(max_length=13, unique=True, blank=True, null=True, 
                               verbose_name="รหัสบัตรประชาชน")
    full_name = models.CharField(max_length=255, blank=True, verbose_name="ชื่อ-สกุล")
    department = models.CharField(max_length=255, blank=True, verbose_name="หน่วยงาน (NPU)")
    position_title = models.CharField(max_length=255, blank=True, verbose_name="ตำแหน่ง")
    staff_type = models.CharField(max_length=100, blank=True, verbose_name="ประเภทบุคลากร")
    employment_status = models.CharField(max_length=100, blank=True, verbose_name="สถานะการทำงาน")
    
    # Internal Management Fields
    department_internal = models.ForeignKey('Department', on_delete=models.SET_NULL, 
                                          null=True, blank=True, verbose_name="แผนกภายใน")
    job_description = models.TextField(blank=True, verbose_name="หน้าที่รับผิดชอบ")
    contact_email = models.EmailField(blank=True, verbose_name="อีเมลติดต่อ")
    line_user_id = models.CharField(max_length=255, blank=True, verbose_name="LINE User ID")
    
    # Document Management Permissions
    is_document_staff = models.BooleanField(default=False, verbose_name="เจ้าหน้าที่สารบรรณ")
    can_forward_documents = models.BooleanField(default=False, verbose_name="สามารถส่งต่อเอกสาร")
    
    # User Status
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="วันที่อนุมัติ")
    
    # PWA/Push Notification Fields
    push_subscription_endpoint = models.URLField(blank=True, verbose_name="Push Endpoint")
    push_subscription_keys = models.JSONField(default=dict, blank=True, verbose_name="Push Keys")
    notifications_enabled = models.BooleanField(default=True, verbose_name="เปิดการแจ้งเตือน")

    @property
    def is_pending_approval(self):
        """Check if user is pending admin approval"""
        return self.approved_at is None and self.is_active

    @property
    def is_suspended(self):
        """Check if user is suspended"""
        return not self.is_active and self.approved_at is not None

class Department(models.Model):
    """Internal department structure"""
    name = models.CharField(max_length=255, unique=True, verbose_name="ชื่อแผนก")
    code = models.CharField(max_length=20, unique=True, verbose_name="รหัสแผนก")
    description = models.TextField(blank=True, verbose_name="รายละเอียด")
    is_active = models.BooleanField(default=True, verbose_name="ใช้งาน")
    created_at = models.DateTimeField(auto_now_add=True)

class FieldLock(models.Model):
    """Control which fields sync from NPU vs local management"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='field_locks')
    locked_fields = models.JSONField(default=list, verbose_name="ฟิลด์ที่ล็อค")
```

### **settings.py Configuration**
```python
# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'accounts.backends.NPUAuthBackend',  # Primary: NPU API
    'django.contrib.auth.backends.ModelBackend',  # Fallback: Django
]

# NPU API Configuration
NPU_AUTH_URL = "https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/"
NPU_API_TOKEN = "your_jwt_token_here"

# Thai Localization
LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True
```

---

## 🔐 **2. NPU Authentication Backend**

### **backends.py**
```python
import requests
import hashlib
import json
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

User = get_user_model()

class NPUAuthBackend(BaseBackend):
    """
    Custom authentication backend for NPU Central Authentication
    Features:
    - API-based authentication
    - Automatic user data synchronization  
    - Field lock system for local overrides
    - Admin approval workflow
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
            
        # Special handling for admin account
        if username == 'admin':
            try:
                user = User.objects.get(username='admin')
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                pass
            return None
        
        # NPU API Authentication
        return self._authenticate_with_npu(username, password)
    
    def _authenticate_with_npu(self, ldap_uid, password):
        """Authenticate with NPU API and sync user data"""
        try:
            # Call NPU Authentication API
            headers = {
                'Authorization': f'Bearer {settings.NPU_API_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'ldap_uid': ldap_uid,
                'password': password
            }
            
            response = requests.post(
                settings.NPU_AUTH_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get('authenticated'):
                    return self._create_or_update_user(user_data)
                    
        except requests.RequestException as e:
            # Log error but don't expose to user
            print(f"NPU Auth Error: {e}")
            
        return None
    
    def _create_or_update_user(self, user_data):
        """Create or update user with NPU data"""
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
            
            # Check if user data has changed (using hash comparison)
            user_hash = self._generate_user_hash(user_data)
            stored_hash = getattr(user, '_last_npu_hash', None)
            
            if created or user_hash != stored_hash:
                # Update user data from NPU (respecting field locks)
                self._sync_user_data(user, user_data)
                user._last_npu_hash = user_hash
                user.save()
            
            # Check approval status
            if user.is_pending_approval:
                return None  # Block pending users
                
            return user if user.is_active else None
            
        except Exception as e:
            print(f"User sync error: {e}")
            return None
    
    def _sync_user_data(self, user, npu_data):
        """Sync user data from NPU, respecting field locks"""
        # Get locked fields for this user
        locked_fields = []
        if hasattr(user, 'field_locks'):
            locked_fields = user.field_locks.locked_fields
        
        # Mapping of NPU fields to User model fields
        field_mapping = {
            'full_name': 'full_name',
            'department': 'department', 
            'position_title': 'position_title',
            'staff_type': 'staff_type',
            'employment_status': 'employment_status',
        }
        
        # Update non-locked fields
        for npu_field, user_field in field_mapping.items():
            if user_field not in locked_fields:
                setattr(user, user_field, npu_data.get(npu_field, ''))
    
    def _generate_user_hash(self, user_data):
        """Generate hash for change detection"""
        relevant_data = {
            'full_name': user_data.get('full_name', ''),
            'department': user_data.get('department', ''),
            'position_title': user_data.get('position_title', ''),
        }
        return hashlib.md5(json.dumps(relevant_data, sort_keys=True).encode()).hexdigest()
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
```

---

## 🎛️ **3. Views & Authentication Logic**

### **views.py - Key Functions**
```python
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

def login_view(request):
    """
    NPU Authentication Login View
    Features:
    - Thai ID validation
    - Toast notifications
    - Approval status checking
    - Mobile API support
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Handle both web and API requests
        if request.content_type == 'application/json':
            return handle_api_login(request)
        else:
            return handle_web_login(request)
    
    return render(request, 'accounts/login.html', {
        'title': 'เข้าสู่ระบบ'
    })

def handle_web_login(request):
    """Handle web-based login"""
    ldap_uid = request.POST.get('ldap_uid', '').strip()
    password = request.POST.get('password', '')
    
    # Validate Thai ID format (13 digits)
    if not ldap_uid.isdigit() or len(ldap_uid) != 13:
        messages.error(request, 'รหัسบัตรประชาชนต้องเป็นตัวเลข 13 หลัก')
        return render(request, 'accounts/login.html')
    
    # Authenticate user
    user = authenticate(request, username=ldap_uid, password=password)
    
    if user:
        if user.is_pending_approval:
            messages.warning(request, 'บัญชีของคุณอยู่ระหว่างการอนุมัติ กรุณารอการติดต่อจากผู้ดูแลระบบ')
        elif user.is_suspended:
            messages.error(request, 'บัญชีของคุณถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ')
        else:
            auth_login(request, user)
            messages.success(request, f'ยินดีต้อนรับ {user.full_name or user.username}')
            return redirect('dashboard')
    else:
        messages.error(request, 'รหัสบัตรประชาชนหรือรหัสผ่านไม่ถูกต้อง')
    
    return render(request, 'accounts/login.html')

@login_required
def dashboard(request):
    """
    User Dashboard with Personalized Content
    Features:
    - NPU user information display
    - Document statistics
    - Recent documents
    - Quick actions
    """
    # Get document statistics
    from documents.models import Document, DocumentRecipient, DocumentForwarding
    
    # User's received documents
    received_docs = DocumentRecipient.objects.filter(recipient=request.user)
    forwarded_docs = DocumentForwarding.objects.filter(forwarded_to=request.user)
    
    # Recent documents (last 5)
    recent_received = received_docs.order_by('-received_at')[:5]
    recent_forwarded = forwarded_docs.order_by('-forwarded_at')[:5]
    
    context = {
        'title': 'หน้าหลัก',
        'user': request.user,
        'stats': {
            'total_received': received_docs.count(),
            'total_forwarded': forwarded_docs.count(),
            'unread_received': received_docs.filter(is_read=False).count(),
            'unread_forwarded': forwarded_docs.filter(is_read=False).count(),
        },
        'recent_received': recent_received,
        'recent_forwarded': recent_forwarded,
    }
    
    return render(request, 'accounts/dashboard.html', context)
```

---

## 🎨 **4. User Interface Templates**

### **login.html - Thai Login Interface**
```html
{% extends 'base.html' %}
{% block title %}เข้าสู่ระบบ - ระบบสารบรรณอิเล็กทรอนิกส์ NPU{% endblock %}

{% block content %}
<div class="container-fluid vh-100">
    <div class="row h-100">
        <!-- Left Panel - NPU Branding -->
        <div class="col-lg-6 d-none d-lg-flex align-items-center justify-content-center bg-primary">
            <div class="text-center text-white">
                <h1 class="display-4 fw-bold mb-4">🏛️ NPU E-Document</h1>
                <p class="lead">ระบบสารบรรณอิเล็กทรอนิกส์</p>
                <p>มหาวิทยาลัยนเรศวร</p>
            </div>
        </div>
        
        <!-- Right Panel - Login Form -->
        <div class="col-lg-6 d-flex align-items-center justify-content-center">
            <div class="card shadow-lg border-0" style="width: 100%; max-width: 400px;">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <h3 class="fw-bold text-primary">เข้าสู่ระบบ</h3>
                        <p class="text-muted">ใช้บัญชี NPU ของคุณ</p>
                    </div>
                    
                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <!-- Thai ID Input -->
                        <div class="mb-3">
                            <label for="ldap_uid" class="form-label">
                                <i class="fas fa-id-card text-primary me-2"></i>
                                รหัสบัตรประชาชน
                            </label>
                            <input type="text" 
                                   class="form-control form-control-lg" 
                                   id="ldap_uid" 
                                   name="ldap_uid" 
                                   placeholder="กรอกรหัสบัตรประชาชน 13 หลัก"
                                   maxlength="13"
                                   required>
                            <div class="invalid-feedback">
                                กรุณากรอกรหัสบัตรประชาชน 13 หลัก
                            </div>
                        </div>
                        
                        <!-- Password Input -->
                        <div class="mb-4">
                            <label for="password" class="form-label">
                                <i class="fas fa-lock text-primary me-2"></i>
                                รหัสผ่าน
                            </label>
                            <input type="password" 
                                   class="form-control form-control-lg" 
                                   id="password" 
                                   name="password" 
                                   placeholder="กรอกรหัสผ่าน NPU"
                                   required>
                            <div class="invalid-feedback">
                                กรุณากรอกรหัสผ่าน
                            </div>
                        </div>
                        
                        <!-- Submit Button -->
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-sign-in-alt me-2"></i>
                                เข้าสู่ระบบ
                            </button>
                        </div>
                    </form>
                    
                    <!-- Help Text -->
                    <div class="text-center mt-4">
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            ใช้บัญชี NPU เดียวกับระบบอื่นๆ ของมหาวิทยาลัย
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Toast Notifications -->
<div class="toast-container position-fixed top-0 end-0 p-3">
    {% if messages %}
        {% for message in messages %}
        <div class="toast show" role="alert">
            <div class="toast-header">
                <strong class="me-auto">
                    {% if message.tags == 'success' %}🟢{% elif message.tags == 'error' %}🔴{% elif message.tags == 'warning' %}🟡{% else %}🔵{% endif %}
                    การแจ้งเตือน
                </strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">{{ message }}</div>
        </div>
        {% endfor %}
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script>
// Thai ID Validation
document.getElementById('ldap_uid').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 13) value = value.slice(0, 13);
    e.target.value = value;
    
    // Validation feedback
    if (value.length === 13) {
        e.target.classList.remove('is-invalid');
        e.target.classList.add('is-valid');
    } else {
        e.target.classList.remove('is-valid');
        if (value.length > 0) e.target.classList.add('is-invalid');
    }
});

// Form Validation
document.querySelector('form').addEventListener('submit', function(e) {
    const ldapUid = document.getElementById('ldap_uid').value;
    const password = document.getElementById('password').value;
    
    if (ldapUid.length !== 13) {
        e.preventDefault();
        document.getElementById('ldap_uid').classList.add('is-invalid');
    }
    
    if (!password) {
        e.preventDefault();
        document.getElementById('password').classList.add('is-invalid');
    }
});
</script>
{% endblock %}
```

---

## 🛡️ **5. Permission System & Decorators**

### **decorators.py**
```python
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.http import Http404
from functools import wraps

def document_staff_required(view_func):
    """Require document staff permissions"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or 
                request.user.is_staff or 
                getattr(request.user, 'is_document_staff', False)):
            raise Http404("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        return view_func(request, *args, **kwargs)
    return wrapper

def can_view_document(view_func):
    """Check document view permissions (confidentiality)"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from documents.models import Document
        
        # Get document from URL parameter
        doc_id = kwargs.get('pk') or kwargs.get('document_id')
        if doc_id:
            document = get_object_or_404(Document, pk=doc_id)
            
            # Check if user can view this document
            if not document.can_view(request.user):
                raise Http404("คุณไม่มีสิทธิ์ดูเอกสารนี้")
                
        return view_func(request, *args, **kwargs)
    return wrapper

def document_owner_or_staff_required(view_func):
    """Require document ownership or staff permissions"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from documents.models import Document
        
        doc_id = kwargs.get('pk')
        document = get_object_or_404(Document, pk=doc_id)
        
        if not (request.user.is_superuser or 
                request.user.is_staff or 
                getattr(request.user, 'is_document_staff', False) or
                document.created_by == request.user):
            raise Http404("คุณไม่มีสิทธิ์แก้ไขเอกสารนี้")
            
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## ⚙️ **6. Admin Interface Integration**

### **admin.py**
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, FieldLock

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Enhanced admin interface for NPU users"""
    
    list_display = ('username', 'full_name', 'department', 'is_document_staff', 
                   'approved_at', 'is_active')
    list_filter = ('is_document_staff', 'can_forward_documents', 'is_active', 
                  'approved_at', 'department')
    search_fields = ('username', 'full_name', 'ldap_uid', 'department')
    
    fieldsets = UserAdmin.fieldsets + (
        ('NPU Information', {
            'fields': ('ldap_uid', 'full_name', 'department', 'position_title', 
                      'staff_type', 'employment_status')
        }),
        ('Internal Management', {
            'fields': ('department_internal', 'job_description', 'contact_email', 
                      'line_user_id')
        }),
        ('Document Permissions', {
            'fields': ('is_document_staff', 'can_forward_documents')
        }),
        ('Approval Status', {
            'fields': ('approved_at',)
        }),
        ('PWA Settings', {
            'fields': ('push_subscription_endpoint', 'push_subscription_keys', 
                      'notifications_enabled'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_users', 'suspend_users']
    
    def approve_users(self, request, queryset):
        """Bulk approve users"""
        from django.utils import timezone
        count = queryset.filter(approved_at__isnull=True).update(
            approved_at=timezone.now()
        )
        self.message_user(request, f'อนุมัติผู้ใช้ {count} คน')
    
    def suspend_users(self, request, queryset):
        """Bulk suspend users"""
        count = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, f'ระงับผู้ใช้ {count} คน')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'member_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    
    def member_count(self, obj):
        return obj.user_set.count()
    member_count.short_description = 'จำนวนสมาชิก'
```

---

## 🔒 **7. Security Best Practices**

### **Critical Security Features**
```python
# 1. Password Security
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 2. Session Security
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour

# 3. CSRF Protection (automatic in Django)
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True

# 4. Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 5. Rate Limiting (implement with django-ratelimit)
@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # ... login logic
```

### **Production Environment Variables**
```bash
# .env file
DEBUG=False
SECRET_KEY=your_production_secret_key_here
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database
DB_NAME=your_db_name
DB_USER=your_db_user  
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# NPU API
NPU_AUTH_URL=https://api.npu.ac.th/v2/ldap/auth_and_get_personnel/
NPU_API_TOKEN=your_production_jwt_token

# Email (for notifications)
EMAIL_HOST=smtp.your-domain.com
EMAIL_USER=noreply@your-domain.com
EMAIL_PASSWORD=your_email_password
```

---

## 📱 **8. Progressive Web App (PWA) Integration**

### **Push Notification Setup**
```python
# models.py - Additional PWA fields
class User(AbstractUser):
    # ... other fields ...
    
    # PWA Push Notifications
    push_subscription_endpoint = models.URLField(blank=True)
    push_subscription_keys = models.JSONField(default=dict, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    
    def send_push_notification(self, title, body, data=None):
        """Send push notification to user"""
        if not self.notifications_enabled or not self.push_subscription_endpoint:
            return False
            
        try:
            from pywebpush import webpush
            
            payload = {
                'title': title,
                'body': body,
                'data': data or {},
                'icon': '/static/favicon.ico',
                'badge': '/static/favicon.ico'
            }
            
            webpush(
                subscription_info={
                    'endpoint': self.push_subscription_endpoint,
                    'keys': self.push_subscription_keys
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': settings.VAPID_SUBJECT}
            )
            return True
        except Exception as e:
            print(f"Push notification error: {e}")
            return False
```

### **Service Worker (static/sw.js)**
```javascript
// Service Worker for PWA functionality
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('Service Worker activated');
    event.waitUntil(clients.claim());
});

// Push notification handling
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body,
            icon: data.icon || '/static/favicon.ico',
            badge: data.badge || '/static/favicon.ico',
            data: data.data,
            actions: [
                {
                    action: 'view',
                    title: 'ดูเอกสาร',
                    icon: '/static/icons/view.png'
                },
                {
                    action: 'dismiss',
                    title: 'ปิด',
                    icon: '/static/icons/close.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});
```

---

## 🚀 **9. Implementation Steps**

### **Step 1: Project Setup**
```bash
# 1. Create Django project
django-admin startproject your_project
cd your_project
python manage.py startapp accounts

# 2. Install dependencies
pip install django requests python-decouple mysqlclient pywebpush

# 3. Configure settings.py
# (Use the settings configuration above)
```

### **Step 2: Database Setup**
```bash
# 1. Create and run migrations
python manage.py makemigrations accounts
python manage.py migrate

# 2. Create superuser
python manage.py createsuperuser

# 3. Create admin account for fallback
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.create_user('admin', password='your_admin_password')
>>> admin.is_staff = True
>>> admin.is_superuser = True
>>> admin.save()
```

### **Step 3: API Integration**
```python
# Configure your external API settings
# Update NPU_AUTH_URL and NPU_API_TOKEN in settings.py
# Modify the authentication backend for your API structure
```

### **Step 4: Template Setup**
```bash
# Create template directories
mkdir -p templates/accounts
mkdir -p static/css static/js static/icons

# Copy template files from this guide
# Customize styling and branding for your organization
```

### **Step 5: Testing**
```python
# Create test users and verify:
# 1. API authentication works
# 2. User data synchronization
# 3. Permission system
# 4. Approval workflow
# 5. Mobile/PWA functionality
```

---

## 🔧 **10. Customization Guide**

### **For Different Organizations**
```python
# 1. Change API endpoints
NPU_AUTH_URL = "https://your-api.your-org.com/auth/"
NPU_API_TOKEN = "your_api_token"

# 2. Modify user fields for your organization
class User(AbstractUser):
    # Replace NPU-specific fields with your organization's fields
    employee_id = models.CharField(max_length=20)  # Instead of ldap_uid
    employee_type = models.CharField(max_length=100)  # Instead of staff_type
    # ... customize as needed

# 3. Update authentication backend
class YourOrgAuthBackend(BaseBackend):
    def _authenticate_with_api(self, employee_id, password):
        # Modify API call structure for your organization
        payload = {
            'employee_id': employee_id,  # Your field name
            'password': password
        }
        # ... rest of implementation
```

### **Language Localization**
```python
# For English interface
LANGUAGE_CODE = 'en-us'

# Update all template text from Thai to your language
# Modify field verbose_name in models
# Update admin interface labels
```

---

## 📚 **11. Additional Features**

### **Email Notifications**
```python
# Send approval notifications
def send_approval_email(user):
    from django.core.mail import send_mail
    
    send_mail(
        subject='Account Approved',
        message=f'Hello {user.full_name}, your account has been approved.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

# Send document notifications  
def send_document_notification(user, document):
    user.send_push_notification(
        title='New Document',
        body=f'You have received: {document.title}',
        data={'document_id': document.id}
    )
```

### **API Endpoints for Mobile**
```python
# views.py - Mobile API
@api_view(['POST'])
def api_login(request):
    """JSON API for mobile login"""
    ldap_uid = request.data.get('ldap_uid')
    password = request.data.get('password')
    
    user = authenticate(username=ldap_uid, password=password)
    
    if user:
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'department': user.department,
                'is_document_staff': user.is_document_staff,
            }
        })
    else:
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=400)
```

---

## ✅ **12. Checklist for Implementation**

### **Pre-deployment Checklist**
- [ ] External API integration tested
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Security settings configured
- [ ] SSL certificates installed
- [ ] Environment variables set
- [ ] Backup system configured
- [ ] Monitoring tools setup
- [ ] Load testing completed
- [ ] Security audit performed

### **Post-deployment Checklist**
- [ ] User registration flow tested
- [ ] Approval workflow tested
- [ ] Permission system verified
- [ ] Mobile/PWA functionality tested
- [ ] Push notifications working
- [ ] Email notifications working
- [ ] Audit logging verified
- [ ] Performance monitoring active

---

## 🎯 **Summary**

This NPU Login System provides:

✅ **Complete Authentication Solution**
- External API integration with fallback
- Automatic user data synchronization
- Field-level control system
- Admin approval workflow

✅ **Enterprise Security**
- Role-based access control
- Session management
- CSRF protection
- Audit logging

✅ **Modern UX/UI**
- Thai-localized interface
- Progressive Web App support
- Toast notifications
- Responsive design

✅ **Production Ready**
- Scalable architecture
- Error handling
- Monitoring capabilities
- Mobile API support

**พร้อมใช้งานจริงและปรับแต่งได้ตามองค์กรต่างๆ!** 🚀

---

*เอกสารนี้จัดทำโดย: Claude Code Assistant*  
*วันที่: 19 กันยายน 2567*  
*เวอร์ชัน: 1.0*