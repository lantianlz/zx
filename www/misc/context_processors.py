# -*- coding: utf-8 -*-

"""
@attention: 定义全局上下文变量
@author: lizheng
@date: 2011-11-28
"""

from django.conf import settings


def config(request):
    """
    @attention: Adds settings-related context variables to the context.
    """
    return {
        'DEBUG': settings.DEBUG,
        'MEDIA_VERSION':'001',
        # 'MEDIA_URL':settings.MEDIA_URL,
    }
