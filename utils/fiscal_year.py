"""
Fiscal Year Utilities for Thai Government Fiscal Year
ปีงบประมาณไทย: 1 ตุลาคม - 30 กันยายน
"""
from datetime import datetime, date, timedelta
from typing import Tuple, Dict, Any


def get_current_fiscal_year() -> int:
    """
    คำนวณปีงบประมาณไทยจากวันที่ปัจจุบัน
    
    Returns:
        int: ปีงบประมาณ พ.ศ. เช่น 2568
        
    Example:
        - วันที่ 15 ต.ค. 2024 -> ปีงบ 2568 (1 ต.ค. 2567/2024 - 30 ก.ย. 2568/2025)
        - วันที่ 15 ก.ย. 2025 -> ปีงบ 2568 (1 ต.ค. 2567/2024 - 30 ก.ย. 2568/2025)
        - วันที่ 15 ต.ค. 2025 -> ปีงบ 2569 (1 ต.ค. 2568/2025 - 30 ก.ย. 2569/2026)
    """
    today = datetime.now().date()
    
    if today.month >= 10:  # ต.ค. - ธ.ค.
        # อยู่ในช่วงเริ่มต้นปีงบประมาณใหม่
        # ปีงบประมาณ = ปี พ.ศ. ปัจจุบัน + 1
        return (today.year + 543) + 1
    else:  # ม.ค. - ก.ย.
        # อยู่ในช่วงปลายปีงบประมาณ
        # ปีงบประมาณ = ปี พ.ศ. ปัจจุบัน
        return today.year + 543


def get_fiscal_year_dates(fiscal_year: int) -> Tuple[date, date]:
    """
    หาวันที่เริ่มต้นและสิ้นสุดของปีงบประมาณ
    
    Args:
        fiscal_year (int): ปีงบประมาณ พ.ศ. เช่น 2568
        
    Returns:
        Tuple[date, date]: (วันเริ่มต้น, วันสิ้นสุด)
        
    Example:
        get_fiscal_year_dates(2568) -> (2567-10-01, 2568-09-30)
    """
    # ปีงบประมาณ 2568 = 1 ต.ค. 2567 - 30 ก.ย. 2568
    # ปี ค.ศ. เริ่มต้น = ปีงบประมาณ - 544 - 1
    # ปี ค.ศ. สิ้นสุด = ปีงบประมาณ - 544
    start_year_ad = fiscal_year - 544 - 1  # 2568 - 544 - 1 = 2023... ผิด!
    
    # แก้ไขให้ถูกต้อง:
    # ปีงบประมาณ 2568 -> เริ่ม 1 ต.ค. 2567 (2024) -> สิ้นสุด 30 ก.ย. 2568 (2025)
    end_year_ad = fiscal_year - 543    # 2568 - 543 = 2025
    start_year_ad = end_year_ad - 1    # 2025 - 1 = 2024
    
    start_date = date(start_year_ad, 10, 1)  # 1 ต.ค. 2024
    end_date = date(end_year_ad, 9, 30)      # 30 ก.ย. 2025
    
    return start_date, end_date


def get_fiscal_year_from_date(target_date: date) -> int:
    """
    หาปีงบประมาณจากวันที่ที่กำหนด
    
    Args:
        target_date (date): วันที่ที่ต้องการหาปีงบประมาณ
        
    Returns:
        int: ปีงบประมาณ พ.ศ.
        
    Example:
        - วันที่ 15 ต.ค. 2024 -> ปีงบ 2568 (1 ต.ค. 2567/2024 - 30 ก.ย. 2568/2025)
        - วันที่ 15 ก.ย. 2025 -> ปีงบ 2568 (1 ต.ค. 2567/2024 - 30 ก.ย. 2568/2025)
    """
    if target_date.month >= 10:  # ต.ค. - ธ.ค.
        # ปีงบประมาณ = ปี พ.ศ. + 1
        return (target_date.year + 543) + 1
    else:  # ม.ค. - ก.ย.
        # ปีงบประมาณ = ปี พ.ศ. ปัจจุบัน
        return target_date.year + 543


def get_fiscal_year_suffix(fiscal_year: int = None) -> str:
    """
    สร้างรหัสปีงบประมาณ 2 หลัก สำหรับเลขที่เอกสาร
    
    Args:
        fiscal_year (int, optional): ปีงบประมาณ พ.ศ. ถ้าไม่ระบุจะใช้ปีปัจจุบัน
        
    Returns:
        str: รหัสปี 2 หลัก เช่น "68", "69"
        
    Example:
        get_fiscal_year_suffix(2568) -> "68"
        get_fiscal_year_suffix() -> "68" (ถ้าปีปัจจุบันคือ 2568)
    """
    if fiscal_year is None:
        fiscal_year = get_current_fiscal_year()
    
    return str(fiscal_year)[-2:]


def is_fiscal_year_transition_period() -> Tuple[bool, Dict[str, Any]]:
    """
    ตรวจสอบว่าอยู่ในช่วงเปลี่ยนปีงบประมาณหรือไม่ (1-7 ต.ค.)
    
    Returns:
        Tuple[bool, Dict]: (is_transition, transition_info)
        
    transition_info contains:
        - is_transition: bool
        - current_fiscal_year: int
        - previous_fiscal_year: int
        - days_until_transition: int (ถ้ายังไม่ถึง)
        - days_since_transition: int (ถ้าผ่านมาแล้ว)
        - warning_message: str
    """
    today = datetime.now().date()
    current_fy = get_current_fiscal_year()
    
    # หาวันที่ 1 ต.ค. ของปีงบประมาณปัจจุบัน
    if today.month >= 10:
        fiscal_start = date(today.year, 10, 1)
    else:
        fiscal_start = date(today.year - 1, 10, 1)
    
    # ตรวจสอบว่าอยู่ในช่วง 7 วันแรกหลังเปลี่ยนปีงบประมาณหรือไม่
    days_since_start = (today - fiscal_start).days
    is_early_transition = 0 <= days_since_start <= 6
    
    # ตรวจสอบว่าอยู่ในช่วง 7 วันก่อนเปลี่ยนปีงบประมาณหรือไม่
    next_fiscal_start = date(fiscal_start.year + 1, 10, 1)
    days_until_next = (next_fiscal_start - today).days
    is_pre_transition = 1 <= days_until_next <= 7
    
    is_transition = is_early_transition or is_pre_transition
    
    info = {
        'is_transition': is_transition,
        'current_fiscal_year': current_fy,
        'previous_fiscal_year': current_fy - 1,
        'fiscal_year_start': fiscal_start,
        'next_fiscal_year_start': next_fiscal_start,
        'days_since_fiscal_start': days_since_start,
        'days_until_next_fiscal': days_until_next,
        'is_early_transition': is_early_transition,
        'is_pre_transition': is_pre_transition,
        'warning_message': ''
    }
    
    if is_early_transition:
        info['warning_message'] = f"อยู่ในช่วงเริ่มต้นปีงบประมาณ {current_fy} (วันที่ {days_since_start + 1} หลังเปลี่ยนปี) ระบบจะไม่สามารถออกใบสำคัญย้อนหลังไปปีงบประมาณ {current_fy - 1} ได้"
    elif is_pre_transition:
        info['warning_message'] = f"ใกล้สิ้นสุดปีงบประมาณ {current_fy} แล้ว (อีก {days_until_next} วันจะเปลี่ยนเป็นปีงบประมาณ {current_fy + 1}) กรุณาเตรียมพร้อมสำหรับการเปลี่ยนแปลง"
    
    return is_transition, info


def get_volume_code(department_code: str, fiscal_year: int = None) -> str:
    """
    สร้างรหัสเล่มสำหรับใบสำคัญรับเงิน
    
    Args:
        department_code (str): รหัสหน่วยงาน เช่น "REG", "FIN"
        fiscal_year (int, optional): ปีงบประมาณ พ.ศ. ถ้าไม่ระบุจะใช้ปีปัจจุบัน
        
    Returns:
        str: รหัสเล่ม เช่น "REG68", "FIN69"
        
    Example:
        get_volume_code("REG", 2568) -> "REG68"
        get_volume_code("FIN") -> "FIN68" (ถ้าปีปัจจุบันคือ 2568)
    """
    if fiscal_year is None:
        fiscal_year = get_current_fiscal_year()
    
    year_suffix = get_fiscal_year_suffix(fiscal_year)
    return f"{department_code.upper()}{year_suffix}"


def format_fiscal_year_display(fiscal_year: int) -> str:
    """
    แปลงปีงบประมาณเป็นข้อความแสดงผล
    
    Args:
        fiscal_year (int): ปีงบประมาณ พ.ศ.
        
    Returns:
        str: ข้อความแสดงผล
        
    Example:
        format_fiscal_year_display(2568) -> "ปีงบประมาณ 2568 (1 ต.ค. 2567 - 30 ก.ย. 2568)"
    """
    start_date, end_date = get_fiscal_year_dates(fiscal_year)
    
    # แปลงวันที่เป็นภาษาไทย
    thai_months = [
        '', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
        'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'
    ]
    
    start_thai = f"{start_date.day} {thai_months[start_date.month]} {start_date.year + 543}"
    end_thai = f"{end_date.day} {thai_months[end_date.month]} {end_date.year + 543}"
    
    return f"ปีงบประมาณ {fiscal_year} ({start_thai} - {end_thai})"


def validate_document_date(document_date: date, allow_previous_fiscal: bool = False) -> Tuple[bool, str]:
    """
    ตรวจสอบความถูกต้องของวันที่เอกสาร
    
    Args:
        document_date (date): วันที่เอกสาร
        allow_previous_fiscal (bool): อนุญาตให้ออกเอกสารปีงบประมาณก่อนหน้าหรือไม่
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    today = datetime.now().date()
    current_fy = get_current_fiscal_year()
    document_fy = get_fiscal_year_from_date(document_date)
    
    # ตรวจสอบวันที่อนาคต
    if document_date > today:
        return False, "ไม่สามารถออกเอกสารในวันที่อนาคตได้"
    
    # ตรวจสอบปีงบประมาณ
    if document_fy > current_fy:
        return False, f"ไม่สามารถออกเอกสารสำหรับปีงบประมาณ {document_fy} ได้ (ปีปัจจุบัน: {current_fy})"
    
    if document_fy < current_fy and not allow_previous_fiscal:
        # ตรวจสอบว่าอยู่ในช่วง transition หรือไม่
        is_transition, transition_info = is_fiscal_year_transition_period()
        
        if is_transition and transition_info['is_early_transition']:
            return False, f"ไม่สามารถออกเอกสารย้อนหลังไปปีงบประมาณ {document_fy} ได้ เนื่องจากอยู่ในช่วงเริ่มต้นปีงบประมาณใหม่"
        elif not is_transition:
            return False, f"ไม่สามารถออกเอกสารย้อนหลังไปปีงบประมาณ {document_fy} ได้"
    
    return True, ""


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print("=== Thai Fiscal Year Utilities Demo ===")
    print(f"ปีงบประมาณปัจจุบัน: {get_current_fiscal_year()}")
    print(f"รหัสปี: {get_fiscal_year_suffix()}")
    print(f"รหัสเล่ม REG: {get_volume_code('REG')}")
    print(f"แสดงปีงบประมาณ: {format_fiscal_year_display(get_current_fiscal_year())}")
    
    is_transition, info = is_fiscal_year_transition_period()
    print(f"อยู่ในช่วงเปลี่ยนปีงบประมาณ: {is_transition}")
    if info['warning_message']:
        print(f"คำเตือน: {info['warning_message']}")