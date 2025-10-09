"""
Fiscal Year Information Card Utilities
สำหรับแสดงข้อมูลปีงบประมาณแบบ Real-time
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any
from .fiscal_year import (
    get_current_fiscal_year,
    get_fiscal_year_dates,
    format_fiscal_year_display
)


def get_fiscal_year_info_card() -> Dict[str, Any]:
    """
    สร้างข้อมูลสำหรับการ์ดแสดงข้อมูลปีงบประมาณ
    
    Returns:
        Dict: ข้อมูลสำหรับแสดงในการ์ด
    """
    current_fy = get_current_fiscal_year()
    today = datetime.now().date()
    
    # หาวันที่เริ่มต้นและสิ้นสุดปีงบประมาณปัจจุบัน
    fy_start, fy_end = get_fiscal_year_dates(current_fy)
    
    # คำนวณวันที่คงเหลือ
    if today <= fy_end:
        days_remaining = (fy_end - today).days
        is_current_fy = True
    else:
        # หากเกินแล้ว (ไม่น่าจะเกิดขึ้น แต่เผื่อ)
        days_remaining = 0
        is_current_fy = False
    
    # คำนวณจำนวนวันทั้งหมดในปีงบประมาณ
    total_days = (fy_end - fy_start).days + 1
    days_passed = total_days - days_remaining if is_current_fy else total_days
    
    # คำนวณเปอร์เซ็นต์
    progress_percentage = (days_passed / total_days) * 100 if total_days > 0 else 0
    
    # หาข้อมูลปีงบประมาณถัดไป
    next_fy = current_fy + 1
    next_fy_start, next_fy_end = get_fiscal_year_dates(next_fy)
    
    # กำหนดสถานะ
    if days_remaining <= 0:
        status = "completed"
        status_text = "สิ้นสุดแล้ว"
        status_color = "secondary"
    elif days_remaining <= 7:
        status = "ending_soon"
        status_text = "ใกล้สิ้นสุด"
        status_color = "warning"
    elif days_remaining <= 30:
        status = "ending"
        status_text = "เข้าสู่ช่วงสิ้นสุด"
        status_color = "info"
    else:
        status = "active"
        status_text = "ปกติ"
        status_color = "success"
    
    # สร้างข้อความแสดงสถานะ
    if days_remaining > 0:
        if days_remaining == 1:
            countdown_text = "เหลือ 1 วัน"
        else:
            countdown_text = f"เหลือ {days_remaining} วัน"
        
        if days_remaining <= 7:
            detail_text = f"{countdown_text} จะสิ้นสุดปีงบประมาณ {current_fy}"
        elif days_remaining <= 30:
            detail_text = f"{countdown_text} จะสิ้นสุดปีงบประมาณ {current_fy}"
        else:
            detail_text = f"{countdown_text} จะสิ้นสุดปีงบประมาณ {current_fy}"
    else:
        countdown_text = "สิ้นสุดแล้ว"
        detail_text = f"ปีงบประมาณ {current_fy} สิ้นสุดแล้ว"
    
    # ข้อความเตรียมพร้อม
    if days_remaining <= 7 and days_remaining > 0:
        preparation_text = f"เตรียมพร้อมเข้าสู่ปีงบประมาณ {next_fy}"
        show_next_fy_info = True
    else:
        preparation_text = None
        show_next_fy_info = False
    
    # คำนวณ stroke-dashoffset สำหรับ progress circle
    # circumference = 2 * π * r = 2 * π * 54 = 339.292
    circumference = 339.292
    progress_dashoffset = circumference - (progress_percentage / 100 * circumference)
    
    return {
        # ข้อมูลปีงบประมาณปัจจุบัน
        'current_fiscal_year': current_fy,
        'current_fy_display': format_fiscal_year_display(current_fy),
        'current_fy_start': fy_start,
        'current_fy_end': fy_end,
        'current_fy_start_thai': format_thai_date(fy_start),
        'current_fy_end_thai': format_thai_date(fy_end),
        
        # ข้อมูลปีงบประมาณถัดไป
        'next_fiscal_year': next_fy,
        'next_fy_display': format_fiscal_year_display(next_fy),
        'next_fy_start': next_fy_start,
        'next_fy_start_thai': format_thai_date(next_fy_start),
        'show_next_fy_info': show_next_fy_info,
        
        # ข้อมูลวันที่
        'today': today,
        'today_thai': format_thai_date(today),
        'days_remaining': days_remaining,
        'days_passed': days_passed,
        'total_days': total_days,
        
        # ข้อมูลความคืบหน้า
        'progress_percentage': progress_percentage,
        'progress_percentage_rounded': round(progress_percentage, 1),
        'progress_dashoffset': round(progress_dashoffset, 2),
        
        # สถานะ
        'status': status,
        'status_text': status_text,
        'status_color': status_color,
        'countdown_text': countdown_text,
        'detail_text': detail_text,
        'preparation_text': preparation_text,
        
        # ข้อมูลเพิ่มเติม
        'is_transition_period': days_remaining <= 7 and days_remaining > 0,
        'is_current_fy': is_current_fy,
        'week_remaining': days_remaining <= 7,
        'month_remaining': days_remaining <= 30,
    }


def format_thai_date(date_obj: date) -> str:
    """
    แปลงวันที่เป็นรูปแบบไทย
    
    Args:
        date_obj (date): วันที่
        
    Returns:
        str: วันที่ในรูปแบบไทย เช่น "24 ก.ย. 2568"
    """
    thai_months = [
        '', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
        'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'
    ]
    
    thai_year = date_obj.year + 543
    thai_month = thai_months[date_obj.month]
    
    return f"{date_obj.day} {thai_month} {thai_year}"


def get_volume_status_summary(current_fy: int) -> Dict[str, Any]:
    """
    สรุปสถานะเล่มเอกสารในปีงบประมาณปัจจุบัน
    
    Args:
        current_fy (int): ปีงบประมาณปัจจุบัน
        
    Returns:
        Dict: สรุปสถานะเล่มเอกสาร
    """
    try:
        from accounts.models import DocumentVolume, Department
        
        # เล่มทั้งหมดในปีนี้
        total_volumes = DocumentVolume.objects.filter(fiscal_year=current_fy).count()
        active_volumes = DocumentVolume.objects.filter(
            fiscal_year=current_fy, 
            status='active'
        ).count()
        closed_volumes = total_volumes - active_volumes
        
        # หน่วยงานทั้งหมด
        total_departments = Department.objects.filter(is_active=True).count()
        
        # หน่วยงานที่มีเล่มแล้ว
        departments_with_volumes = DocumentVolume.objects.filter(
            fiscal_year=current_fy
        ).values_list('department_id', flat=True).distinct().count()
        
        # หน่วยงานที่ยังไม่มีเล่ม
        departments_without_volumes = total_departments - departments_with_volumes
        
        # เปอร์เซ็นต์ความครอบคลุม
        coverage_percentage = (departments_with_volumes / total_departments * 100) if total_departments > 0 else 0
        
        return {
            'total_volumes': total_volumes,
            'active_volumes': active_volumes,
            'closed_volumes': closed_volumes,
            'total_departments': total_departments,
            'departments_with_volumes': departments_with_volumes,
            'departments_without_volumes': departments_without_volumes,
            'coverage_percentage': round(coverage_percentage, 1),
            'has_volumes': total_volumes > 0,
            'full_coverage': departments_without_volumes == 0,
        }
        
    except ImportError:
        # หาก models ยังไม่ได้ import (เช่น ใน testing)
        return {
            'total_volumes': 0,
            'active_volumes': 0,
            'closed_volumes': 0,
            'total_departments': 0,
            'departments_with_volumes': 0,
            'departments_without_volumes': 0,
            'coverage_percentage': 0,
            'has_volumes': False,
            'full_coverage': False,
        }


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print("=" * 60)
    print("📊 ข้อมูลปีงบประมาณ Real-time")
    print("=" * 60)
    
    info = get_fiscal_year_info_card()
    
    print(f"🗓️  {info['current_fy_display']}")
    print(f"📅 วันนี้: {info['today_thai']}")
    print(f"⏰ {info['detail_text']}")
    print(f"📈 ความคืบหน้า: {info['progress_percentage_rounded']}%")
    print(f"🚦 สถานะ: {info['status_text']}")
    
    if info['preparation_text']:
        print(f"⚠️  {info['preparation_text']}")
    
    print()
    print("🏢 สรุปสถานะเล่มเอกสาร:")
    volume_info = get_volume_status_summary(info['current_fiscal_year'])
    print(f"   เล่มทั้งหมด: {volume_info['total_volumes']}")
    print(f"   ความครอบคลุม: {volume_info['coverage_percentage']}%")