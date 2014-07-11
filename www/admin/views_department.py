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
def department(request, template_name='admin/department.html'):
    # from www.kaihu.models import FriendlyLink
    # link_types = [{'value': x[0], 'name': x[1]} for x in FriendlyLink.link_type_choices]
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


def format_department(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'department_id': x.id,
            'company_id': x.company.id,
            'company_name': x.company.name,
            'name': x.name,
            'des': x.des,
            'custom_manager_count': x.cm_count,
            'address': x.addr,
            'tel': x.tel,
            'sort_num': x.sort_num,
            'city_id': x.city_id,
            'city_name': CityBase().get_city_by_id(x.city_id).city
        })

    return data


@verify_permission('query_department')
def search(request):
    data = []
    db = DepartmentBase()
    objs = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    if name:
        objs = db.get_departments_by_name(name)
    else:
        objs = db.get_all_departments()

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_department(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_department')
def get_department_by_id(request):
    department_id = request.REQUEST.get('department_id')

    data = format_department([DepartmentBase().get_department_by_id(department_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


def get_company_by_name(request):
    '''
    根据名字查询公司
    '''
    company_name = request.REQUEST.get('company_name')

    result = []

    companys = CompanyBase().get_companys_by_name(company_name)

    if companys:
        for x in companys:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')


@verify_permission('modify_department')
@common_ajax_response
def modify_department(request):
    department_id = request.REQUEST.get('department_id')
    name = request.REQUEST.get('name')
    sort_num = request.REQUEST.get('sort')
    tel = request.REQUEST.get('tel')
    city_id = request.REQUEST.get('belong_city')
    company_id = request.REQUEST.get('belong_company')
    addr = request.REQUEST.get('addr')
    des = request.REQUEST.get('des')

    return DepartmentBase().modify_department(
        department_id, name=name, sort_num=sort_num, tel=tel, city_id=city_id, company_id=company_id, addr=addr, des=des
    )
