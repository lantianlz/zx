# -*- coding: utf-8 -*-
"""
@note: 自定义标签文件
@author: lizheng
"""
import datetime
from django import template
register = template.Library()


@register.simple_tag
def current_time(format_string):
    """
    @note: 当前时间tag
    """
    return datetime.datetime.now().strftime(format_string)


@register.simple_tag(takes_context=True)
def import_variable(context, name, value, json_flag=False):
    """
    @note: 传入一个变量到context中
    """
    from django.utils.encoding import smart_str
    import json
    value = smart_str(value)
    context[name] = value if not json_flag else json.loads(value)
    return ''
