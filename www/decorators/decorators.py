# -*- coding: utf-8 -*-

"""
@attention: 和权限相关的装饰器添加
@author: lizheng
@date: 2013-12-10
"""


from django.http import HttpResponse, HttpResponseRedirect
import urllib


def member_required(func):
    """
    @attention: 过滤器, 是否是会员
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        if not (hasattr(request, 'user') and request.user.is_authenticated()):
            if request.is_ajax():
                return HttpResponse('need_login')
            else:
                url = urllib.quote_plus(request.get_full_path())
                return HttpResponseRedirect("/login?next_url=%s" % url)

        return func(request, *args, **kwargs)
    return _decorator


def protected_view(func):
    """
    @attention: 过滤器, 站内的views，不对站外用户开发
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        authentication = request.REQUEST.get('authentication')
        if authentication != u'ifit1003-codoon1012-newcodoon1112':
            raise Exception, u'the request from mom authentication error!'
            return HttpResponse('it works, but authenticate error!')
        return func(request, *args, **kwargs)
    return _decorator
