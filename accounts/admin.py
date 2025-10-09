from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User, Department, FieldLock, NPUApiLog, ReceiptTemplate, Receipt, ReceiptItem, ReceiptChangeLog, UserActivityLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Enhanced admin interface for file-based authenticated users"""
    
    list_display = ('username', 'full_name', 'department', 'approval_status', 
                   'approved_at', 'is_active', 'last_npu_sync')
    list_filter = ('approval_status', 'is_active', 'staff_type', 'department', 'last_npu_sync')
    search_fields = ('username', 'full_name', 'ldap_uid', 'department', 'contact_email', 
                    'npu_staff_id', 'first_name_th', 'last_name_th')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('ข้อมูลจาก NPU API', {
            'fields': ('ldap_uid', 'npu_staff_id', 'full_name', 'prefix_name', 
                      'first_name_th', 'last_name_th', 'birth_date', 'gender'),
            'classes': ('collapse',),
        }),
        ('ข้อมูลองค์กร (NPU)', {
            'fields': ('department', 'position_title', 'staff_type', 'staff_sub_type', 
                      'employment_status'),
            'classes': ('collapse',),
        }),
        ('ข้อมูล Sync', {
            'fields': ('last_npu_sync', 'npu_last_login'),
            'classes': ('collapse',),
        }),
        ('ข้อมูลภายใน', {
            'fields': ('department_internal_name', 'job_description', 'contact_email', 
                      'line_user_id'),
            'classes': ('collapse',),
        }),
        ('สิทธิ์ใบสำคัญรับเงิน (DEPRECATED)', {
            'fields': ('is_document_staff', 'can_forward_documents'),
            'classes': ('collapse',),
            'description': 'ใช้ Role system แทน - กรุณาจัดการบทบาทผ่านหน้า Roles & Permissions',
        }),
        ('สถานะการอนุมัติ', {
            'fields': ('approval_status', 'approved_at'),
        }),
        ('การตั้งค่า PWA', {
            'fields': ('push_subscription_endpoint', 'push_subscription_keys', 
                      'notifications_enabled'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'last_npu_sync', 'npu_last_login')
    
    actions = ['approve_users', 'reject_users', 'suspend_users', 'reactivate_users']
    
    def approve_users(self, request, queryset):
        """Bulk approve users"""
        count = 0
        for user in queryset.filter(approval_status='pending'):
            user.approve_user()
            count += 1
        self.message_user(request, f'อนุมัติผู้ใช้ {count} คน เรียบร้อยแล้ว')
    approve_users.short_description = 'อนุมัติผู้ใช้ที่เลือก'
    
    def reject_users(self, request, queryset):
        """Bulk reject users"""
        count = 0
        for user in queryset.exclude(approval_status='approved'):
            user.reject_user()
            count += 1
        self.message_user(request, f'ปฏิเสธผู้ใช้ {count} คน เรียบร้อยแล้ว')
    reject_users.short_description = 'ปฏิเสธผู้ใช้ที่เลือก'
    
    def suspend_users(self, request, queryset):
        """Bulk suspend users"""
        count = 0
        for user in queryset.filter(approval_status='approved'):
            user.suspend_user()
            count += 1
        self.message_user(request, f'ระงับผู้ใช้ {count} คน เรียบร้อยแล้ว')
    suspend_users.short_description = 'ระงับผู้ใช้ที่เลือก'
    
    def reactivate_users(self, request, queryset):
        """Bulk reactivate users"""
        count = 0
        for user in queryset.filter(approval_status__in=['suspended', 'rejected']):
            user.approve_user()
            count += 1
        self.message_user(request, f'เปิดใช้งานผู้ใช้ {count} คน เรียบร้อยแล้ว')
    reactivate_users.short_description = 'เปิดใช้งานผู้ใช้ที่เลือก'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for internal departments"""
    
    list_display = ('name', 'code', 'is_active', 'member_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    
    def member_count(self, obj):
        """Count users in this department"""
        return obj.user_set.count()
    member_count.short_description = 'จำนวนสมาชิก'
    member_count.admin_order_field = 'user_count'
    
    def get_queryset(self, request):
        """Add annotation for member count"""
        qs = super().get_queryset(request)
        return qs.extra(
            select={'user_count': 'SELECT COUNT(*) FROM accounts_user WHERE department_internal_id = accounts_department.id'}
        )


@admin.register(FieldLock)
class FieldLockAdmin(admin.ModelAdmin):
    """Admin interface for field locks"""
    
    list_display = ('user', 'locked_fields_display', 'get_user_department')
    list_filter = ('user__department', 'user__is_active')
    search_fields = ('user__username', 'user__full_name', 'user__ldap_uid')
    
    def locked_fields_display(self, obj):
        """Display locked fields as comma-separated string"""
        if obj.locked_fields:
            return ', '.join(obj.locked_fields)
        return 'ไม่มี'
    locked_fields_display.short_description = 'ฟิลด์ที่ล็อค'
    
    def get_user_department(self, obj):
        """Get user's department"""
        return obj.user.department or 'ไม่ระบุ'
    get_user_department.short_description = 'หน่วยงาน'


@admin.register(NPUApiLog)
class NPUApiLogAdmin(admin.ModelAdmin):
    """Admin interface for NPU API logs"""
    
    list_display = ('user_ldap_uid', 'action', 'status', 'response_time_ms', 'created_at')
    list_filter = ('action', 'status', 'created_at')
    search_fields = ('user_ldap_uid', 'error_message')
    readonly_fields = ('user_ldap_uid', 'action', 'status', 'request_data', 
                      'response_data', 'error_message', 'created_at', 'response_time_ms')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False  # Logs are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs should not be modified
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superuser can delete logs


@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Receipt Templates"""
    
    list_display = ('name', 'max_amount', 'fixed_amount', 'is_active', 'category')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'category')
    ordering = ('name',)


class ReceiptItemInline(admin.TabularInline):
    """Inline admin for Receipt Items"""
    model = ReceiptItem
    extra = 1
    fields = ('template', 'description', 'amount', 'order')


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Admin interface for Receipts"""
    
    list_display = ('receipt_number', 'recipient_name', 'department', 'total_amount', 'is_loan', 'status', 'created_at')
    list_filter = ('status', 'is_loan', 'department', 'created_at')
    search_fields = ('receipt_number', 'recipient_name', 'recipient_id_card')
    ordering = ('-created_at',)
    readonly_fields = ('receipt_number', 'total_amount_text', 'volume_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('ข้อมูลใบสำคัญ', {
            'fields': ('receipt_number', 'volume_code', 'department', 'created_by', 'status')
        }),
        ('ข้อมูลผู้รับ', {
            'fields': ('recipient_name', 'recipient_address', 'recipient_id_card')
        }),
        ('ข้อมูลเงิน', {
            'fields': ('total_amount', 'total_amount_text', 'is_loan')
        }),
        ('วันที่', {
            'fields': ('receipt_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReceiptItemInline]


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    """Admin interface for Receipt Items"""

    list_display = ('receipt', 'description', 'amount', 'template', 'order')
    list_filter = ('template', 'receipt__department')
    search_fields = ('receipt__receipt_number', 'description')
    ordering = ('receipt', 'order')


@admin.register(ReceiptChangeLog)
class ReceiptChangeLogAdmin(admin.ModelAdmin):
    """Admin interface for Receipt Change Logs (Audit Trail)"""

    list_display = ('receipt_number', 'get_action_display', 'user_display', 'created_at', 'notes_preview')
    list_filter = ('action', 'created_at', 'receipt__department', 'receipt__status')
    search_fields = ('receipt__receipt_number', 'user__full_name', 'user__username', 'notes')
    readonly_fields = ('receipt', 'edit_request', 'action', 'field_name', 'old_value',
                      'new_value', 'notes', 'user', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('ข้อมูลใบสำคัญ', {
            'fields': ('receipt', 'edit_request')
        }),
        ('การดำเนินการ', {
            'fields': ('action', 'field_name', 'old_value', 'new_value')
        }),
        ('รายละเอียด', {
            'fields': ('notes', 'user', 'created_at')
        }),
    )

    def receipt_number(self, obj):
        """แสดงเลขที่ใบสำคัญ"""
        return obj.receipt.receipt_number
    receipt_number.short_description = 'เลขที่ใบสำคัญ'
    receipt_number.admin_order_field = 'receipt__receipt_number'

    def user_display(self, obj):
        """แสดงชื่อผู้ทำ"""
        return obj.user.get_display_name() if obj.user else '-'
    user_display.short_description = 'ผู้ดำเนินการ'
    user_display.admin_order_field = 'user__full_name'

    def notes_preview(self, obj):
        """แสดงตัวอย่างหมายเหตุ"""
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'หมายเหตุ'

    def has_add_permission(self, request):
        """ห้ามเพิ่ม log ด้วยตนเอง"""
        return False

    def has_change_permission(self, request, obj=None):
        """ห้ามแก้ไข log"""
        return False

    def has_delete_permission(self, request, obj=None):
        """อนุญาตให้ superuser ลบได้เท่านั้น"""
        return request.user.is_superuser


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for User Activity Logs (Login/Logout tracking)"""

    list_display = ('created_at', 'user_display', 'action_display', 'ip_address', 'success_indicator')
    list_filter = ('action', 'created_at')
    search_fields = ('username_attempted', 'ip_address', 'user__full_name', 'user__username', 'notes')
    readonly_fields = ('user', 'username_attempted', 'action', 'ip_address', 'user_agent', 'notes', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('ข้อมูลผู้ใช้', {
            'fields': ('user', 'username_attempted')
        }),
        ('การดำเนินการ', {
            'fields': ('action', 'created_at')
        }),
        ('ข้อมูลเทคนิค', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('หมายเหตุ', {
            'fields': ('notes',)
        }),
    )

    def user_display(self, obj):
        """แสดงชื่อผู้ใช้"""
        if obj.user:
            return obj.user.get_display_name()
        else:
            return f"[ล้มเหลว] {obj.username_attempted}"
    user_display.short_description = 'ผู้ใช้'
    user_display.admin_order_field = 'user__full_name'

    def action_display(self, obj):
        """แสดงการดำเนินการพร้อมสี"""
        return obj.get_action_display()
    action_display.short_description = 'การดำเนินการ'
    action_display.admin_order_field = 'action'

    def success_indicator(self, obj):
        """แสดงสถานะความสำเร็จ"""
        if obj.action == 'login_failed':
            return '❌ ล้มเหลว'
        else:
            return '✅ สำเร็จ'
    success_indicator.short_description = 'สถานะ'

    def has_add_permission(self, request):
        """ห้ามเพิ่ม log ด้วยตนเอง"""
        return False

    def has_change_permission(self, request, obj=None):
        """ห้ามแก้ไข log"""
        return False

    def has_delete_permission(self, request, obj=None):
        """อนุญาตให้ superuser ลบได้เท่านั้น"""
        return request.user.is_superuser


# Customize admin site
admin.site.site_header = 'ระบบออกใบสำคัญรับเงิน - มหาวิทยาลัยนครพนม'
admin.site.site_title = 'Receipt System Admin - NPU'
admin.site.index_title = 'ยินดีต้อนรับสู่ระบบออกใบสำคัญรับเงิน กองคลัง สำนักงานอธิการบดี'