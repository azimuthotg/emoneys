from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def add_commas(value):
    """เพิ่ม comma ให้ตัวเลข"""
    try:
        return intcomma(int(float(value)))
    except (ValueError, TypeError):
        return value