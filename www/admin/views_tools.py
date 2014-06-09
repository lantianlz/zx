# -*- coding: utf-8 -*-

import json
import datetime
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response, verify_permission
from common import cache, debug, page

from message.interface import GlobalNoticeBase


#--------------------------------- 缓存管理
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
        debug.get_debug_detail(e)
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
        debug.get_debug_detail(e)
        return 1, u'系统错误!'


@verify_permission('get_cache')
@common_ajax_response
def get_cache(request):
    index = request.REQUEST.get('index')
    key = request.REQUEST.get('key_name')

    try:
        c = cache.Cache(cache.CACHE_INDEX[index][1])

        return 0, c.get(key) or ''
    except Exception, e:
        debug.get_debug_detail(e)
        return 1, u'系统错误!'


#--------------------------------- 全站通告
@verify_permission('')
def notice(request, template_name='admin/notice.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_notice')
def search_notice(request):

    data = []
    gnb = GlobalNoticeBase()

    page_index = int(request.REQUEST.get('page_index'))

    page_objs = page.Cpt(gnb.get_all_global_notice(), count=10, page=page_index).info

    num = 10 * (page_index - 1)
    for obj in page_objs[0]:
        num += 1
        data.append({
            'num': num,
            'notice_id': obj.id,
            'content': obj.content,
            'start_time': str(obj.start_time),
            'end_time': str(obj.end_time),
            'level': obj.level,
            'state': True if (obj.end_time - datetime.datetime.now()).total_seconds > 0 else False
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('add_notice')
@common_ajax_response
def add_notice(request):
    content = request.REQUEST.get('content')
    start_time = request.REQUEST.get('start_time')
    end_time = request.REQUEST.get('end_time')
    level = request.REQUEST.get('level')

    return GlobalNoticeBase().create_global_notice(
        content, start_time, end_time, request.user.id, level)


@verify_permission('query_notice')
def get_notice_by_id(request):
    notice_id = request.REQUEST.get('notice_id')

    data = ''

    obj = GlobalNoticeBase().get_notice_by_id(notice_id)
    if obj:
        data = {
            'num': 1,
            'notice_id': obj.id,
            'content': obj.content,
            'start_time': str(obj.start_time)[:10],
            'end_time': str(obj.end_time)[:10],
            'level': obj.level,
            'state': True if (obj.end_time - datetime.datetime.now()).total_seconds > 0 else False
        }

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_notice')
@common_ajax_response
def modify_notice(request):
    notice_id = request.REQUEST.get('notice_id')
    content = request.REQUEST.get('content')
    start_time = request.REQUEST.get('start_time')
    end_time = request.REQUEST.get('end_time')
    level = request.REQUEST.get('level')

    return GlobalNoticeBase().modify_global_notice(
        notice_id, content=content, start_time=start_time, end_time=end_time, level=level)


@verify_permission('remove_notice')
@common_ajax_response
def remove_notice(request):
    notice_id = request.REQUEST.get('notice_id')

    return GlobalNoticeBase().remove_global_notice(notice_id)
