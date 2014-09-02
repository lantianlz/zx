# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.toutiao.interface import BanKeyBase


@verify_permission('')
def bankey(request, template_name='admin/toutiao_bankey.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_toutiao_bankey')
@common_ajax_response
def add_bankey(request):
    key = request.REQUEST.get('key')
    return BanKeyBase().add_ban_key(key)


@verify_permission('remove_toutiao_bankey')
@common_ajax_response
def remove_bankey(request):
    benkey_id = request.REQUEST.get('benkey_id')
    return BanKeyBase().remove_bankey(benkey_id)


@verify_permission('query_toutiao_bankey')
def search(request):
    key = request.REQUEST.get('key')
    page_index = int(request.REQUEST.get('page_index'))

    page_objs = page.Cpt(BanKeyBase().get_all_bankeys(), count=10, page=page_index).info

    num = 10 * (page_index - 1)

    data = []
    for x in page_objs[0]:
        num += 1
        data.append({
            'num': num,
            'bankey_id': x.id,
            'key': x.key
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )
