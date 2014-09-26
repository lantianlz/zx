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
                        "tel": department.tel, "addr": department.addr})
    return results


@common_ajax_response_for_api
def api_get_department_list(request, template_name='kaihu/department_list.html'):
    city = cb.get_city_by_pinyin_abbr("chengdu")
    if not city:
        raise Http404
    departments = db.get_departments_by_city_id(city.id)
    # departments_count = len(departments)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(departments, count=10, page=page_num).info
    departments = page_objs[0]
    return dict(departments=_format_api_departments(departments))
