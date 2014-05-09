# -*- coding: utf-8 -*-

"""
@note: 和权限相关的装饰器添加
@author: lizheng
@date: 2013-12-10
"""


from django.http import HttpResponse, HttpResponseRedirect
import urllib
from common import cache


def member_required(func):
    """
    @note: 过滤器, 是否是会员
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        if not (hasattr(request, 'user') and request.user.is_authenticated()):
            if request.is_ajax():
                return HttpResponse('need_login')
            else:
                try:
                    url = urllib.quote_plus(request.get_full_path())
                except:
                    url = '/'
                return HttpResponseRedirect("/login?next_url=%s" % url)

        return func(request, *args, **kwargs)
    return _decorator


def staff_required(func):
    """
    @note: 过滤器, 是否是内部成员
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        if not (hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff()):
            if request.is_ajax():
                return HttpResponse('need_staff')
            else:
                HttpResponse(u'需要管理员权限才可')

        return func(request, *args, **kwargs)
    return _decorator


def protected_view(func):
    """
    @note: 过滤器, 站内的views，不对站外用户开发
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        authentication = request.REQUEST.get('authentication')
        if authentication != u'token':
            raise Exception, u'the request from mom authentication error!'
            return HttpResponse('it works, but authenticate error!')
        return func(request, *args, **kwargs)
    return _decorator


def cache_required(cache_key, cache_key_type=0, expire=3600 * 24, cache_config=cache.CACHE_TMP):
    '''
    @note: 缓存装饰器
    cache_key格式为1：'answer_summary_%s' 取方法的第一个值做键 2：'global_var'固定值
    如果需要格式化cache_key的话，cache_key_type为
    0：传参为：func(self, cache_key_param)
    1：传参为：func(cache_key_param)
    2：传参为：func(self) cache_key为self.id
    '''

    def _wrap_decorator(func):
        func.cache_key = cache_key

        def _decorator(*args, **kwargs):
            cache_key = func.cache_key
            must_update_cache = kwargs.get('must_update_cache')
            if '%' in cache_key:
                assert len(args) > 0
                if cache_key_type == 0:
                    key = args[1].id if hasattr(args[1], 'id') else args[1]
                    assert isinstance(key, (unicode, str, int, long, float))
                    cache_key = cache_key % key
                if cache_key_type == 1:
                    cache_key = cache_key % args[0]
                if cache_key_type == 2:
                    cache_key = cache_key % args[0].id
            return cache.get_or_update_data_from_cache(cache_key, expire, cache_config, must_update_cache, func, *args, **kwargs)
        return _decorator
    return _wrap_decorator
