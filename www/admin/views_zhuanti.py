# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.zhuanti.interface import ZhuantiBase


@verify_permission('')
def zhuanti(request, template_name='admin/zhuanti.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_zhuanti')
def add_zhuanti(request):
    title = request.REQUEST.get('title')
    summary = request.REQUEST.get('summary')
    author = request.REQUEST.get('author')
    domain = request.REQUEST.get('domain')
    sort_num = request.REQUEST.get('sort')

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='topic')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = ZhuantiBase().create_zhuanti(title, summary, img_name, domain, author, sort_num)

    if flag == 0:
        url = "/admin/zhuanti?#modify/%s" % (msg.id)
    else:
        url = "/admin/zhuanti?%s" % (msg)

    return HttpResponseRedirect(url)


def format_zhuanti(objs, num):
    data = []

    for x in objs:
        num += 1
        data.append({
            'num': num,
            'zhuanti_id': x.id,
            'title': x.title,
            'summary': x.summary,
            'img': x.img,
            'author_name': x.author_name,
            'domain': x.domain,
            'sort_num': x.sort_num,
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_zhuanti')
def search(request):
    data = []
    zb = ZhuantiBase()

    page_index = int(request.REQUEST.get('page_index'))

    page_objs = page.Cpt(zb.get_all_zhuantis(state=None), count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_zhuanti(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_zhuanti')
def get_zhuanti_by_id(request):
    zhuanti_id = request.REQUEST.get('zhuanti_id')
    zb = ZhuantiBase()

    obj = zb.get_zhuanti_by_id_or_domain(zhuanti_id)

    data = format_zhuanti([obj], 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_zhuanti')
@common_ajax_response
def remove_zhuanti(request):
    zhuanti_id = request.REQUEST.get('zhuanti_id')
    return ZhuantiBase().remove_zhuanti(zhuanti_id)


@verify_permission('modify_zhuanti')
def modify_zhuanti(request):
    zb = ZhuantiBase()

    zhuanti_id = request.REQUEST.get('zhuanti_id')

    obj = zb.get_zhuanti_by_id_or_domain(zhuanti_id)
    img_name = obj.img

    title = request.REQUEST.get('title')
    summary = request.REQUEST.get('summary')
    author = request.REQUEST.get('author')
    domain = request.REQUEST.get('domain')
    sort_num = request.REQUEST.get('sort')

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='topic')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = ZhuantiBase().modify_zhuanti(
        zhuanti_id, title=title, summary=summary, img=img_name,
        author_name=author, domain=domain, sort_num=sort_num
    )

    if flag == 0:
        url = "/admin/zhuanti?#modify/%s" % (obj.id)
    else:
        url = "/admin/zhuanti?%s#modify/%s" % (msg, obj.id)

    return HttpResponseRedirect(url)
