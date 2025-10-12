"""
Utility functions for the accounts app
"""
from datetime import datetime, date


def convert_to_thai_date(date_obj, format_type='full'):
    """
    แปลงวันที่เป็นรูปแบบไทย (ปีพุทธศักราช)

    Args:
        date_obj: datetime or date object
        format_type: 'full' = "4 ตุลาคม 2568"
                    'short' = "4 ต.ค. 2568"
                    'long' = "4 ตุลาคม พ.ศ. 2568"

    Returns:
        str: วันที่รูปแบบไทย
    """
    if not date_obj:
        return ''

    # Convert to datetime if it's a date object
    if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
        date_obj = datetime.combine(date_obj, datetime.min.time())

    if not isinstance(date_obj, (datetime, date)):
        return str(date_obj)

    # Thai month names
    thai_months_full = [
        '', 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
        'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ]

    thai_months_short = [
        '', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
        'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'
    ]

    day = date_obj.day
    month = date_obj.month
    year = date_obj.year + 543  # Convert to Buddhist year

    if format_type == 'short':
        return f"{day} {thai_months_short[month]} {year}"
    elif format_type == 'long':
        return f"{day} {thai_months_full[month]} พ.ศ. {year}"
    else:  # full (default)
        return f"{day} {thai_months_full[month]} {year}"
