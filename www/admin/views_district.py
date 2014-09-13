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
def district(request, template_name='admin/district.html'):
    # from www.kaihu.models import FriendlyLink
    # link_types = [{'value': x[0], 'name': x[1]} for x in FriendlyLink.link_type_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_district(objs, num):
    data = []

    for x in objs:
        num += 1
        city = CityBase().get_city_by_id(x.city)

        data.append({
            'num': num,
            'district_id': x.id,
            'district_name': x.district,
            'city_id': city.id if city else '',
            'city_name': city.city if city else '',
            'is_show': x.is_show,
            'pinyin': x.pinyin,
            'pinyin_abbr': x.pinyin_abbr,
            'sort_num': x.sort_num,
            # 'rank': CityBase().get_city_baidu_rank(x) if x.is_show else '未开放',
            # 'rank_url': x.get_baidu_search_url() if x.is_show else '#'
            'rank': u'未开放',
            'rank_url': ''
        })

    return data


@verify_permission('query_city')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    is_show = request.REQUEST.get('is_show')

    page_index = int(request.REQUEST.get('page_index'))

    objs = CityBase().search_districts_for_admin(name, is_show)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_district(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_city')
def get_district_by_id(request):
    district_id = request.REQUEST.get('district_id')

    data = format_district([CityBase().get_district_by_id(district_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_city')
@common_ajax_response
def modify_district(request):
    district_id = request.REQUEST.get('district_id')
    district = request.REQUEST.get('name')
    pinyin = request.REQUEST.get('pinyin')
    pinyin_abbr = request.REQUEST.get('pinyin_abbr')
    sort_num = int(request.REQUEST.get('sort'))
    is_show = int(request.REQUEST.get('is_show'))

    return CityBase().modify_district(
        district_id, pinyin=pinyin, sort_num=sort_num, pinyin_abbr=pinyin_abbr, is_show=is_show, district=district
    )
