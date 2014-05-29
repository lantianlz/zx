# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import CityBase, DepartmentBase, CustomerManagerBase
from www.account.interface import UserBase


@verify_permission('')
def customer_manager(request, template_name='admin/customer_manager.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def get_citys_by_name(request):
    '''
    根据名字查询城市
    '''
    city_name = request.REQUEST.get('city_name')

    result = []

    citys = CityBase().get_citys_by_name(city_name)

    if citys:
        for x in citys:
            result.append([x.id, x.city, None, x.city])

    return HttpResponse(json.dumps(result), mimetype='application/json')


def get_departments_by_name(request):
    '''
    根据名字查询营业部
    '''
    department_name = request.REQUEST.get('department_name')

    result = []

    departments = DepartmentBase().get_departments_by_name(department_name)

    if departments:
        for x in departments:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')


@verify_permission('add_customer_manager')
@common_ajax_response
def add_customer_manager(request):
    user_id = request.REQUEST.get('user_id')
    department_id = request.REQUEST.get('belong_department')
    end_date = request.REQUEST.get('end_date')
    sort_num = request.REQUEST.get('sort')
    vip_info = request.REQUEST.get('vip_info')
    qq = request.REQUEST.get('qq')
    mobile = request.REQUEST.get('mobile')
    pay_type = request.REQUEST.get('pay_type', 0)

    return CustomerManagerBase().add_customer_manager(
        user_id, department_id, end_date, vip_info,
        sort_num, qq=qq, mobile=mobile, pay_type=pay_type
    )


def format_customer_managers(objs, num):
    data = []

    for x in objs:
        num += 1
        data.append({
            'num': num,
            'user_id': x.user.id,
            'user_nick': x.user.nick,
            'user_avatar': x.user.get_avatar_25(),
            'city_name': x.department.city.city,
            'city_id': x.department.city.id,
            'department_name': x.department.name,
            'department_id': x.department.id,
            'sort': x.sort_num,
            'vip_info': x.vip_info,
            'end_date': str(x.end_date)[:10],
            'qq': x.qq,
            'mobile': x.mobile,
            'state': x.state,
            'pay_type': x.pay_type
        })

    return data


@verify_permission('query_customer_manager')
def search(request):
    data = []
    cmb = CustomerManagerBase()
    cms = []

    user_nick = request.REQUEST.get('user_nick')
    city_name = request.REQUEST.get('city_name')
    page_index = int(request.REQUEST.get('page_index'))

    if user_nick:
        user = UserBase().get_user_by_nick(user_nick)
        if user:
            cms = [cmb.get_customer_manager_by_user_id(user.id)]
    else:
        # 获取所有正常于不正常的客户经理
        cms = cmb.get_all_customer_managers(active=False, state=None)

        # 城市
        if city_name:
            city = CityBase().get_one_city_by_name(city_name)
            if city:
                cms = cms.filter(city_id=city.id)
            else:
                cms = []

    page_objs = page.Cpt(cms, count=10, page=page_index).info

    cms = cmb.format_customer_managers(page_objs[0])

    # 格式化json
    num = 10 * (page_index - 1) + 0
    data = format_customer_managers(cms, num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_customer_manager')
def get_customer_manager_by_user_id(request):
    user_id = request.REQUEST.get('user_id')
    cmb = CustomerManagerBase()
    obj = cmb.get_customer_manager_by_user_id(user_id)
    obj = cmb.format_customer_managers([obj])

    data = format_customer_managers(obj, 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_customer_manager')
@common_ajax_response
def delete_customer_manager(request):
    user_id = request.REQUEST.get('user_id')
    return CustomerManagerBase().remove_customer_manager(user_id)


@verify_permission('modify_customer_manager')
@common_ajax_response
def modify_customer_manager(request):
    user_id = request.REQUEST.get('user_id')
    department_id = request.REQUEST.get('belong_department')
    end_date = request.REQUEST.get('end_date')
    sort_num = request.REQUEST.get('sort')
    vip_info = request.REQUEST.get('vip_info')
    qq = request.REQUEST.get('qq')
    mobile = request.REQUEST.get('mobile')
    pay_type = request.REQUEST.get('pay_type', 0)

    return CustomerManagerBase().modify_customer_manager(
        user_id, department_id=department_id, end_date=end_date,
        sort_num=sort_num, vip_info=vip_info, qq=qq, mobile=mobile, pay_type=pay_type
    )
