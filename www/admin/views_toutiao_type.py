# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.toutiao.interface import ArticleTypeBase


@verify_permission('')
def toutiao_type(request, template_name='admin/toutiao_type.html'):
    # from www.kaihu.models import FriendlyLink
    # link_types = [{'value': x[0], 'name': x[1]} for x in FriendlyLink.link_type_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_toutiao_type')
@common_ajax_response
def add_type(request):
    name = request.REQUEST.get('name')
    domain = request.REQUEST.get('domain')
    sort_num = request.REQUEST.get('sort_num')

    code, msg = ArticleTypeBase().add_article_type(name, domain, sort_num)

    return code, msg if code else msg.id


def format_type(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'type_id': x.id,
            'name': x.name,
            'domain': x.domain,
            'sort_num': x.sort_num,
            'state': x.state
        })

    return data


@verify_permission('query_toutiao_type')
def search(request):
    data = []

    data = format_type(ArticleTypeBase().get_article_types(), 0)

    return HttpResponse(
        json.dumps({'data': data}),
        mimetype='application/json'
    )


@verify_permission('query_toutiao_type')
def get_type_by_id(request):
    type_id = request.REQUEST.get('type_id')

    data = format_type([ArticleTypeBase().get_type_by_id(type_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_toutiao_type')
@common_ajax_response
def modify_type(request):
    type_id = request.REQUEST.get('type_id')
    name = request.REQUEST.get('name')
    domain = request.REQUEST.get('domain')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False
    sort_num = int(request.REQUEST.get('sort_num'))

    return ArticleTypeBase().modify_article_type(
        type_id, name=name, sort_num=sort_num, domain=domain, state=state
    )
