from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # API endpoints for mobile/AJAX
    path('api/login/', views.handle_api_login, name='api_login'),
    
    # User Management
    path('management/users/', views.user_management_view, name='user_management'),
    path('management/users/create/staff/', views.manual_staff_create_view, name='manual_staff_create'),
    path('management/users/create/student/', views.manual_student_create_view, name='manual_student_create'),
    
    # Admin AJAX endpoints
    path('management/approve-user/<int:user_id>/', views.approve_user_ajax, name='approve_user_ajax'),
    path('management/reject-user/<int:user_id>/', views.reject_user_ajax, name='reject_user_ajax'),
    path('management/suspend-user/<int:user_id>/', views.suspend_user_ajax, name='suspend_user_ajax'),
    path('management/activate-user/<int:user_id>/', views.activate_user_ajax, name='activate_user_ajax'),
    path('management/user-details/<int:user_id>/', views.user_details_ajax, name='user_details_ajax'),
    
    # Legacy admin URLs for backward compatibility
    path('admin/approve-user/<int:user_id>/', views.approve_user_ajax, name='admin_approve_user_ajax'),
    path('admin/reject-user/<int:user_id>/', views.reject_user_ajax, name='admin_reject_user_ajax'),
    path('admin/user-details/<int:user_id>/', views.user_details_ajax, name='admin_user_details_ajax'),
    path('management/user/<int:user_id>/roles/', views.user_roles_ajax, name='user_roles_ajax'),
    path('management/available-roles/', views.get_available_roles_ajax, name='available_roles_ajax'),
    
    # Roles and Permissions URLs
    path('admin/roles-permissions/', views.roles_permissions_view, name='roles_permissions'),
    path('admin/role/create/', views.role_create_view, name='role_create'),
    path('admin/role/<int:role_id>/edit/', views.role_edit_view, name='role_edit'),
    path('admin/role/<int:role_id>/delete/', views.role_delete_view, name='role_delete'),
    path('admin/user/<int:user_id>/assign-roles/', views.user_role_assign_view, name='user_role_assign'),
    
    # Department Management URLs
    path('management/departments/', views.department_management_view, name='department_management'),
    path('management/department/create/', views.department_create_view, name='department_create'),
    path('management/department/<int:department_id>/edit/', views.department_edit_view, name='department_edit'),
    path('management/department/<int:department_id>/delete/', views.department_delete_view, name='department_delete'),
    path('management/department/<int:department_id>/activate/', views.department_activate_view, name='department_activate'),
    path('management/department/<int:department_id>/deactivate/', views.department_deactivate_view, name='department_deactivate'),
    path('management/available-npu-departments/', views.available_npu_departments_ajax, name='available_npu_departments_ajax'),
    
    # Document Numbering URLs
    path('management/document-numbering/', views.document_numbering_view, name='document_numbering'),
    path('management/volume/<int:volume_id>/close/', views.close_volume_ajax, name='close_volume_ajax'),
    
    # QR Code Verification URLs (เก่า)
    path('verify/', views.receipt_verify_view, name='receipt_verify_scan'),
    path('verify/<str:verification_hash>/', views.receipt_verify_view, name='receipt_verify'),
    
    # QR Code Verification URLs (ใหม่ - แบบง่าย)
    # URL ใหม่: รวมรหัสหน่วยงาน (ไม่ซ้ำกัน)
    path('check/<str:dept_code>/<str:date_part>/<str:number_part>/', views.receipt_check_public_view, name='receipt_check_public_with_dept'),
    # URL เก่า: ยังรองรับ (backward compatibility)
    path('check/<str:date_part>/<str:number_part>/', views.receipt_check_public_view, name='receipt_check_public'),
    
    # QR Code Image Generation
    path('receipt/<int:receipt_id>/qr/', views.receipt_qr_image_view, name='receipt_qr_image'),
    
    # Receipt Frontend URLs
    path('receipt/create/', views.receipt_create_view, name='receipt_create'),
    path('receipt/list/', views.receipt_list_view, name='receipt_list'),
    path('receipt/<int:receipt_id>/', views.receipt_detail_view, name='receipt_detail'),
    path('receipt/<int:receipt_id>/edit/', views.receipt_edit_view, name='receipt_edit'),
    path('receipt/<int:receipt_id>/pdf/', views.receipt_pdf_view, name='receipt_pdf'),
    path('receipt/<int:receipt_id>/pdf/download/', views.receipt_pdf_download_view, name='receipt_pdf_download'),
    path('receipt/<int:receipt_id>/pdf/v2/', views.receipt_pdf_v2_view, name='receipt_pdf_v2'),
    path('receipt/<int:receipt_id>/pdf/v2/download/', views.receipt_pdf_v2_download_view, name='receipt_pdf_v2_download'),
    path('receipt/save/', views.receipt_save_ajax, name='receipt_save'),
    path('receipt/<int:receipt_id>/update/', views.receipt_update_ajax, name='receipt_update'),
    path('receipt/<int:receipt_id>/complete/', views.receipt_complete_draft_ajax, name='receipt_complete_draft'),

    # Edit Request URLs
    path('receipt/<int:receipt_id>/edit-request/', views.edit_request_create_view, name='edit_request_create'),
    path('edit-requests/', views.edit_request_list_view, name='edit_request_list'),
    path('edit-request/<int:request_id>/', views.edit_request_detail_view, name='edit_request_detail'),
    path('edit-request/<int:request_id>/approve/', views.edit_request_approval_view, name='edit_request_approval'),
    path('edit-request/<int:request_id>/withdraw/', views.edit_request_withdraw_view, name='edit_request_withdraw'),
    
    # Cancel Request URLs
    path('cancel-requests/', views.cancel_request_list_view, name='cancel_request_list'),
    path('receipt/<int:receipt_id>/cancel-direct/', views.receipt_cancel_direct_view, name='receipt_cancel_direct'),
    path('receipt/<int:receipt_id>/cancel-request/', views.receipt_cancel_request_view, name='receipt_cancel_request'),
    path('cancel-request/<int:request_id>/', views.cancel_request_detail_view, name='cancel_request_detail'),
    # DEPRECATED: ฟอร์มอนุมัติถูกรวมเข้าไปในหน้า detail แล้ว
    # path('cancel-request/<int:request_id>/approve/', views.cancel_request_approve_view, name='cancel_request_approve'),
    path('cancel-request/<int:request_id>/withdraw/', views.cancel_request_withdraw_view, name='cancel_request_withdraw'),
    
    # Reports URLs
    path('reports/', views.reports_dashboard_view, name='reports_dashboard'),
    path('reports/receipts/', views.receipt_report_view, name='receipt_report'),
    path('reports/receipts/export/excel/', views.receipt_report_excel_export, name='receipt_report_excel_export'),
    path('reports/receipts/export/pdf/', views.receipt_report_pdf_export, name='receipt_report_pdf_export'),
    path('reports/summary/', views.revenue_summary_report_view, name='revenue_summary_report'),
    path('reports/summary/export/excel/', views.revenue_summary_excel_export, name='revenue_summary_excel_export'),
    path('reports/summary/export/pdf/', views.revenue_summary_pdf_export, name='revenue_summary_pdf_export'),
    path('reports/audit-log/', views.audit_log_view, name='audit_log'),
    path('reports/audit-log/export/excel/', views.audit_log_excel_export, name='audit_log_excel_export'),

    # User Activity Log (Admin Only)
    path('management/user-activity-log/', views.user_activity_log_view, name='user_activity_log'),
    path('management/user-activity-log/export/excel/', views.user_activity_log_excel_export, name='user_activity_log_excel_export'),

    # Template Management (Admin Only)
    path('manage/templates/', views.receipt_templates_list, name='receipt_templates_list'),
    path('manage/templates/create/', views.receipt_template_create, name='receipt_template_create'),
    path('manage/templates/<int:template_id>/edit/', views.receipt_template_edit, name='receipt_template_edit'),
    path('manage/templates/<int:template_id>/delete/', views.receipt_template_delete, name='receipt_template_delete'),
]