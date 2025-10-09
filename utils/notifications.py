"""
Notification System for Fiscal Year Transitions
ระบบแจ้งเตือนสำหรับการเปลี่ยนปีงบประมาณและการจัดการเล่มเอกสาร
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .fiscal_year import (
    get_current_fiscal_year,
    is_fiscal_year_transition_period,
    get_fiscal_year_dates,
    format_fiscal_year_display
)

User = get_user_model()


class FiscalYearNotificationManager:
    """จัดการการแจ้งเตือนเกี่ยวกับปีงบประมาณและเล่มเอกสาร"""
    
    def __init__(self):
        self.current_fiscal_year = get_current_fiscal_year()
        self.is_transition, self.transition_info = is_fiscal_year_transition_period()
    
    def get_transition_warnings(self) -> List[Dict[str, Any]]:
        """
        สร้างคำเตือนสำหรับช่วงเปลี่ยนปีงบประมาณ
        
        Returns:
            List[Dict]: รายการคำเตือน
        """
        warnings = []
        
        if not self.is_transition:
            return warnings
        
        info = self.transition_info
        
        if info['is_early_transition']:
            # ช่วงเริ่มต้นปีงบประมาณใหม่
            warnings.append({
                'type': 'fiscal_year_start',
                'level': 'warning',
                'title': f'เข้าสู่ปีงบประมาณใหม่ {info["current_fiscal_year"]}',
                'message': info['warning_message'],
                'details': {
                    'current_fiscal_year': info['current_fiscal_year'],
                    'previous_fiscal_year': info['previous_fiscal_year'],
                    'days_since_start': info['days_since_fiscal_start'],
                    'restriction': 'ไม่สามารถออกใบสำคัญย้อนหลังไปปีงบประมาณที่แล้วได้'
                },
                'actions': [
                    {
                        'label': 'ตรวจสอบเล่มใหม่',
                        'url': '/accounts/management/document-numbering/',
                        'type': 'primary'
                    }
                ]
            })
        
        elif info['is_pre_transition']:
            # ช่วงก่อนสิ้นสุดปีงบประมาณ
            warnings.append({
                'type': 'fiscal_year_ending',
                'level': 'info',
                'title': f'ใกล้สิ้นสุดปีงบประมาณ {info["current_fiscal_year"]}',
                'message': info['warning_message'],
                'details': {
                    'current_fiscal_year': info['current_fiscal_year'],
                    'next_fiscal_year': info['current_fiscal_year'] + 1,
                    'days_remaining': info['days_until_next_fiscal'],
                    'preparation_needed': 'ควรเตรียมพร้อมสำหรับเล่มใหม่'
                },
                'actions': [
                    {
                        'label': 'เตรียมข้อมูลเล่มใหม่',
                        'url': '/accounts/management/document-numbering/',
                        'type': 'info'
                    }
                ]
            })
        
        return warnings
    
    def get_volume_warnings(self) -> List[Dict[str, Any]]:
        """
        ตรวจสอบและสร้างคำเตือนเกี่ยวกับเล่มเอกสาร
        
        Returns:
            List[Dict]: รายการคำเตือนเกี่ยวกับเล่มเอกสาร
        """
        warnings = []
        
        try:
            from accounts.models import DocumentVolume, Department
            
            # ตรวจสอบเล่มที่ใกล้เต็ม
            nearly_full_volumes = DocumentVolume.objects.filter(
                status='active',
                fiscal_year=self.current_fiscal_year
            ).select_related('department')
            
            for volume in nearly_full_volumes:
                usage_percentage = volume.get_usage_percentage()
                
                if usage_percentage >= 95:
                    warnings.append({
                        'type': 'volume_critical',
                        'level': 'danger',
                        'title': f'เล่ม {volume.volume_code} เกือบเต็ม',
                        'message': f'เล่ม {volume.volume_code} ของ{volume.department.name} ใช้งานไปแล้ว {usage_percentage:.1f}% ({volume.last_document_number}/{volume.max_documents})',
                        'details': {
                            'volume_code': volume.volume_code,
                            'department': volume.department.name,
                            'usage_percentage': usage_percentage,
                            'remaining': volume.max_documents - volume.last_document_number
                        },
                        'actions': [
                            {
                                'label': 'ดูรายละเอียด',
                                'url': f'/accounts/management/document-numbering/#volume-{volume.id}',
                                'type': 'danger'
                            }
                        ]
                    })
                
                elif usage_percentage >= 80:
                    warnings.append({
                        'type': 'volume_warning',
                        'level': 'warning',
                        'title': f'เล่ม {volume.volume_code} ใกล้เต็ม',
                        'message': f'เล่ม {volume.volume_code} ของ{volume.department.name} ใช้งานไปแล้ว {usage_percentage:.1f}%',
                        'details': {
                            'volume_code': volume.volume_code,
                            'department': volume.department.name,
                            'usage_percentage': usage_percentage,
                            'remaining': volume.max_documents - volume.last_document_number
                        },
                        'actions': [
                            {
                                'label': 'ตรวจสอบ',
                                'url': f'/accounts/management/document-numbering/#volume-{volume.id}',
                                'type': 'warning'
                            }
                        ]
                    })
            
            # ตรวจสอบหน่วยงานที่ยังไม่มีเล่มในปีงบประมาณปัจจุบัน
            departments_with_volumes = set(
                DocumentVolume.objects.filter(
                    fiscal_year=self.current_fiscal_year
                ).values_list('department_id', flat=True)
            )
            
            all_active_departments = Department.objects.filter(is_active=True)
            
            for dept in all_active_departments:
                if dept.id not in departments_with_volumes:
                    warnings.append({
                        'type': 'volume_missing',
                        'level': 'info',
                        'title': f'ยังไม่มีเล่มสำหรับ {dept.name}',
                        'message': f'{dept.name} ({dept.code}) ยังไม่มีเล่มเอกสารสำหรับปีงบประมาณ {self.current_fiscal_year}',
                        'details': {
                            'department': dept.name,
                            'department_code': dept.code,
                            'fiscal_year': self.current_fiscal_year,
                            'note': 'เล่มจะถูกสร้างอัตโนมัติเมื่อออกใบสำคัญแรก'
                        },
                        'actions': [
                            {
                                'label': 'สร้างเล่มล่วงหน้า',
                                'url': '/accounts/management/document-numbering/',
                                'type': 'info'
                            }
                        ]
                    })
        
        except ImportError:
            pass  # Models ยังไม่ได้ migrate
        
        return warnings
    
    def get_all_notifications(self) -> Dict[str, Any]:
        """
        รวบรวมการแจ้งเตือนทั้งหมด
        
        Returns:
            Dict: ข้อมูลการแจ้งเตือนทั้งหมด
        """
        transition_warnings = self.get_transition_warnings()
        volume_warnings = self.get_volume_warnings()
        
        all_warnings = transition_warnings + volume_warnings
        
        # จัดกลุ่มตามระดับความสำคัญ
        grouped_warnings = {
            'danger': [w for w in all_warnings if w['level'] == 'danger'],
            'warning': [w for w in all_warnings if w['level'] == 'warning'],
            'info': [w for w in all_warnings if w['level'] == 'info'],
        }
        
        return {
            'fiscal_year_info': {
                'current_fiscal_year': self.current_fiscal_year,
                'display_name': format_fiscal_year_display(self.current_fiscal_year),
                'is_transition': self.is_transition,
                'transition_info': self.transition_info if self.is_transition else None
            },
            'warnings': grouped_warnings,
            'total_warnings': len(all_warnings),
            'has_critical': len(grouped_warnings['danger']) > 0,
            'has_warnings': len(grouped_warnings['warning']) > 0,
        }
    
    def send_email_notifications(self, recipients: List[str] = None) -> bool:
        """
        ส่งการแจ้งเตือนทางอีเมล
        
        Args:
            recipients (List[str], optional): รายการอีเมลผู้รับ ถ้าไม่ระบุจะส่งให้ Admin ทั้งหมด
            
        Returns:
            bool: สำเร็จหรือไม่
        """
        if not recipients:
            # ส่งให้ Admin ทั้งหมด
            recipients = list(
                User.objects.filter(
                    is_staff=True,
                    is_active=True,
                    email__isnull=False
                ).exclude(email='').values_list('email', flat=True)
            )
        
        if not recipients:
            return False
        
        notifications = self.get_all_notifications()
        
        # ตรวจสอบว่ามีสิ่งที่ต้องแจ้งเตือนหรือไม่
        if notifications['total_warnings'] == 0:
            return True
        
        try:
            subject = f"แจ้งเตือนระบบใบสำคัญรับเงิน - ปีงบประมาณ {self.current_fiscal_year}"
            
            # สร้างเนื้อหาอีเมล
            html_content = render_to_string('emails/fiscal_year_notification.html', {
                'notifications': notifications,
                'site_name': 'ระบบออกใบสำคัญรับเงิน มหาวิทยาลัยนครพนม'
            })
            
            # สร้างเนื้อหา text สำหรับอีเมลที่ไม่รองรับ HTML
            text_content = self._create_text_notification(notifications)
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_content,
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending email notifications: {e}")
            return False
    
    def _create_text_notification(self, notifications: Dict[str, Any]) -> str:
        """สร้างเนื้อหาการแจ้งเตือนแบบข้อความ"""
        lines = [
            "=== แจ้งเตือนระบบใบสำคัญรับเงิน ===",
            f"ปีงบประมาณปัจจุบัน: {notifications['fiscal_year_info']['display_name']}",
            ""
        ]
        
        for level in ['danger', 'warning', 'info']:
            warnings = notifications['warnings'][level]
            if warnings:
                lines.append(f"--- {level.upper()} ---")
                for warning in warnings:
                    lines.append(f"• {warning['title']}")
                    lines.append(f"  {warning['message']}")
                lines.append("")
        
        lines.append("กรุณาตรวจสอบระบบเพื่อดูรายละเอียดเพิ่มเติม")
        
        return "\n".join(lines)


def get_dashboard_notifications() -> Dict[str, Any]:
    """
    ฟังก์ชันสำหรับแสดงการแจ้งเตือนใน Dashboard
    
    Returns:
        Dict: ข้อมูลการแจ้งเตือนสำหรับ Dashboard
    """
    manager = FiscalYearNotificationManager()
    return manager.get_all_notifications()


def send_daily_notifications() -> bool:
    """
    ฟังก์ชันสำหรับส่งการแจ้งเตือนรายวัน (สำหรับ cron job)
    
    Returns:
        bool: สำเร็จหรือไม่
    """
    manager = FiscalYearNotificationManager()
    
    # ส่งการแจ้งเตือนเฉพาะในช่วงที่สำคัญ
    if manager.is_transition:
        return manager.send_email_notifications()
    
    # หรือเมื่อมีเล่มที่ใกล้เต็ม
    volume_warnings = manager.get_volume_warnings()
    critical_warnings = [w for w in volume_warnings if w['level'] == 'danger']
    
    if critical_warnings:
        return manager.send_email_notifications()
    
    return True


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print("=== Fiscal Year Notification System Demo ===")
    
    manager = FiscalYearNotificationManager()
    notifications = manager.get_all_notifications()
    
    print(f"ปีงบประมาณปัจจุบัน: {notifications['fiscal_year_info']['current_fiscal_year']}")
    print(f"จำนวนการแจ้งเตือน: {notifications['total_warnings']}")
    print(f"มีการแจ้งเตือนวิกฤติ: {notifications['has_critical']}")
    
    for level in ['danger', 'warning', 'info']:
        warnings = notifications['warnings'][level]
        if warnings:
            print(f"\n{level.upper()}:")
            for warning in warnings:
                print(f"- {warning['title']}: {warning['message']}")