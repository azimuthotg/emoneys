from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from accounts.utils import convert_to_thai_date
import json

register = template.Library()

@register.filter
def add_commas(value):
    """เพิ่ม comma ให้ตัวเลข"""
    try:
        return intcomma(int(float(value)))
    except (ValueError, TypeError):
        return value

@register.filter
def thai_date(value, format_type='full'):
    """
    แปลงวันที่เป็นรูปแบบไทย (ปีพุทธศักราช)
    ใช้ฟังก์ชัน convert_to_thai_date จาก accounts.utils

    Args:
        value: datetime, date object
        format_type: 'full' = "4 ตุลาคม 2568"
                    'short' = "4 ต.ค. 2568"
                    'long' = "4 ตุลาคม พ.ศ. 2568"

    Returns:
        str: วันที่รูปแบบไทย
    """
    return convert_to_thai_date(value, format_type)

@register.filter(name='tojson')
def tojson(value):
    """
    Convert Python object to JSON string for use in HTML attributes
    """
    if value is None:
        return 'null'
    return json.dumps(value, ensure_ascii=False)