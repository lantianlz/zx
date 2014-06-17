# -*- coding: utf-8 -*-
import json
import logging

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page
from www.timeline.interface import FeedBase
from www.kaihu import interface

cb = interface.CityBase()
db = interface.DepartmentBase()
cmb = interface.CustomerManagerBase()
flb = interface.FriendlyLinkBase()


def home(request, template_name='kaihu/home.html'):
    areas = cb.get_all_areas()
    citys_by_area = cb.get_all_city_group_by_province()
    flinks = flb.get_friendly_link_by_link_type(link_type=1)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def department_list(request, city_abbr, template_name='kaihu/department_list.html'):
    city = cb.get_city_by_pinyin_abbr(city_abbr)
    if not city:
        raise Http404
    departments = db.get_departments_by_city_id(city.id)
    departments_count = len(departments)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(departments, count=10, page=page_num).info
    departments = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    customer_managers = cmb.get_customer_managers_by_city_id(city.id)
    customer_manager_user_ids = [cm['user_id'] for cm in customer_managers]
    customer_managers = customer_managers[:4]

    if not request.REQUEST.has_key('page'):
        flinks = flb.get_friendly_link_by_city_id(city.id)

    fb = FeedBase()
    feeds = fb.format_feeds_by_id(fb.get_feed_ids_by_feed_type(feed_type=3, user_ids=customer_manager_user_ids)[:5])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def department_detail(request, department_id, template_name='kaihu/department_detail.html'):
    department = db.get_department_by_id(department_id)
    if not department:
        raise Http404

    customer_managers = cmb.format_customer_managers_for_ajax(cmb.get_customer_managers_by_department(department))

    customer_manager_user_ids = [cm['user_id'] for cm in customer_managers]
    fb = FeedBase()
    feeds = fb.format_feeds_by_id(fb.get_feed_ids_by_feed_type(feed_type=3, user_ids=customer_manager_user_ids)[:20])
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# ===================================================ajax部分=================================================================#

def get_customer_manager(request):
    '''
    @note: 获取更多的推荐客户经理
    '''
    city_id = request.REQUEST.get('city_id', '')
    page_num = int(request.REQUEST.get('page', 1))
    page_count = 4

    customer_managers = cmb.get_customer_managers_by_city_id(city_id)[(page_num - 1) * page_count:page_num * page_count]

    return HttpResponse(json.dumps(customer_managers), mimetype='application/json')
