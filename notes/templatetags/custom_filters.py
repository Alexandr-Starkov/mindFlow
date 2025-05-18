from django import template
from datetime import datetime


register = template.Library()


@register.filter
def isoformat_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return ''
