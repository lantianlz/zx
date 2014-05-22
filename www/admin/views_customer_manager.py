# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import CityBase, DepartmentBase


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
