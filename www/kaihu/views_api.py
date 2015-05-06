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
                        "tel": department.tel, "addr": department.addr, "company_name": department.company.get_short_name(), "des": department.des})
    return results


@common_ajax_response_for_api
def api_get_department_list(request):
    city = cb.get_city_by_id(int(request.REQUEST.get('city_id', '0')) or 1974)
    if not city:
        raise Http404
    departments = db.get_departments_by_city_id(city.id)
    department_count = len(departments)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(departments, count=10, page=page_num).info
    departments = page_objs[0]
    return dict(departments=_format_api_departments(departments), department_count=department_count)


@common_ajax_response_for_api
def api_get_city_by_ip(request):
    ip = utils.get_clientip(request)
    city_info = utils.get_city_by_ip_from_taobao(ip)
    city_name = "成都市"
    city_id = 1974
    if city_info["country"] == u"中国":
        city = cb.get_one_city_by_name(city_info["city"])
        if city:
            city_name = city.city
            city_id = city.id

    return dict(ip=ip, city_name=city_name, city_id=city_id)


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
    from django.conf import settings

    city = cb.get_city_by_id(int(request.REQUEST.get('city_id', '0')) or 1974)
    if not city:
        raise Http404
    # =============================下线所有客户经理====================================
    # custom_managers = cmb.get_customer_managers_by_city_id(city.id)
    # if not custom_managers:
    #     defualt_user_id = "f762a6f5d2b711e39a09685b35d0bf16" if settings.DEBUG else "d1baa40e5f3a11e4813d00163e003240"
    #     custom_managers = cmb.format_customer_managers_for_ajax([cmb.get_customer_manager_by_user_id(user_id=defualt_user_id), ])
    # =============================只保留2个==========================================
    custom_managers = cmb.format_customer_managers_for_ajax([
        cmb.get_customer_manager_by_user_id(user_id="d1baa40e5f3a11e4813d00163e003240"), 
        cmb.get_customer_manager_by_user_id(user_id="248eaf24aa7b11e3ac1c00163e003240"), 
    ])
    # ===============================================================================
    custom_managers_count = len(custom_managers)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_count = int(request.REQUEST.get('page_count', 30))
    page_objs = page.Cpt(custom_managers, count=page_count, page=page_num).info
    custom_managers = page_objs[0]

    # 广州单独处理
    if city.id == 1204:
        # custom_managers = [x for x in custom_managers if x['user_id'] == '5e46b030f23d11e4ab5f00163e003240']
        custom_managers = cmb.format_customer_managers_for_ajax([
            cmb.get_customer_manager_by_user_id(user_id="5e46b030f23d11e4ab5f00163e003240"), 
        ])

        custom_managers_count = len(custom_managers)
        
    return dict(custom_managers=_format_api_custom_managers(custom_managers), custom_managers_count=custom_managers_count)


@common_ajax_response_for_api
def api_get_custom_manager_list_of_department(request):
    department = db.get_department_by_id(request.REQUEST.get('department_id'))
    if not department:
        raise Http404
    custom_managers = cmb.get_customer_managers_by_department(department)
    custom_managers = cmb.format_customer_managers_for_ajax(custom_managers)
    custom_managers_count = len(custom_managers)

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
