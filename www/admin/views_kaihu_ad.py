# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.kaihu.interface import AdBase, CityBase


@verify_permission('')
def ad(request, template_name='admin/kaihu_ad.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_article')
def add_ad(request):
    qq = request.REQUEST.get('qq')
    expire_time = request.REQUEST.get('expire_time')
    city_id = request.REQUEST.get('belong_city')

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='kaihu_ad')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = AdBase().add_ad(city_id, qq, expire_time, img_name)

    if flag == 0:
        url = "/admin/kaihu/ad?#modify/%s" % (msg.id)
    else:
        url = "/admin/kaihu/ad?%s" % (msg)

    return HttpResponseRedirect(url)



def format_ad(objs, num):
    data = []

    for x in objs:
        num += 1
        city = CityBase().get_city_by_id(x.city_id) if x.city_id else None

        data.append({
            'num': num,
            'ad_id': x.id,
            'city_id': city.id if city else '',
            'city_name': city.city if city else '',
            'city_pinyin_abbr': city.pinyin_abbr if city else '',
            'qq': x.qq,
            'img': x.img,
            'expire_time': str(x.expire_time)[:10],
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_article')
def search(request):
    data = []

    city_name = request.REQUEST.get('name')

    objs = AdBase().search_ads_for_admin(city_name)

    page_index = int(request.REQUEST.get('page_index'))

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_ad(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_article')
def get_ad_by_id(request):
    ad_id = request.REQUEST.get('ad_id')

    obj = AdBase().get_ad_by_id(ad_id)

    data = format_ad([obj], 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_article')
@common_ajax_response
def remove_ad(request):
    ad_id = request.REQUEST.get('ad_id')
    return AdBase().remove_ad(ad_id)


@verify_permission('modify_article')
def modify_ad(request):

    ad_id = request.REQUEST.get('ad_id')
    obj = AdBase().get_ad_by_id(ad_id)
    img_name = obj.img

    qq = request.REQUEST.get('qq')
    expire_time = request.REQUEST.get('expire_time')
    city_id = request.REQUEST.get('belong_city')

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='kaihu_ad')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = AdBase().modify_ad(ad_id, city_id, qq, expire_time, img_name)

    if flag == 0:
        url = "/admin/kaihu/ad?#modify/%s" % (obj.id)
    else:
        url = "/admin/kaihu/ad?%s#modify/%s" % (msg, obj.id)

    return HttpResponseRedirect(url)
