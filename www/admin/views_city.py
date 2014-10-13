# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import CityBase, DepartmentBase, CompanyBase


@verify_permission('')
def city(request, template_name='admin/city.html'):
    # from www.kaihu.models import FriendlyLink
    # link_types = [{'value': x[0], 'name': x[1]} for x in FriendlyLink.link_type_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_city(objs, num):
    data = []

    for x in objs:
        num += 1
        province = CityBase().get_province_by_id(x.province)

        data.append({
            'num': num,
            'city_id': x.id,
            'city_name': x.city,
            'province_id': province.id if province else '',
            'province_name': province.province if province else '',
            'is_show': x.is_show,
            'pinyin': x.pinyin,
            'pinyin_abbr': x.pinyin_abbr,
            'sort_num': x.sort_num,
            'rank': x.baidu_rank if x.is_show else '未开放',
            'rank_url': x.get_baidu_search_url() if x.is_show else '#',
            'department_count': len(DepartmentBase().get_departments_by_city_id(x.id)),
            'note': x.note or ''
        })

    return data


@verify_permission('query_city')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    is_show = request.REQUEST.get('is_show')

    page_index = int(request.REQUEST.get('page_index'))

    objs = CityBase().search_citys_for_admin(name, is_show)

    page_objs = page.Cpt(objs, count=500, page=page_index).info

    # 格式化json
    num = 500 * (page_index - 1)
    data = format_city(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_city')
def get_city_by_id(request):
    city_id = request.REQUEST.get('city_id')

    data = format_city([CityBase().get_city_by_id(city_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_city')
@common_ajax_response
def modify_city(request):
    city_id = request.REQUEST.get('city_id')
    city = request.REQUEST.get('name')
    pinyin = request.REQUEST.get('pinyin')
    pinyin_abbr = request.REQUEST.get('pinyin_abbr')
    sort_num = int(request.REQUEST.get('sort'))
    is_show = int(request.REQUEST.get('is_show'))
    note = request.REQUEST.get('note')

    return CityBase().modify_city(
        city_id, pinyin=pinyin, sort_num=sort_num, pinyin_abbr=pinyin_abbr, 
        is_show=is_show, city=city, note=note
    )

@verify_permission('modify_city')
@common_ajax_response
def modify_note(request):
    city_id = request.REQUEST.get('city_id')
    note = request.REQUEST.get('note')

    return CityBase().modify_city(
        city_id, note=note
    )

@verify_permission('query_city')
def get_districts_by_city(request):
    city_id = request.REQUEST.get('city_id')
    data = []

    for d in CityBase().get_districts_by_city(city_id):
        data.append({
            'district_id': d.id,
            'district_name': d.district
        })

    return HttpResponse(json.dumps(data), mimetype='application/json')
