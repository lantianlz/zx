# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page, utils
from www.misc.decorators import common_ajax_response_for_api
from www.kaihu import interface

cb = interface.CityBase()
db = interface.DepartmentBase()
cmb = interface.CustomerManagerBase()
flb = interface.FriendlyLinkBase()
atb = interface.ArticleBase()
nb = interface.NewsBase()


def _format_api_departments(departments):
    results = []
    for department in departments:
        results.append({"id": department.id, "short_name": department.get_short_name(), "cm_count": department.cm_count, "img": department.company.img,
                        "tel": department.tel, "addr": department.addr, "company_name": department.company.get_short_name(), "des":department.des})
    return results


@common_ajax_response_for_api
def api_get_department_list(request, template_name='kaihu/department_list.html'):
    city = cb.get_city_by_id(request.REQUEST.get('city_id', 1974))
    if not city:
        raise Http404
    departments = db.get_departments_by_city_id(city.id)
    department_count = len(departments)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(departments, count=10, page=page_num).info
    departments = page_objs[0]
    return dict(departments=_format_api_departments(departments), department_count=department_count)
    

def _format_api_custom_managers(custom_managers):
    results = []
    for custom_manager in custom_managers:
        results.append({
            "id": custom_manager["user_id"], 
            "nick": custom_manager["user_nick"],
            "img": custom_manager["user_avatar"],
            "company_name": custom_manager["company_short_name"],
            "vip_info": custom_manager["vip_info"],
            "qq": custom_manager["qq"],
            "mobile": custom_manager["mobile"],
        })
    return results
    
@common_ajax_response_for_api
def api_get_custom_manager_list(request):
    city = cb.get_city_by_id(request.REQUEST.get('city_id', 1974))
    if not city:
        raise Http404
    custom_managers = cmb.get_customer_managers_by_city_id(city.id)
    custom_managers_count = len(custom_managers)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(custom_managers, count=10, page=page_num).info
    custom_managers = page_objs[0]

    return dict(custom_managers=_format_api_custom_managers(custom_managers), custom_managers_count=custom_managers_count)
    
    
@common_ajax_response_for_api
def api_get_province_and_city(request):
    data = []
    for province in cb.get_all_provinces().order_by("id"):
        temp = {
            "id": province.id,
            "name": province.province,
            "cities": []
        }
        for city in cb.get_citys_by_province(province.id):
            temp["cities"].append({
                "id": city.id,
                "name": city.city
            })
        
        data.append(temp)
    
    return dict(data=data)

