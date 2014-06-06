# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response, verify_permission
from common import cache


@verify_permission('')
def caches(request, template_name='admin/caches.html'):
    indexes = [{'name': cache.CACHE_INDEX[k][0], 'value': k} for k in cache.CACHE_INDEX.keys()]
    descs = [{'name': cache.CACHE_KEYS_DESC[k], 'value': k} for k in cache.CACHE_KEYS_DESC.keys()]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('modify_cache')
@common_ajax_response
def modify_cache(request):
    index = request.REQUEST.get('index')
    key = request.REQUEST.get('key_name')
    value = request.REQUEST.get('key_value', '')
    expire = request.REQUEST.get('key_expire', 3600)

    try:
        c = cache.Cache(cache.CACHE_INDEX[index][1])
        c.set(key, value, expire)
        return 0, u'修改成功!'
    except Exception, e:
        print e
        return 1, u'系统错误!'


@verify_permission('remove_cache')
@common_ajax_response
def remove_cache(request):
    index = request.REQUEST.get('index')
    key = request.REQUEST.get('key_name')

    try:
        c = cache.Cache(cache.CACHE_INDEX[index][1])
        c.delete(key)
        return 0, u'删除成功!'
    except Exception, e:
        print e
        return 1, u'系统错误!'


@verify_permission('get_cache')
@common_ajax_response
def get_cache(request):
    index = request.REQUEST.get('index')
    key = request.REQUEST.get('key_name')

    try:
        c = cache.Cache(cache.CACHE_INDEX[index][1])
        print c.get(key)
        return 0, c.get(key) or ''
    except Exception, e:
        print e
        return 1, u'系统错误!'
