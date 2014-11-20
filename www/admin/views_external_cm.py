# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import ExternalCMBase


@verify_permission('')
def external_cm(request, template_name='admin/external_cm.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_external_cm(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'externalCM_id': x.id,
            'name': x.name,
            'city_name': x.city_name,
            'department_name': x.department_name,
            'href': x.href,
            'pay_type': x.pay_type,
            'qq': x.qq,
            'mobile': x.mobile,
            'note': x.note,
            'state': x.state
        })

    return data


@verify_permission('query_external_cm')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    city_name = request.REQUEST.get('city_name')
    department_name = request.REQUEST.get('department_name')
    state = request.REQUEST.get('state')
    qq = request.REQUEST.get('qq')
    page_index = int(request.REQUEST.get('page_index'))

    objs = ExternalCMBase().get_external_cm_for_admin(name, city_name, department_name, state, qq)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_external_cm(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('modify_external_cm')
@common_ajax_response
def save_state(request):
    external_cm_id = request.REQUEST.get('externalCM_id')
    note = request.REQUEST.get('note')
    state = request.REQUEST.get('state')
    return ExternalCMBase().save_state(external_cm_id, state, note)
