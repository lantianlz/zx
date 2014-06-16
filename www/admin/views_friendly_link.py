# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import CityBase, DepartmentBase, CustomerManagerBase, FriendlyLinkBase
from www.account.interface import UserBase


@verify_permission('')
def friendly_link(request, template_name='admin/friendly_link.html'):
    from www.kaihu.models import FriendlyLink
    link_types = [{'value': x[0], 'name': x[1]} for x in FriendlyLink.link_type_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_friendly_link')
@common_ajax_response
def add_friendly_link(request):
    link_type = request.REQUEST.get('link_type', 0)
    city_id = request.REQUEST.get('belong_city')
    if not city_id:
        city_id = None

    name = request.REQUEST.get('name')
    href = request.REQUEST.get('href')
    sort_num = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')

    return FriendlyLinkBase().add_friendly_link(name, href, link_type=link_type, city_id=city_id, sort_num=sort_num, des=des)


def format_friendly_link(objs, num):
    data = []

    for x in objs:
        num += 1
        data.append({
            'num': num,
            'link_id': x.id,
            'name': x.name,
            'href': x.href,
            'city_name': x.city.city if x.city else '',
            'city_id': x.city.id if x.city else '',
            'sort': x.sort_num,
            'state': x.state,
            'type': x.link_type,
            'des': x.des
        })

    return data


@verify_permission('query_friendly_link')
def search(request):
    data = []
    flb = FriendlyLinkBase()
    fls = []

    name = request.REQUEST.get('name')
    city_name = request.REQUEST.get('city_name')
    page_index = int(request.REQUEST.get('page_index'))

    if name:
        fls = FriendlyLinkBase().get_friendly_link_by_name(name)
    else:
        # 获取所有正常与不正常的客户经理
        fls = flb.get_all_friendly_link(state=None)

        # 城市
        if city_name:
            city = CityBase().get_one_city_by_name(city_name)
            if city:
                fls = fls.filter(city_id=city.id)
            else:
                fls = []

    page_objs = page.Cpt(fls, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_friendly_link(flb.format_friendly_links(page_objs[0]), num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_friendly_link')
def get_friendly_link_by_id(request):
    link_id = request.REQUEST.get('link_id')
    flb = FriendlyLinkBase()

    obj = flb.get_friendly_link_by_id(link_id, state=None)

    data = format_friendly_link(flb.format_friendly_links(obj), 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_friendly_link')
@common_ajax_response
def remove_friendly_link(request):
    link_id = request.REQUEST.get('link_id')
    return FriendlyLinkBase().remove_friendly_link(link_id)


@verify_permission('modify_friendly_link')
@common_ajax_response
def modify_friendly_link(request):
    link_id = request.REQUEST.get('link_id')
    link_type = request.REQUEST.get('link_type', 0)
    city_id = request.REQUEST.get('belong_city')
    if not city_id:
        city_id = None

    name = request.REQUEST.get('name')
    href = request.REQUEST.get('href')
    sort_num = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')

    return FriendlyLinkBase().modify_friendly_link(
        link_id, link_type=link_type, city_id=city_id, name=name, href=href, sort_num=sort_num, des=des
    )
