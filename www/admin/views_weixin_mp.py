# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.toutiao.interface import ArticleTypeBase, WeixinMpBase


@verify_permission('')
def weixin_mp(request, template_name='admin/weixin_mp.html'):
    types = [{'value': x.id, 'name': x.name} for x in ArticleTypeBase().get_all_valid_article_type()]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def get_weixin_mp_by_name(request):
    weixin_name = request.REQUEST.get('weixin_name')

    result = []

    objs = WeixinMpBase().get_weixin_mp_by_name(weixin_name)

    if objs:
        for x in objs:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')


@verify_permission('query_weixin_mp')
def get_weixin_info(request):
    open_id = request.REQUEST.get('open_id')
    data = WeixinMpBase().get_mp_info_by_open_id(open_id)

    return HttpResponse(
        json.dumps({
            'open_id': data[0],
            'name': data[1],
            'weixin_id': data[2],
            'des': data[3],
            'vip_info': data[4],
            'img': data[5],
            'qrimg': data[6],
            'sort_num': 0
        }),
        mimetype='application/json'
    )


@verify_permission('add_weixin_mp')
@common_ajax_response
def add_weixin_mp(request):
    open_id = request.REQUEST.get('open_id')
    name = request.REQUEST.get('name')
    weixin_id = request.REQUEST.get('weixin_id')
    des = request.REQUEST.get('des')
    vip_info = request.REQUEST.get('vip_info', '')
    img = request.REQUEST.get('img')
    qrimg = request.REQUEST.get('qrimg')
    article_type = request.REQUEST.get('article_type')
    sort_num = request.REQUEST.get('sort_num')

    code, msg = WeixinMpBase().add_mp(open_id, name, weixin_id, des, vip_info, img, qrimg, article_type, False, sort_num)

    return code, msg if code else msg.id


def format_weixin_wp(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'weixin_mp_id': x.id,
            'weixin_id': x.weixin_id,
            'open_id': x.open_id,
            'name': x.name,
            'des': x.des,
            'vip_info': x.vip_info,
            'img': x.img,
            'qrimg': x.qrimg,
            'is_silence': x.is_silence,
            'sort_num': x.sort_num,
            'article_type': x.article_type.id if x.article_type else '',
            'state': x.state
        })

    return data


@verify_permission('query_weixin_mp')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state')

    page_index = int(request.REQUEST.get('page_index'))

    objs = WeixinMpBase().search_weixin_mp_for_admin(name, state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_weixin_wp(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_weixin_mp')
def get_weixin_mp_by_id(request):
    weixin_mp_id = request.REQUEST.get('weixin_mp_id')

    data = format_weixin_wp([WeixinMpBase().get_weixin_mp_by_id(weixin_mp_id, None)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_weixin_mp')
@common_ajax_response
def modify_weixin_mp(request):
    weixin_mp_id = request.REQUEST.get('weixin_mp_id')
    open_id = request.REQUEST.get('open_id')
    name = request.REQUEST.get('name')
    weixin_id = request.REQUEST.get('weixin_id')
    des = request.REQUEST.get('des')
    vip_info = request.REQUEST.get('vip_info', '')
    img = request.REQUEST.get('img')
    qrimg = request.REQUEST.get('qrimg')
    article_type = request.REQUEST.get('article_type')
    sort_num = request.REQUEST.get('sort_num')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    return WeixinMpBase().modify_weixin_mp(
        weixin_mp_id, open_id=open_id, name=name, weixin_id=weixin_id,
        des=des, vip_info=vip_info, img=img, qrimg=qrimg, article_type_id=article_type,
        sort_num=sort_num, state=state
    )
