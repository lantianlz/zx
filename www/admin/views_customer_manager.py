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
        for x in departments[:10]:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')


@verify_permission('add_customer_manager')
def add_customer_manager(request):
    user_id = request.REQUEST.get('user_id')
    department_id = request.REQUEST.get('belong_department')
    end_date = request.REQUEST.get('end_date')
    vip_info = request.REQUEST.get('vip_info')
    sort_num = request.REQUEST.get('sort')
    qq = request.REQUEST.get('qq')
    entry_time = request.REQUEST.get('entry_time')
    mobile = request.REQUEST.get('mobile')
    real_name = request.REQUEST.get('real_name')
    id_card = request.REQUEST.get('id_card')
    id_cert = request.REQUEST.get('id_cert')
    des = request.REQUEST.get('des')
    pay_type = request.REQUEST.get('pay_type', 0)

    img_name = ''
    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='custom_manager')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = CustomerManagerBase().add_customer_manager(
        user_id, department_id, end_date, vip_info,
        sort_num, img=img_name, qq=qq, entry_time=entry_time, mobile=mobile, 
        real_name=real_name, id_card=id_card, id_cert=id_cert, des=des,
        pay_type=pay_type
    )
    
    if flag == 0:
        url = "/admin/user/customer_manager#modify/" + user_id
    else:
        url = "/admin/user/customer_manager?%s#add/%s" % (msg, user_id)
        
    return HttpResponseRedirect(url)


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
            'pay_type': x.pay_type,
            'real_name': x.real_name,
            'entry_time': str(x.entry_time)[:10],
            'id_card': x.id_card,
            'id_cert': x.id_cert,
            'des': x.des,
            'img': x.img
        })

    return data


@verify_permission('query_customer_manager')
def search(request):
    data = []
    cmb = CustomerManagerBase()
    cms = []

    user_nick = request.REQUEST.get('user_nick')
    city_name = request.REQUEST.get('city_name')
    state = request.REQUEST.get('state')
    page_index = int(request.REQUEST.get('page_index'))

    cms = cmb.get_custom_managers_for_admin(user_nick, city_name, state)

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

    if obj:
        obj = cmb.format_customer_managers([obj])

    data = format_customer_managers(obj, 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_customer_manager')
@common_ajax_response
def delete_customer_manager(request):
    user_id = request.REQUEST.get('user_id')
    return CustomerManagerBase().remove_customer_manager(user_id)


@verify_permission('modify_customer_manager')
def modify_customer_manager(request):
    user_id = request.REQUEST.get('user_id')
    department_id = request.REQUEST.get('belong_department')
    end_date = request.REQUEST.get('end_date')
    sort_num = request.REQUEST.get('sort')
    vip_info = request.REQUEST.get('vip_info')
    qq = request.REQUEST.get('qq')
    mobile = request.REQUEST.get('mobile')
    pay_type = request.REQUEST.get('pay_type', 0)
    entry_time = request.REQUEST.get('entry_time')
    real_name = request.REQUEST.get('real_name')
    id_card = request.REQUEST.get('id_card')
    id_cert = request.REQUEST.get('id_cert')
    des = request.REQUEST.get('des')
    state = request.REQUEST.get('state', '1')
    state = True if state == '1' else False

    obj = CustomerManagerBase().get_customer_manager_by_user_id(user_id)
    img_name = obj.img
    
    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='custom_manager')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)
    
    
    flag, msg = CustomerManagerBase().modify_customer_manager(
        user_id, department_id=department_id, end_date=end_date, state=state,
        sort_num=sort_num, vip_info=vip_info, qq=qq, mobile=mobile, 
        pay_type=pay_type, entry_time=entry_time, real_name=real_name,
        id_card=id_card, id_cert=id_cert, des=des, img=img_name
    )
    
    if flag == 0:
        url = "/admin/user/customer_manager#modify/" + user_id
    else:
        url = "/admin/user/customer_manager?%s#modify/%s" % (msg, user_id)
        
    return HttpResponseRedirect(url)
