from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model for NPU Hybrid Authentication
    Supports both MySQL lookup and NPU AD API integration
    """
    
    # === NPU LDAP/AD Fields ===
    # Primary identification
    ldap_uid = models.CharField(
        max_length=13, 
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name="รหัสบัตรประชาชน",
        help_text="เก็บ staffcitizenid จาก NPU API"
    )
    
    # NPU Staff Information
    npu_staff_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="รหัสพนักงาน NPU",
        help_text="เก็บ staffid จาก NPU API"
    )
    
    # Personal Information from NPU
    prefix_name = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="คำนำหน้า",
        help_text="เก็บ prefixfullname จาก NPU API"
    )
    first_name_th = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ชื่อ (ไทย)",
        help_text="เก็บ staffname จาก NPU API"
    )
    last_name_th = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="นามสกุล (ไทย)",
        help_text="เก็บ staffsurname จาก NPU API"
    )
    full_name = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="ชื่อ-สกุล (เต็ม)",
        help_text="เก็บ fullname จาก NPU API"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="วันเกิด",
        help_text="เก็บ staffbirthdate จาก NPU API"
    )
    gender = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="เพศ",
        help_text="เก็บ gendernameth จาก NPU API"
    )
    
    # NPU Organization Fields
    department = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="หน่วยงาน",
        help_text="เก็บ departmentname จาก NPU API"
    )
    position_title = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="ตำแหน่ง",
        help_text="เก็บ posnameth จาก NPU API"
    )
    staff_type = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="ประเภทบุคลากร",
        help_text="เก็บ stftypename จาก NPU API"
    )
    staff_sub_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ประเภทบุคลากรย่อย",
        help_text="เก็บ substftypename จาก NPU API"
    )
    employment_status = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="สถานะการทำงาน",
        help_text="เก็บ stfstaname จาก NPU API"
    )
    
    # NPU API Metadata
    last_npu_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="ล่าสุดที่ sync จาก NPU"
    )
    npu_last_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="login ล่าสุดจาก NPU API"
    )

    # === USER SOURCE & MANUAL CREATION ===
    USER_SOURCE_CHOICES = [
        ('npu_api', 'NPU API'),
        ('manual', 'Manual Creation'),
    ]

    source = models.CharField(
        max_length=20,
        choices=USER_SOURCE_CHOICES,
        default='npu_api',
        verbose_name="แหล่งที่มาของผู้ใช้",
        help_text="ระบุว่าผู้ใช้ถูกสร้างจาก NPU API หรือสร้างแบบ Manual โดย Admin"
    )

    created_by_user = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name="สร้างโดยผู้ใช้",
        help_text="ผู้ใช้ที่สร้าง user นี้ (สำหรับ manual creation เท่านั้น)"
    )

    # === USER TYPE & STUDENT FIELDS ===
    USER_TYPE_CHOICES = [
        ('staff', 'เจ้าหน้าที่'),
        ('student', 'นักศึกษา'),
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='staff',
        verbose_name="ประเภทผู้ใช้",
        help_text="ประเภทผู้ใช้ระบบ (เจ้าหน้าที่ หรือ นักศึกษา)"
    )

    # Student Information (nullable - ใช้เฉพาะนักศึกษา)
    student_code = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        verbose_name="รหัสนักศึกษา",
        help_text="เก็บ student_code จาก NPU Student API"
    )
    student_level = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ระดับการศึกษา",
        help_text="เช่น ปริญญาตรี, ปริญญาโท"
    )
    student_program = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="สาขาวิชา",
        help_text="เก็บ program_name จาก NPU Student API"
    )
    student_faculty = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="คณะ",
        help_text="เก็บ faculty_name จาก NPU Student API"
    )
    student_degree = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ระดับปริญญา",
        help_text="เก็บ degree_name จาก NPU Student API"
    )

    # Internal Management Fields  
    # department_internal = models.ForeignKey(
    #     'Department', 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     blank=True, 
    #     verbose_name="แผนกภายใน"
    # )
    department_internal_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="แผนกภายใน"
    )
    job_description = models.TextField(
        blank=True, 
        verbose_name="หน้าที่รับผิดชอบ"
    )
    contact_email = models.EmailField(
        blank=True, 
        verbose_name="อีเมลติดต่อ"
    )
    line_user_id = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="LINE User ID"
    )
    
    # DEPRECATED: Legacy permissions - ใช้ Role system แทน
    is_document_staff = models.BooleanField(
        default=False, 
        verbose_name="[DEPRECATED] เจ้าหน้าที่ออกใบสำคัญรับเงิน"
    )
    can_forward_documents = models.BooleanField(
        default=False, 
        verbose_name="[DEPRECATED] สามารถอนุมัติใบสำคัญรับเงิน"
    )
    
    # User Status
    approved_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="วันที่อนุมัติ"
    )
    
    # PWA/Push Notification Fields
    push_subscription_endpoint = models.URLField(
        blank=True, 
        verbose_name="Push Endpoint"
    )
    push_subscription_keys = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name="Push Keys"
    )
    notifications_enabled = models.BooleanField(
        default=True, 
        verbose_name="เปิดการแจ้งเตือน"
    )

    # === Authentication Status ===
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'รอการอนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ปฏิเสธ'),
        ('suspended', 'ระงับการใช้งาน'),
    ]
    
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        verbose_name="สถานะการอนุมัติ"
    )
    
    @property
    def is_pending_approval(self):
        """Check if user is pending admin approval"""
        return self.approval_status == 'pending'
    
    @property
    def is_approved(self):
        """Check if user is approved"""
        return self.approval_status == 'approved'

    @property
    def is_suspended(self):
        """Check if user is suspended"""
        return self.approval_status == 'suspended'
    
    @property
    def is_rejected(self):
        """Check if user is rejected"""
        return self.approval_status == 'rejected'

    def approve_user(self):
        """Approve user account"""
        self.approval_status = 'approved'
        self.approved_at = timezone.now()
        self.is_active = True
        self.save()
        
    def reject_user(self, reason=None):
        """Reject user account"""
        self.approval_status = 'rejected'
        self.is_active = False
        self.save()
        
    def suspend_user(self, reason=None):
        """Suspend user account"""
        self.approval_status = 'suspended'
        self.is_active = False
        self.save()
        
    def get_display_name(self):
        """Get the best display name available"""
        if self.full_name:
            return self.full_name
        elif self.first_name_th and self.last_name_th:
            prefix = f"{self.prefix_name} " if self.prefix_name else ""
            return f"{prefix}{self.first_name_th} {self.last_name_th}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username

    def get_department(self):
        """
        Get appropriate department/faculty based on user type

        Returns:
            str: department for staff, student_faculty for student
        """
        if self.user_type == 'student':
            return self.student_faculty or 'ไม่ระบุคณะ'
        else:
            return self.department or 'ไม่ระบุหน่วยงาน'

    def get_roles(self):
        """ได้บทบาททั้งหมดของผู้ใช้"""
        return Role.objects.filter(
            userrole__user=self,
            userrole__is_active=True,
            is_active=True
        )
    
    def has_role(self, role_name):
        """ตรวจสอบว่ามีบทบาทนี้หรือไม่"""
        return self.get_roles().filter(name=role_name).exists()
    
    def has_permission(self, permission_name):
        """ตรวจสอบว่ามีสิทธิ์นี้หรือไม่"""
        # Check if superuser or staff
        if self.is_superuser or self.is_staff:
            return True
            
        # Check role permissions
        user_roles = self.get_roles()
        for role in user_roles:
            if role.has_permission(permission_name):
                return True
        return False
    
    def assign_role(self, role, assigned_by=None):
        """กำหนดบทบาทให้ผู้ใช้"""
        user_role, created = UserRole.objects.get_or_create(
            user=self,
            role=role,
            defaults={
                'assigned_by': assigned_by,
                'is_active': True
            }
        )
        if not created and not user_role.is_active:
            user_role.is_active = True
            user_role.assigned_by = assigned_by
            user_role.save()
        return user_role
    
    def remove_role(self, role):
        """ลบบทบาทของผู้ใช้"""
        UserRole.objects.filter(user=self, role=role).update(is_active=False)

    def __str__(self):
        if self.user_type == 'student':
            return f"{self.full_name or self.username} ({self.student_code or self.username})"
        else:
            return f"{self.full_name or self.username} ({self.ldap_uid or self.username})"

    class Meta:
        verbose_name = "ผู้ใช้"
        verbose_name_plural = "ผู้ใช้"


class Department(models.Model):
    """Department abbreviations for NPU departments from AD"""
    name = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="ชื่อหน่วยงาน (จาก NPU AD)"
    )
    code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="ชื่อย่อหน่วยงาน",
        help_text="ชื่อย่อที่จะใช้ในใบสำคัญรับเงิน"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="เปิดใช้งาน",
        help_text="หน่วยงานที่ปิดจะไม่สามารถออกใบสำคัญได้"
    )
    
    # ข้อมูลที่อยู่หน่วยงาน (สำหรับใบสำคัญรับเงิน)
    address = models.TextField(
        blank=True, 
        verbose_name="ที่อยู่หน่วยงาน",
        help_text="ที่อยู่หน่วยงานแบบครบถ้วน"
    )
    postal_code = models.CharField(
        max_length=10, 
        blank=True, 
        verbose_name="รหัสไปรษณีย์"
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="เบอร์โทรศัพท์"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_user_count(self):
        """นับจำนวนผู้ใช้ในหน่วยงานนี้"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(department=self.name).count()
    
    def get_full_address(self):
        """รวมที่อยู่เป็นข้อความเดียว"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.postal_code:
            address_parts.append(self.postal_code)
        return " ".join(address_parts) if address_parts else ""
    
    def has_complete_address(self):
        """ตรวจสอบว่ามีที่อยู่ครบถ้วนหรือไม่"""
        return bool(self.address.strip())

    class Meta:
        verbose_name = "ชื่อย่อหน่วยงาน"
        verbose_name_plural = "ชื่อย่อหน่วยงาน"
        ordering = ['name']


class FieldLock(models.Model):
    """Control which fields sync from NPU API vs local management for Receipt System"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='field_locks'
    )
    locked_fields = models.JSONField(
        default=list, 
        verbose_name="ฟิลด์ที่ล็อค"
    )

    def __str__(self):
        return f"Field locks for {self.user}"

    class Meta:
        verbose_name = "การล็อคฟิลด์"
        verbose_name_plural = "การล็อคฟิลด์"


class NPUApiLog(models.Model):
    """Log NPU API calls for debugging and monitoring"""
    
    ACTION_CHOICES = [
        ('auth', 'Authentication'),
        ('sync', 'Data Synchronization'),
        ('lookup', 'User Lookup'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'สำเร็จ'),
        ('failed', 'ล้มเหลว'),
        ('error', 'ข้อผิดพลาด'),
    ]
    
    user_ldap_uid = models.CharField(
        max_length=13,
        verbose_name="รหัสบัตรประชาชน"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="การดำเนินการ"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="สถานะ"
    )
    request_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="ข้อมูลที่ส่งไป"
    )
    response_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="ข้อมูลที่ได้รับ"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="ข้อความข้อผิดพลาด"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="เวลาที่เรียก API"
    )
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="เวลาตอบสนอง (มิลลิวินาที)"
    )
    
    def __str__(self):
        return f"{self.user_ldap_uid} - {self.action} - {self.status} ({self.created_at})"
    
    class Meta:
        verbose_name = "บันทึกการเรียก NPU API"
        verbose_name_plural = "บันทึกการเรียก NPU API"
        ordering = ['-created_at']


class Permission(models.Model):
    """ระบบสิทธิ์การใช้งาน"""
    
    PERMISSION_TYPES = [
        # สิทธิ์พื้นฐาน
        ('receipt_create', 'สร้างใบสำคัญรับเงิน'),
        ('receipt_view_own', 'ดูใบสำคัญของตัวเอง'),
        
        # สิทธิ์การขอแก้ไขใบสำคัญ (สำหรับ Basic User)
        ('receipt_edit_request', 'ส่งคำร้องขอแก้ไขใบสำคัญรับเงิน'),
        ('receipt_edit_request_view', 'ดูคำร้องขอแก้ไขของตัวเอง'),
        ('receipt_edit_withdraw', 'ถอนคำร้องขอแก้ไข'),
        
        # สิทธิ์ระดับหน่วยงาน
        ('receipt_edit_approve', 'อนุมัติการแก้ไขใบสำคัญรับเงิน'),
        ('receipt_edit_approve_manager', 'อนุมัติการแก้ไขจาก Department Manager'),
        ('receipt_cancel_department', 'ยกเลิกใบสำคัญของหน่วยงานตัวเอง'),
        ('receipt_view_department', 'ดูใบสำคัญของหน่วยงานตัวเอง'),
        
        # สิทธิ์ระบบ
        ('receipt_view_all', 'ดูใบสำคัญรับเงินทั้งหมด'),
        ('receipt_export', 'ส่งออกข้อมูลใบสำคัญ'),
        ('user_manage', 'จัดการผู้ใช้งาน'),
        ('role_manage', 'จัดการบทบาทและสิทธิ์'),
        ('report_view', 'ดูรายงาน'),
        ('system_config', 'ตั้งค่าระบบ'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=PERMISSION_TYPES,
        unique=True,
        verbose_name="ชื่อสิทธิ์"
    )
    description = models.TextField(
        blank=True,
        verbose_name="คำอธิบาย"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ใช้งาน"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        verbose_name = "สิทธิ์การใช้งาน"
        verbose_name_plural = "สิทธิ์การใช้งาน"


class Role(models.Model):
    """บทบาทผู้ใช้งาน"""
    
    ROLE_TYPES = [
        ('admin', 'ผู้ดูแลระบบ'),
        ('manager', 'ผู้จัดการ'),
        ('staff', 'เจ้าหน้าที่'),
        ('approver', 'ผู้อนุมัติ'),
        ('viewer', 'ผู้ดู'),
    ]
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ชื่อบทบาท"
    )
    display_name = models.CharField(
        max_length=100,
        verbose_name="ชื่อแสดง"
    )
    description = models.TextField(
        blank=True,
        verbose_name="คำอธิบาย"
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="สิทธิ์"
    )
    department_scope = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ขอบเขตหน่วยงาน",
        help_text="หน่วยงานที่สามารถจัดการได้ (เว้นว่างหมายถึงทุกหน่วยงาน)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ใช้งาน"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name
    
    def has_permission(self, permission_name):
        """ตรวจสอบว่ามีสิทธิ์นี้หรือไม่"""
        return self.permissions.filter(name=permission_name, is_active=True).exists()
    
    class Meta:
        verbose_name = "บทบาท"
        verbose_name_plural = "บทบาท"


class UserRole(models.Model):
    """การกำหนดบทบาทให้ผู้ใช้"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="ผู้ใช้"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="บทบาท"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name="ผู้กำหนด"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่กำหนด"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="ใช้งาน"
    )
    
    def __str__(self):
        return f"{self.user} - {self.role}"
    
    class Meta:
        verbose_name = "บทบาทผู้ใช้"
        verbose_name_plural = "บทบาทผู้ใช้"
        unique_together = ['user', 'role']


class DocumentVolume(models.Model):
    """
    เล่มเอกสารสำหรับใบสำคัญรับเงิน
    จัดการตามปีงบประมาณไทย (1 ต.ค. - 30 ก.ย.)
    """
    
    STATUS_CHOICES = [
        ('active', 'ใช้งานอยู่'),
        ('closed', 'ปิดเล่มแล้ว'),
        ('archived', 'เก็บเป็นเอกสารประวัติ'),
    ]
    
    # Basic Information
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="หน่วยงาน"
    )
    fiscal_year = models.IntegerField(
        verbose_name="ปีงบประมาณ (พ.ศ.)",
        help_text="ปีงบประมาณไทย เช่น 2568"
    )
    volume_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="รหัสเล่ม",
        help_text="รหัสเล่ม เช่น REG68, FIN68"
    )
    
    # Status and Control
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="สถานะ"
    )
    is_auto_generated = models.BooleanField(
        default=True,
        verbose_name="สร้างอัตโนมัติ",
        help_text="สร้างโดยระบบอัตโนมัติตามปีงบประมาณ"
    )
    
    # Document Numbering
    last_document_number = models.IntegerField(
        default=0,
        verbose_name="เลขที่เอกสารล่าสุด",
        help_text="เลขที่เอกสารล่าสุดที่ออกในเล่มนี้"
    )
    max_documents = models.IntegerField(
        default=9999,
        verbose_name="จำนวนเอกสารสูงสุด",
        help_text="จำนวนเอกสารสูงสุดที่สามารถออกในเล่มนี้ได้"
    )
    
    # Fiscal Year Dates
    fiscal_year_start = models.DateField(
        verbose_name="วันเริ่มต้นปีงบประมาณ"
    )
    fiscal_year_end = models.DateField(
        verbose_name="วันสิ้นสุดปีงบประมาณ"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่สร้าง"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="วันที่แก้ไข"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="วันที่ปิดเล่ม"
    )
    
    # Management
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_volumes',
        verbose_name="ผู้สร้าง"
    )
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_volumes',
        verbose_name="ผู้ปิดเล่ม"
    )
    
    def __str__(self):
        return f"{self.volume_code} ({self.department.name} - ปีงบ {self.fiscal_year})"
    
    def get_next_document_number(self):
        """ได้เลขที่เอกสารลำดับถัดไป"""
        if self.status != 'active':
            raise ValueError(f"เล่ม {self.volume_code} ไม่ได้อยู่ในสถานะใช้งาน")
        
        if self.last_document_number >= self.max_documents:
            raise ValueError(f"เล่ม {self.volume_code} เต็มแล้ว (สูงสุด {self.max_documents} เอกสาร)")
        
        return self.last_document_number + 1
    
    def increment_document_number(self):
        """เพิ่มเลขที่เอกสารและบันทึก"""
        next_number = self.get_next_document_number()
        self.last_document_number = next_number
        self.save(update_fields=['last_document_number', 'updated_at'])
        return next_number
    
    def get_document_code(self, document_number=None):
        """
        สร้างรหัสเอกสารเต็ม เช่น REG68-0001
        
        Args:
            document_number (int, optional): เลขที่เอกสาร ถ้าไม่ระบุจะใช้เลขถัดไป
        """
        if document_number is None:
            document_number = self.get_next_document_number()
        
        return f"{self.volume_code}-{document_number:04d}"
    
    def get_usage_percentage(self):
        """คำนวณเปอร์เซ็นต์การใช้งาน"""
        if self.max_documents == 0:
            return 0
        return (self.last_document_number / self.max_documents) * 100
    
    def is_nearly_full(self, threshold=90):
        """ตรวจสอบว่าเล่มใกล้เต็มหรือไม่"""
        return self.get_usage_percentage() >= threshold
    
    def close_volume(self, user=None):
        """ปิดเล่ม"""
        if self.status == 'closed':
            raise ValueError(f"เล่ม {self.volume_code} ถูกปิดแล้ว")
        
        from django.utils import timezone
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.closed_by = user
        self.save()
    
    @classmethod
    def get_or_create_volume_for_department(cls, department, fiscal_year=None, user=None):
        """
        หาหรือสร้างเล่มสำหรับหน่วยงานในปีงบประมาณที่กำหนด
        
        Args:
            department (Department): หน่วยงาน
            fiscal_year (int, optional): ปีงบประมาณ พ.ศ. ถ้าไม่ระบุจะใช้ปีปัจจุบัน
            user (User, optional): ผู้สร้าง
            
        Returns:
            DocumentVolume: เล่มเอกสาร
        """
        if fiscal_year is None:
            from utils.fiscal_year import get_current_fiscal_year
            fiscal_year = get_current_fiscal_year()
        
        from utils.fiscal_year import get_volume_code, get_fiscal_year_dates
        
        volume_code = get_volume_code(department.code, fiscal_year)
        fiscal_start, fiscal_end = get_fiscal_year_dates(fiscal_year)
        
        volume, created = cls.objects.get_or_create(
            department=department,
            fiscal_year=fiscal_year,
            defaults={
                'volume_code': volume_code,
                'fiscal_year_start': fiscal_start,
                'fiscal_year_end': fiscal_end,
                'created_by': user,
                'status': 'active'
            }
        )
        
        return volume, created
    
    class Meta:
        verbose_name = "เล่มเอกสาร"
        verbose_name_plural = "เล่มเอกสาร"
        ordering = ['-fiscal_year', 'department__name']
        unique_together = ['department', 'fiscal_year']
        indexes = [
            models.Index(fields=['fiscal_year', 'status']),
            models.Index(fields=['department', 'fiscal_year']),
            models.Index(fields=['volume_code']),
        ]


class DocumentVolumeLog(models.Model):
    """
    บันทึกการเปลี่ยนแปลงเล่มเอกสาร
    เพื่อติดตามประวัติการใช้งาน
    """
    
    ACTION_CHOICES = [
        ('created', 'สร้างเล่มใหม่'),
        ('document_issued', 'ออกเอกสาร'),
        ('closed', 'ปิดเล่ม'),
        ('archived', 'เก็บเป็นเอกสารประวัติ'),
        ('reopened', 'เปิดเล่มใหม่'),
    ]
    
    volume = models.ForeignKey(
        DocumentVolume,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name="เล่มเอกสาร"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="การดำเนินการ"
    )
    document_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="เลขที่เอกสาร",
        help_text="เฉพาะกรณีออกเอกสาร"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ผู้ดำเนินการ"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="หมายเหตุ"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่ดำเนินการ"
    )
    
    def __str__(self):
        return f"{self.volume.volume_code} - {self.get_action_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
    
    class Meta:
        verbose_name = "บันทึกเล่มเอกสาร"
        verbose_name_plural = "บันทึกเล่มเอกสาร"
        ordering = ['-created_at']


# ===== RECEIPT SYSTEM MODELS =====

class ReceiptTemplate(models.Model):
    """
    รายการสำเร็จรูปสำหรับใบสำคัญรับเงิน
    เช่น ค่าอาหารว่าง, ค่าประกันของเสียหาย

    รองรับ 3 รูปแบบการกรอก:
    1. simple: กรอกเฉพาะจำนวนเงิน (เช่น ค่าประกันของเสียหาย max 1000 บาท)
    2. textarea: กรอกรายละเอียด + จำนวนเงิน (เช่น รับเงินอื่นๆ)
    3. food_calculation: กรอกหลายรายการย่อย พร้อมการคำนวณ (เช่น ค่าอาหาร)
    """

    INPUT_TYPE_CHOICES = [
        ('simple', 'ช่องเดียว - จำนวนเงิน'),
        ('textarea', 'ช่องเดียว - รายละเอียด + เงิน'),
        ('food_calculation', 'หลายรายการย่อย - คำนวณอัตโนมัติ'),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name="ชื่อรายการ",
        help_text="เช่น ค่าอาหารว่างและเครื่องดื่ม"
    )

    # ฟิลด์ใหม่: กำหนดรูปแบบการกรอก
    input_type = models.CharField(
        max_length=20,
        choices=INPUT_TYPE_CHOICES,
        default='simple',
        verbose_name="รูปแบบการกรอกข้อมูล"
    )

    # ฟิลด์ใหม่: ข้อมูลรายการย่อย (สำหรับ food_calculation)
    sub_items = models.JSONField(
        null=True,
        blank=True,
        verbose_name="รายการย่อย (JSON)",
        help_text='ตัวอย่าง: {"items": [{"name": "ค่าอาหารเช้า", "fields": [...]}]}'
    )

    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="จำนวนเงินสูงสุด",
        help_text="เช่น 2000 บาท สำหรับค่าอาหาร หรือ 1000 บาท สำหรับค่าประกัน"
    )
    fixed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="จำนวนเงินคงที่",
        help_text="เช่น 1000 บาท (ถ้าไม่คงที่ให้เว้นว่าง)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="เปิดใช้งาน"
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="หมวดหมู่",
        help_text="เช่น ค่าอาหาร, ค่าประกัน"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.fixed_amount:
            return f"{self.name} ({self.fixed_amount} บาท)"
        elif self.max_amount:
            return f"{self.name} (สูงสุด {self.max_amount} บาท)"
        else:
            return self.name
    
    class Meta:
        verbose_name = "รายการสำเร็จรูป"
        verbose_name_plural = "รายการสำเร็จรูป"
        ordering = ['category', 'name']


class Receipt(models.Model):
    """
    ใบสำคัญรับเงิน
    """
    
    STATUS_CHOICES = [
        ('draft', 'ร่าง'),
        ('completed', 'เสร็จสิ้น'),
        ('cancelled', 'ยกเลิก'),
    ]
    
    # เลขที่เอกสาร (ddmmyy/xxxx)
    receipt_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="เลขที่ใบสำคัญรับเงิน",
        help_text="รูปแบบ: ddmmyy/xxxx เช่น 240968/0001 (ร่างยังไม่มีเลข จะได้เลขเมื่อเปลี่ยนเป็นเสร็จสิ้น)"
    )
    
    # ข้อมูลหน่วยงานและผู้สร้าง
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="หน่วยงาน"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="ผู้สร้าง"
    )
    
    # ข้อมูลผู้รับเงิน (ข้าพเจ้า)
    recipient_name = models.CharField(
        max_length=255,
        verbose_name="ชื่อผู้รับเงิน",
        help_text="ข้าพเจ้า ..."
    )
    recipient_address = models.TextField(
        verbose_name="ที่อยู่ผู้รับเงิน",
        help_text="บ้านเลขที่ หมู่ ซอย ถนน ตำบล อำเภอ จังหวัด"
    )
    recipient_postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="รหัสไปรษณีย์ผู้รับเงิน"
    )
    recipient_id_card = models.CharField(
        max_length=20,
        verbose_name="เลขบัตรประชาชนผู้รับเงิน"
    )
    
    # ประเภทการจ่าย
    is_loan = models.BooleanField(
        default=False,
        verbose_name="เป็นการยืมเงิน",
        help_text="ถ้าเลือก จะใช้ชื่อผู้สร้างเป็นผู้จ่าย"
    )
    
    # จำนวนเงิน
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="จำนวนเงินรวม"
    )
    total_amount_text = models.CharField(
        max_length=500,
        verbose_name="จำนวนเงินตัวหนังสือ",
        help_text="เช่น หนึ่งหมื่นบาทถ้วน"
    )
    
    # สถานะ
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="สถานะ"
    )
    
    # วันที่
    receipt_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="วันที่ในใบสำคัญรับเงิน"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # QR Code Verification
    verification_hash = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        verbose_name="รหัสตรวจสอบ",
        help_text="SHA-256 hash สำหรับตรวจสอบความถูกต้อง (ร่างยังไม่มี hash)"
    )
    qr_code_data = models.TextField(
        null=True,
        blank=True,
        verbose_name="ข้อมูล QR Code",
        help_text="ข้อมูลที่จะแสดงใน QR Code (ร่างยังไม่มี QR)"
    )
    
    def __str__(self):
        return f"{self.receipt_number} - {self.recipient_name} ({self.total_amount} บาท)"
    
    @property
    def volume_code(self):
        """รหัสเล่มเอกสาร เช่น MIT68"""
        from utils.fiscal_year import get_volume_code, get_fiscal_year_from_date
        from datetime import datetime

        # ถ้าไม่มี receipt_date (draft) ให้ใช้วันที่ปัจจุบัน
        target_date = self.receipt_date or datetime.now().date()
        fiscal_year = get_fiscal_year_from_date(target_date)
        return get_volume_code(self.department.code, fiscal_year)
    
    def save(self, *args, **kwargs):
        # Track if this is a new completion (status changing to completed)
        is_new_completion = False
        if self.pk:
            try:
                old_receipt = Receipt.objects.get(pk=self.pk)
                is_new_completion = (old_receipt.status != 'completed' and self.status == 'completed')
            except Receipt.DoesNotExist:
                pass
        else:
            # New receipt being saved as completed
            is_new_completion = (self.status == 'completed')

        # Auto-create DocumentVolume for this department if not exists
        # This ensures every department gets a volume automatically when completing first receipt
        if self.status == 'completed':
            from utils.fiscal_year import get_fiscal_year_from_date
            from datetime import datetime

            receipt_date = self.receipt_date or datetime.now().date()
            fiscal_year = get_fiscal_year_from_date(receipt_date)

            # Create volume if it doesn't exist
            volume, created = DocumentVolume.get_or_create_volume_for_department(
                department=self.department,
                fiscal_year=fiscal_year,
                user=self.created_by
            )

            if created:
                # Log that a new volume was auto-created
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Auto-created DocumentVolume: {volume.volume_code} for {self.department.name}")

        # Auto-generate receipt number ONLY when status is 'completed' and no number yet
        # Draft receipts don't get a number to avoid gaps in numbering
        if self.status == 'completed' and not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()

        # Auto-generate total_amount_text if not set
        if not self.total_amount_text and self.total_amount:
            self.total_amount_text = self.convert_amount_to_thai_text(self.total_amount)

        # Auto-generate verification hash if not set (only for completed)
        if self.status == 'completed' and not self.verification_hash:
            self.verification_hash = self.generate_verification_hash()

        # Auto-generate QR code data if not set (only for completed)
        if self.status == 'completed' and not self.qr_code_data:
            self.qr_code_data = self.generate_qr_code_data()

        super().save(*args, **kwargs)

        # Update DocumentVolume.last_document_number after saving receipt
        # This keeps track of how many receipts have been issued from this volume
        if is_new_completion and self.status == 'completed':
            from utils.fiscal_year import get_fiscal_year_from_date
            from datetime import datetime

            receipt_date = self.receipt_date or datetime.now().date()
            fiscal_year = get_fiscal_year_from_date(receipt_date)

            # Get the volume for this department and fiscal year
            try:
                volume = DocumentVolume.objects.get(
                    department=self.department,
                    fiscal_year=fiscal_year
                )

                # Count total completed receipts for this volume
                total_receipts = Receipt.objects.filter(
                    department=self.department,
                    status='completed',
                    receipt_date__gte=volume.fiscal_year_start,
                    receipt_date__lte=volume.fiscal_year_end
                ).count()

                # Update volume's last_document_number
                volume.last_document_number = total_receipts
                volume.save(update_fields=['last_document_number'])

            except DocumentVolume.DoesNotExist:
                pass  # Volume doesn't exist (shouldn't happen, but handle gracefully)
    
    def generate_receipt_number(self):
        """สร้างเลขที่ใบสำคัญรับเงินแบบ ddmmyy/xxxx"""
        from datetime import datetime
        from django.db.models import Max
        from django.db import transaction

        today = self.receipt_date or datetime.now().date()

        # Format: ddmmyy
        date_part = today.strftime("%d%m%y")

        # หาเลข running number สำหรับวันนี้และหน่วยงานนี้
        prefix = f"{date_part}/"

        # ใช้ transaction เพื่อป้องกัน race condition
        with transaction.atomic():
            # Lock rows เพื่อป้องกันการอ่านพร้อมกัน
            last_receipt = Receipt.objects.filter(
                receipt_number__startswith=prefix,
                department=self.department
            ).select_for_update().aggregate(
                max_number=Max('receipt_number')
            )['max_number']

            if last_receipt:
                # ดึงตัวเลขท้ายสุด
                last_number = int(last_receipt.split('/')[-1])
                next_number = last_number + 1
            else:
                next_number = 1

        # Format: ddmmyy/xxxx
        return f"{date_part}/{next_number:04d}"
    
    @staticmethod
    def convert_amount_to_thai_text(amount):
        """แปลงจำนวนเงินเป็นตัวหนังสือไทย"""
        if amount == 0:
            return 'ศูนย์บาทถ้วน'
        
        def number_to_thai(num):
            if num == 0:
                return ''
            
            ones = ['', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า']
            
            def convert_group(n):
                if n == 0:
                    return ''
                elif n < 10:
                    return ones[n]
                elif n < 20:
                    if n == 10:
                        return 'สิบ'
                    else:
                        return 'สิบ' + ones[n - 10]
                elif n < 100:
                    tens = n // 10
                    units = n % 10
                    if tens == 2:
                        return 'ยี่สิบ' + ones[units]
                    else:
                        return ones[tens] + 'สิบ' + ones[units]
                else:
                    hundreds = n // 100
                    remainder = n % 100
                    return ones[hundreds] + 'ร้อย' + convert_group(remainder)
            
            def convert_full_number(num):
                if num == 0:
                    return ''
                
                result = ''
                
                # ล้าน
                if num >= 1000000:
                    millions = num // 1000000
                    result += convert_group(millions) + 'ล้าน'
                    num %= 1000000
                
                # แสน
                if num >= 100000:
                    hundred_thousands = num // 100000
                    result += convert_group(hundred_thousands) + 'แสน'
                    num %= 100000
                
                # หมื่น
                if num >= 10000:
                    ten_thousands = num // 10000
                    result += convert_group(ten_thousands) + 'หมื่น'
                    num %= 10000
                
                # พัน
                if num >= 1000:
                    thousands = num // 1000
                    if thousands == 1:
                        result += 'หนึ่งพัน'
                    else:
                        result += convert_group(thousands) + 'พัน'
                    num %= 1000
                
                # ร้อย สิบ หน่วย
                if num > 0:
                    result += convert_group(num)
                
                return result
            
            return convert_full_number(int(num))
        
        # แยกส่วนจำนวนเต็มและทศนิยม
        integer_part = int(amount)
        decimal_part = round((amount - integer_part) * 100)
        
        result = number_to_thai(integer_part) + 'บาท'
        
        if decimal_part > 0:
            result += number_to_thai(decimal_part) + 'สตางค์'
        else:
            result += 'ถ้วน'
        
        return result
    
    def generate_verification_hash(self):
        """สร้าง hash สำหรับตรวจสอบความถูกต้อง"""
        import hashlib
        import json
        from django.conf import settings
        
        # ข้อมูลหลักที่ใช้สร้าง hash
        data_dict = {
            'receipt_number': self.receipt_number,
            'department_code': self.department.code if self.department else '',
            'recipient_name': self.recipient_name,
            'total_amount': str(self.total_amount),
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else '',
            'created_by': self.created_by.username if self.created_by else ''
        }
        
        # เพิ่ม secret key เพื่อความปลอดภัย
        data_dict['secret'] = getattr(settings, 'SECRET_KEY', 'default-secret')
        
        # สร้าง hash
        data_string = json.dumps(data_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    
    def generate_qr_code_data(self):
        """สร้างข้อมูลสำหรับ QR Code แบบง่าย"""
        from django.conf import settings

        # ถ้าไม่มีเลขที่ (draft) ไม่สามารถสร้าง QR ได้
        if not self.receipt_number:
            return None

        # ใช้เลขที่เอกสารเป็น URL หลัก (แบบง่าย)
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8002')

        # URL ใหม่: รวมรหัสหน่วยงาน เพื่อไม่ให้ซ้ำกัน
        # รูปแบบ: /check/{dept_code}/{date_part}/{number_part}/
        dept_code = self.department.code if self.department else 'UNKNOWN'
        receipt_path = self.receipt_number.replace('/', '/')  # 091025/0003
        verification_url = f"{base_url}/check/{dept_code}/{receipt_path}"

        # QR Code เก็บเฉพาะ URL เท่านั้น (ง่ายที่สุด)
        return verification_url
    
    def verify_integrity(self):
        """ตรวจสอบความถูกต้องของใบสำคัญ"""
        expected_hash = self.generate_verification_hash()
        return self.verification_hash == expected_hash
    
    def get_verification_url(self):
        """ได้ URL สำหรับตรวจสอบ (ใช้ระบบใหม่แบบง่าย)"""
        from django.conf import settings

        # ถ้าไม่มีเลขที่ (draft) ไม่มี verification URL
        if not self.receipt_number:
            return None

        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8002')
        dept_code = self.department.code if self.department else 'UNKNOWN'
        return f"{base_url}/check/{dept_code}/{self.receipt_number}"
    
    def can_be_cancelled_by(self, user):
        """ตรวจสอบว่าผู้ใช้สามารถยกเลิกใบสำคัญนี้ได้หรือไม่"""
        # ไม่สามารถยกเลิกได้หากถูกยกเลิกแล้ว
        if self.status == 'cancelled':
            return False

        # ตรวจสอบสิทธิ์
        # System Admin: ยกเลิกได้ทุกใบสำคัญ
        if user.has_permission('receipt_view_all'):
            return True

        # Senior Manager: ยกเลิกได้ในหน่วยงานตัวเอง
        if user.has_permission('receipt_cancel_approve_manager'):
            return user.get_department() == self.department.name

        # Department Manager และ Basic User: ยกเลิกได้เฉพาะของตัวเอง (ต้องขออนุมัติ)
        if self.created_by == user:
            return True

        return False
    
    def can_be_cancelled_directly(self, user):
        """ตรวจสอบว่าสามารถยกเลิกได้เลย (ไม่ต้องขออนุมัติ)"""
        if not self.can_be_cancelled_by(user):
            return False
            
        # ร่าง: ยกเลิกได้เลยทุกคน (เฉพาะเจ้าของ)
        if self.status == 'draft':
            return self.created_by == user
            
        # เสร็จสิ้น: เฉพาะ Senior Manager และ Admin
        if self.status == 'completed':
            return (user.has_permission('receipt_cancel_approve_manager') or 
                   user.has_permission('receipt_view_all'))
                   
        return False
    
    def cancel(self, user, reason="", skip_permission_check=False):
        """ยกเลิกใบสำคัญรับเงิน

        Args:
            user: ผู้ดำเนินการ
            reason: เหตุผล
            skip_permission_check: ข้ามการเช็คสิทธิ์ (ใช้สำหรับการอนุมัติคำขอยกเลิก)
        """
        from django.core.exceptions import PermissionDenied
        from django.utils import timezone

        # ตรวจสอบสิทธิ์ (ยกเว้นกรณีอนุมัติผ่าน cancel request)
        if not skip_permission_check and not self.can_be_cancelled_directly(user):
            raise PermissionDenied("คุณไม่มีสิทธิ์ยกเลิกใบสำคัญนี้")

        # ตรวจสอบสถานะ
        if self.status == 'cancelled':
            raise ValueError("ใบสำคัญนี้ถูกยกเลิกแล้ว")

        # ตรวจสอบว่ามี edit request รออยู่หรือไม่
        if hasattr(self, 'edit_requests'):
            pending_requests = self.edit_requests.filter(status='pending')
            if pending_requests.exists():
                raise ValueError("ไม่สามารถยกเลิกได้ เนื่องจากมีคำขอแก้ไขรออนุมัติอยู่")

        # เปลี่ยนสถานะเป็นยกเลิก
        old_status = self.status
        self.status = 'cancelled'
        self.save()

        # บันทึก log
        ReceiptChangeLog.log_change(
            receipt=self,
            action='cancelled',
            user=user,
            field_name='status',
            old_value=old_status,
            new_value='cancelled',
            notes=reason or 'ยกเลิกใบสำคัญรับเงิน'
        )
    
    class Meta:
        verbose_name = "ใบสำคัญรับเงิน"
        verbose_name_plural = "ใบสำคัญรับเงิน"
        ordering = ['-created_at']
        unique_together = [['receipt_number', 'department']]
        indexes = [
            models.Index(fields=['receipt_number', 'department']),
            models.Index(fields=['status', 'created_at']),
        ]


class ReceiptItem(models.Model):
    """
    รายการในใบสำคัญรับเงิน
    """
    
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="ใบสำคัญรับเงิน"
    )
    template = models.ForeignKey(
        ReceiptTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="รายการสำเร็จรูป",
        help_text="ถ้าเลือกจากรายการสำเร็จรูป"
    )
    description = models.CharField(
        max_length=500,
        verbose_name="รายการ",
        help_text="คำอธิบายรายการ"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="จำนวนเงิน"
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="ลำดับ"
    )
    
    def __str__(self):
        return f"{self.receipt.receipt_number} - {self.description} ({self.amount} บาท)"
    
    class Meta:
        verbose_name = "รายการใบสำคัญรับเงิน"
        verbose_name_plural = "รายการใบสำคัญรับเงิน"
        ordering = ['receipt', 'order']


# ===== RECEIPT EDIT REQUEST SYSTEM MODELS =====

class ReceiptEditRequest(models.Model):
    """
    คำร้องขอแก้ไขใบสำคัญรับเงิน
    สำหรับ Basic User ที่ต้องการแก้ไขใบสำคัญที่สร้างแล้ว
    """
    
    STATUS_CHOICES = [
        ('pending', 'รอการอนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ปฏิเสธ'),
        ('withdrawn', 'ถอนคำร้อง'),
        ('applied', 'ดำเนินการแล้ว'),
    ]
    
    # ข้อมูลพื้นฐาน
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='edit_requests',
        verbose_name="ใบสำคัญรับเงิน"
    )
    request_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="เลขที่คำร้อง",
        help_text="รูปแบบ: ER-yymmdd-xxxx เช่น ER-241001-0001"
    )
    
    # ผู้ขอและผู้อนุมัติ
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='submitted_edit_requests',
        verbose_name="ผู้ส่งคำร้อง"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_edit_requests',
        verbose_name="ผู้อนุมัติ"
    )
    
    # เหตุผลและรายละเอียด
    reason = models.TextField(
        verbose_name="เหตุผลในการขอแก้ไข",
        help_text="อธิบายเหตุผลที่ต้องการแก้ไขใบสำคัญ"
    )
    description = models.TextField(
        blank=True,
        verbose_name="รายละเอียดการแก้ไข",
        help_text="อธิบายสิ่งที่ต้องการแก้ไข"
    )
    
    # สถานะและการอนุมัติ
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="สถานะ"
    )
    approval_notes = models.TextField(
        blank=True,
        verbose_name="หมายเหตุการอนุมัติ",
        help_text="หมายเหตุจากผู้อนุมัติ"
    )
    
    # ข้อมูลใหม่ที่ขอแก้ไข (ข้อมูลหลัก)
    new_recipient_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ชื่อผู้รับเงิน (ใหม่)"
    )
    new_recipient_address = models.TextField(
        blank=True,
        verbose_name="ที่อยู่ผู้รับเงิน (ใหม่)"
    )
    new_recipient_postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="รหัสไปรษณีย์ (ใหม่)"
    )
    new_recipient_id_card = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="เลขบัตรประชาชน (ใหม่)"
    )
    new_receipt_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="วันที่ในใบสำคัญ (ใหม่)"
    )
    new_total_amount_text = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="จำนวนเงินตัวหนังสือ (ใหม่)"
    )
    new_total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="จำนวนเงินรวม (ใหม่)"
    )
    new_items_data = models.TextField(
        blank=True,
        verbose_name="ข้อมูลรายการสินค้าใหม่ (JSON)",
        help_text="เก็บข้อมูลรายการสินค้าในรูปแบบ JSON"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่ส่งคำร้อง"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="วันที่แก้ไขล่าสุด"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="วันที่อนุมัติ"
    )
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="วันที่ดำเนินการ"
    )
    
    def __str__(self):
        return f"{self.request_number} - {self.receipt.receipt_number} ({self.get_status_display()})"
    
    def generate_request_number(self):
        """สร้างเลขที่คำร้อง รูปแบบ ER-yymmdd-xxxx"""
        from django.utils import timezone
        today = timezone.now().date()
        prefix = f"ER-{today.strftime('%y%m%d')}"
        
        # หาลำดับล่าสุดในวันนี้
        last_request = ReceiptEditRequest.objects.filter(
            request_number__startswith=prefix
        ).order_by('-request_number').first()
        
        if last_request:
            last_seq = int(last_request.request_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
            
        return f"{prefix}-{new_seq:04d}"
    
    def save(self, *args, **kwargs):
        # Auto-generate request number if not set
        if not self.request_number:
            self.request_number = self.generate_request_number()
        super().save(*args, **kwargs)
    
    def can_be_approved_by(self, user):
        """ตรวจสอบว่าผู้ใช้สามารถอนุมัติคำร้องนี้ได้หรือไม่"""
        # Admin/Aadmin: ดูได้อย่างเดียว ไม่มีสิทธิ์อนุมัติ (ลบออก)

        # ต้องอยู่แผนกเดียวกันเท่านั้น
        if user.get_department() != self.receipt.department.name:
            return False

        # Senior Manager อนุมัติได้สำหรับ Department Manager ในแผนกเดียวกัน
        if user.has_permission('receipt_edit_approve_manager'):
            # ต้องเป็นคำขอจาก Department Manager เท่านั้น
            requester_has_manager_permission = self.requested_by.has_permission('receipt_edit_approve')
            return requester_has_manager_permission

        # Department Manager อนุมัติได้สำหรับ Basic User ในแผนกเดียวกัน
        if user.has_permission('receipt_edit_approve'):
            # ต้องไม่ใช่คำขอจาก Department Manager (ต้องเป็นคำขอจาก User)
            requester_has_manager_permission = self.requested_by.has_permission('receipt_edit_approve')
            return not requester_has_manager_permission

        return False
    
    def approve(self, approved_by, notes=""):
        """อนุมัติคำร้อง"""
        from django.utils import timezone
        import json
        
        self.status = 'approved'
        self.approved_by = approved_by
        self.approval_notes = notes
        self.approved_at = timezone.now()
        self.save()
        
        # Apply changes to the original receipt
        receipt = self.receipt
        
        # Update basic information if provided
        if self.new_recipient_name:
            receipt.recipient_name = self.new_recipient_name
        if self.new_recipient_address:
            receipt.recipient_address = self.new_recipient_address
        if self.new_recipient_postal_code:
            receipt.recipient_postal_code = self.new_recipient_postal_code
        if self.new_recipient_id_card:
            receipt.recipient_id_card = self.new_recipient_id_card
        if self.new_receipt_date:
            receipt.receipt_date = self.new_receipt_date
        if self.new_total_amount_text:
            receipt.total_amount_text = self.new_total_amount_text
        if self.new_total_amount:
            receipt.total_amount = self.new_total_amount
        
        # Update receipt items if provided
        if self.new_items_data:
            try:
                items_data = json.loads(self.new_items_data)

                # Clear existing items
                receipt.items.all().delete()

                # Create new items
                for order, item_data in enumerate(items_data, 1):
                    quantity = item_data.get('quantity', 1)
                    unit_price = item_data.get('unit_price', 0)
                    amount = quantity * unit_price

                    ReceiptItem.objects.create(
                        receipt=receipt,
                        description=item_data.get('description', ''),
                        amount=amount,
                        order=order
                    )

                # Recalculate total amount
                total = sum(item.amount for item in receipt.items.all())
                receipt.total_amount = total

                # Update total amount text (Thai)
                receipt.total_amount_text = Receipt.convert_amount_to_thai_text(total)

            except json.JSONDecodeError:
                pass
        
        receipt.save()
        
        # Mark as applied
        self.status = 'applied'
        self.applied_at = timezone.now()
        self.save()
    
    def reject(self, rejected_by, notes=""):
        """ปฏิเสธคำร้อง"""
        self.status = 'rejected'
        self.approved_by = rejected_by
        self.approval_notes = notes
        self.save()
    
    def withdraw(self):
        """ถอนคำร้อง (โดยผู้ส่งคำร้อง)"""
        if self.status == 'pending':
            self.status = 'withdrawn'
            self.save()
    
    class Meta:
        verbose_name = "คำร้องขอแก้ไขใบสำคัญรับเงิน"
        verbose_name_plural = "คำร้องขอแก้ไขใบสำคัญรับเงิน"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['receipt', 'status']),
            models.Index(fields=['requested_by', 'status']),
        ]


class ReceiptEditRequestItem(models.Model):
    """
    รายการที่ขอแก้ไขในคำร้องขอแก้ไขใบสำคัญรับเงิน
    สำหรับการแก้ไขรายการแต่ละรายการ
    """
    
    ACTION_CHOICES = [
        ('update', 'แก้ไข'),
        ('add', 'เพิ่ม'),
        ('delete', 'ลบ'),
    ]
    
    edit_request = models.ForeignKey(
        ReceiptEditRequest,
        on_delete=models.CASCADE,
        related_name='item_changes',
        verbose_name="คำร้องขอแก้ไข"
    )
    
    # รายการเดิม (ถ้ามี)
    original_item = models.ForeignKey(
        'ReceiptItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="รายการเดิม"
    )
    
    # การดำเนินการ
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name="การดำเนินการ"
    )
    
    # ข้อมูลใหม่ที่ขอ
    new_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="รายการ (ใหม่)"
    )
    new_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="จำนวนเงิน (ใหม่)"
    )
    new_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ลำดับ (ใหม่)"
    )
    
    def __str__(self):
        return f"{self.edit_request.request_number} - {self.get_action_display()}: {self.new_description or self.original_item.description}"
    
    class Meta:
        verbose_name = "รายการขอแก้ไข"
        verbose_name_plural = "รายการขอแก้ไข"
        ordering = ['edit_request', 'new_order', 'id']


class ReceiptCancelRequest(models.Model):
    """
    คำขอยกเลิกใบสำคัญรับเงิน
    สำหรับกรณีที่ผู้ใช้ไม่สามารถยกเลิกได้เลย ต้องขออนุมัติ
    """
    
    STATUS_CHOICES = [
        ('pending', 'รอการอนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ปฏิเสธ'),
        ('withdrawn', 'ถอนคำร้อง'),
        ('applied', 'ดำเนินการแล้ว'),
    ]
    
    # ใบสำคัญที่ขอยกเลิก
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='cancel_requests',
        verbose_name="ใบสำคัญรับเงิน"
    )
    
    # เลขที่คำขอยกเลิก (CR-yymmdd-xxxx)
    request_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="เลขที่คำขอยกเลิก",
        help_text="รูปแบบ: CR-yymmdd-xxxx"
    )
    
    # ผู้ร้องขอและผู้อนุมัติ
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='requested_cancel_requests',
        verbose_name="ผู้ส่งคำขอ"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_cancel_requests', 
        verbose_name="ผู้พิจารณา"
    )
    
    # เหตุผลในการยกเลิก
    cancel_reason = models.TextField(
        verbose_name="เหตุผลการยกเลิก",
        help_text="ระบุเหตุผลที่ต้องการยกเลิกใบสำคัญ"
    )
    
    # สถานะคำขอ
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="สถานะคำขอ"
    )
    
    # วันที่และเวลา
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่ส่งคำขอ"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="วันที่พิจารณา"
    )
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="วันที่ดำเนินการ"
    )
    
    # หมายเหตุการพิจารณา
    approval_notes = models.TextField(
        blank=True,
        verbose_name="หมายเหตุการพิจารณา"
    )
    
    def __str__(self):
        return f"{self.request_number} - ยกเลิก {self.receipt.receipt_number}"
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = self.generate_request_number()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_request_number(cls):
        """สร้างเลขที่คำขอยกเลิก รูปแบบ CR-yymmdd-xxxx"""
        from django.utils import timezone
        today = timezone.now()
        date_part = today.strftime('%y%m%d')
        
        # หา sequence ของวันนี้
        prefix = f"CR-{date_part}-"
        last_request = cls.objects.filter(
            request_number__startswith=prefix
        ).order_by('-request_number').first()
        
        if last_request:
            # ดึงตัวเลขลำดับจากเลขที่เก่า
            last_sequence = int(last_request.request_number.split('-')[-1])
            new_sequence = last_sequence + 1
        else:
            new_sequence = 1
            
        return f"{prefix}{new_sequence:04d}"
    
    def can_be_approved_by(self, user):
        """ตรวจสอบว่าผู้ใช้สามารถอนุมัติคำขอยกเลิกนี้ได้หรือไม่"""
        # Admin/Aadmin: ดูได้อย่างเดียว ไม่มีสิทธิ์อนุมัติ (ลบออก)

        # ต้องอยู่ในแผนกเดียวกันเท่านั้น
        if user.get_department() != self.receipt.department.name:
            return False

        # เช็คว่า requester เป็น Basic User หรือ Manager
        requester_is_manager = self.requested_by.has_permission('receipt_cancel_approve')

        # Department Manager: อนุมัติคำขอของ Basic User เท่านั้น
        if user.has_permission('receipt_cancel_approve') and not requester_is_manager:
            return True

        # Senior Manager: อนุมัติคำขอของ Department Manager เท่านั้น
        if user.has_permission('receipt_cancel_approve_manager') and requester_is_manager:
            return True

        return False
    
    def approve(self, approved_by, notes=""):
        """อนุมัติคำขอยกเลิก"""
        from django.utils import timezone
        from django.core.exceptions import PermissionDenied

        # ตรวจสอบสิทธิ์
        if not self.can_be_approved_by(approved_by):
            raise PermissionDenied("คุณไม่มีสิทธิ์อนุมัติคำขอนี้")

        if self.status != 'pending':
            raise ValueError("สามารถอนุมัติได้เฉพาะคำขอที่รออนุมัติเท่านั้น")

        # อนุมัติคำขอ
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()

        # ยกเลิกใบสำคัญ (ข้ามการเช็คสิทธิ์เพราะผ่านการอนุมัติแล้ว)
        self.receipt.cancel(approved_by, self.cancel_reason, skip_permission_check=True)

        # เปลี่ยนสถานะเป็นดำเนินการแล้ว
        self.status = 'applied'
        self.applied_at = timezone.now()
        self.save()
    
    def reject(self, rejected_by, notes=""):
        """ปฏิเสธคำขอยกเลิก"""
        from django.utils import timezone
        from django.core.exceptions import PermissionDenied
        
        # ตรวจสอบสิทธิ์
        if not self.can_be_approved_by(rejected_by):
            raise PermissionDenied("คุณไม่มีสิทธิ์พิจารณาคำขอนี้")
        
        if self.status != 'pending':
            raise ValueError("สามารถปฏิเสธได้เฉพาะคำขอที่รออนุมัติเท่านั้น")
        
        self.status = 'rejected'
        self.approved_by = rejected_by
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()
    
    def withdraw(self):
        """ถอนคำขอ (โดยผู้ส่งคำขอ)"""
        if self.status == 'pending':
            self.status = 'withdrawn'
            self.save()
    
    class Meta:
        verbose_name = "คำขอยกเลิกใบสำคัญ"
        verbose_name_plural = "คำขอยกเลิกใบสำคัญ"
        ordering = ['-created_at']


class UserActivityLog(models.Model):
    """
    บันทึกประวัติการใช้งานระบบ (User Activity Log)
    เก็บข้อมูล login/logout และความผิดปกติเพื่อความปลอดภัย
    """

    ACTION_CHOICES = [
        ('login', 'เข้าสู่ระบบ'),
        ('logout', 'ออกจากระบบ'),
        ('login_failed', 'เข้าสู่ระบบล้มเหลว'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name="ผู้ใช้",
        help_text="null ได้ในกรณี login_failed"
    )
    username_attempted = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Username ที่พยายามเข้าสู่ระบบ",
        help_text="เก็บไว้กรณี login_failed"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="การดำเนินการ"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent",
        help_text="เก็บข้อมูล Browser/Device"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="หมายเหตุ",
        help_text="เช่น เหตุผลที่ login ล้มเหลว"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่-เวลา"
    )

    def __str__(self):
        user_display = self.user.get_display_name() if self.user else self.username_attempted
        return f"{user_display} - {self.get_action_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def log_login(cls, user, request):
        """บันทึกการเข้าสู่ระบบสำเร็จ"""
        return cls.objects.create(
            user=user,
            username_attempted=user.username,
            action='login',
            ip_address=cls._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

    @classmethod
    def log_logout(cls, user, request):
        """บันทึกการออกจากระบบ"""
        return cls.objects.create(
            user=user,
            username_attempted=user.username,
            action='logout',
            ip_address=cls._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

    @classmethod
    def log_failed_login(cls, username, request, reason=""):
        """บันทึกการเข้าสู่ระบบล้มเหลว"""
        return cls.objects.create(
            user=None,
            username_attempted=username,
            action='login_failed',
            ip_address=cls._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            notes=reason
        )

    @staticmethod
    def _get_client_ip(request):
        """ดึง IP Address ของผู้ใช้"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    class Meta:
        verbose_name = "ประวัติการใช้งานระบบ"
        verbose_name_plural = "ประวัติการใช้งานระบบ"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['created_at']),
        ]


class ReceiptChangeLog(models.Model):
    """
    บันทึกประวัติการเปลี่ยนแปลงใบสำคัญรับเงิน
    เก็บ audit trail ของการแก้ไขทั้งหมด
    """

    ACTION_CHOICES = [
        ('created', 'สร้างใบสำคัญ'),
        ('updated', 'แก้ไขใบสำคัญ'),
        ('cancelled', 'ยกเลิกใบสำคัญ'),
        ('edit_requested', 'ส่งคำร้องขอแก้ไข'),
        ('edit_approved', 'อนุมัติการแก้ไข'),
        ('edit_rejected', 'ปฏิเสธการแก้ไข'),
        ('edit_applied', 'ดำเนินการแก้ไข'),
    ]
    
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name="ใบสำคัญรับเงิน"
    )
    edit_request = models.ForeignKey(
        ReceiptEditRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_logs',
        verbose_name="คำร้องขอแก้ไข"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="การดำเนินการ"
    )
    field_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ฟิลด์ที่เปลี่ยน"
    )
    old_value = models.TextField(
        blank=True,
        verbose_name="ค่าเดิม"
    )
    new_value = models.TextField(
        blank=True,
        verbose_name="ค่าใหม่"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="หมายเหตุ"
    )
    
    # ผู้ทำ
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ผู้ดำเนินการ"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="วันที่เปลี่ยนแปลง"
    )
    
    def __str__(self):
        return f"{self.receipt.receipt_number} - {self.get_action_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
    
    @classmethod
    def log_change(cls, receipt, action, user=None, field_name='', old_value='', new_value='', notes='', edit_request=None):
        """บันทึกการเปลี่ยนแปลง"""
        return cls.objects.create(
            receipt=receipt,
            edit_request=edit_request,
            action=action,
            field_name=field_name,
            old_value=str(old_value),
            new_value=str(new_value),
            notes=notes,
            user=user
        )
    
    class Meta:
        verbose_name = "ประวัติการเปลี่ยนแปลง"
        verbose_name_plural = "ประวัติการเปลี่ยนแปลง"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receipt', 'action']),
            models.Index(fields=['edit_request']),
            models.Index(fields=['created_at']),
        ]