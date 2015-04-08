# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.stock.interface import KindBase


@verify_permission('')
def kind(request, template_name='admin/stock_kind.html'):
    from www.stock.models import Kind
    choices = [{'value': x[0], 'name': x[1]} for x in Kind.group_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_kind(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'kind_id': x.id,
            'name': x.name,
            'group': x.group,
            'sort': x.sort_num,
            'stocks': [{'stock_id': k.stock.id, 'stock_name': k.stock.name} for k in x.stocks.all()],
            'stocks_count': x.stocks.count()
        })

    return data


@verify_permission('query_kind')
def search(request):
    data = []

    name = request.REQUEST.get('name')

    page_index = int(request.REQUEST.get('page_index'))

    objs = KindBase().search_kind_for_admin(name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_kind(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_kind')
def get_kind_by_id(request):
    kind_id = request.REQUEST.get('kind_id')

    data = format_kind([KindBase().get_kind_by_id(kind_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_kind')
@common_ajax_response
def modify_kind(request):
    kind_id = request.REQUEST.get('kind_id')
    name = request.REQUEST.get('name')
    stocks = request.REQUEST.get('stocks')
    stocks = stocks.split(',')
    group = request.REQUEST.get('group')
    sort = request.REQUEST.get('sort')

    return KindBase().modify_kind(
        kind_id, name, stocks, group, sort
    )

@verify_permission('remove_kind')
@common_ajax_response
def remove_kind(request):
    kind_id = request.REQUEST.get('kind_id')

    return KindBase().remove_kind(kind_id)


@verify_permission('add_kind')
@common_ajax_response
def add_kind(request):

    name = request.REQUEST.get('name')
    stocks = request.REQUEST.get('stocks')
    stocks = stocks.split(',')
    group = request.REQUEST.get('group')
    sort = request.REQUEST.get('sort')

    code, msg = KindBase().add_kind(name, stocks, group, sort)
    return code, msg if code else msg.id