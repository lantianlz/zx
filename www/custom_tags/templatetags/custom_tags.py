# -*- coding: utf-8 -*-
"""
@note: 自定义标签文件
@author: lizheng
"""
import datetime
from django import template
register = template.Library()

from django.shortcuts import render_to_response
from django.template import RequestContext


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


@register.simple_tag(takes_context=True)
def question_type_option_display(context):
    """
    @note: 问答类型options方式展现
    """
    from www.question.interface import QuestionTypeBase
    aqts = QuestionTypeBase().get_all_question_type()

    return render_to_response('question/_question_type_option_display.html', locals(),
                              context_instance=context).content


@register.simple_tag(takes_context=True)
def question_type_nav_display(context):
    """
    @note: 问题类型导航方式展现
    """
    from www.question.interface import QuestionTypeBase
    aqts = QuestionTypeBase().get_all_question_type()
    return render_to_response('question/_question_type_nav_display.html', locals(),
                              context_instance=context).content
