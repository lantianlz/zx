# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.stock.interface import StockBase


@verify_permission('')
def stock(request, template_name='admin/stock.html'):
    from www.stock.models import Stock
    boards = [{'value': x[0], 'name': x[1]} for x in Stock.board_choices]
    markets = [{'value': x[0], 'name': x[1]} for x in Stock.market_choices]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('add_stock')
def add_stock(request):
    name = request.REQUEST.get('name')
    code = request.REQUEST.get('code')
    des = request.REQUEST.get('des')
    belong_board = request.REQUEST.get('board')
    belong_market = request.REQUEST.get('market')
    sort_num = request.REQUEST.get('sort')
    state = request.REQUEST.get('state', '0')
    state = False if state == '0' else True

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='stock')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = StockBase().create_stock(name, code, belong_board, belong_market, img_name, des, sort_num, state)

    if flag == 0:
        url = "/admin/stock/stock?#modify/%s" % (msg.id)
    else:
        url = "/admin/stock/stock?%s" % (msg)

    return HttpResponseRedirect(url)


def format_stock(objs, num):
    data = []

    for x in objs:
        num += 1
        data.append({
            'num': num,
            'stock_id': x.id,
            'name': x.name,
            'code': x.code,
            'des': x.des,
            'belong_board': x.belong_board,
            'belong_market': x.belong_market,
            'img': x.img,
            'feed_count': x.feed_count,
            'following_count': x.following_count,
            'sort': x.sort_num,
            'state': x.state
        })

    return data


@verify_permission('query_stock')
def search(request):
    data = []
    sb = StockBase()
    fls = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = sb.get_stocks_by_name(name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_stock(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_friendly_link')
def get_friendly_link_by_id(request):
    link_id = request.REQUEST.get('link_id')
    flb = FriendlyLinkBase()

    obj = flb.get_friendly_link_by_id(link_id, state=None)

    data = format_friendly_link(flb.format_friendly_links(obj), 1)[0]
    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('remove_friendly_link')
@common_ajax_response
def remove_friendly_link(request):
    link_id = request.REQUEST.get('link_id')
    return FriendlyLinkBase().remove_friendly_link(link_id)


@verify_permission('modify_friendly_link')
@common_ajax_response
def modify_friendly_link(request):
    link_id = request.REQUEST.get('link_id')
    link_type = request.REQUEST.get('link_type', 0)
    city_id = request.REQUEST.get('belong_city')
    if not city_id:
        city_id = None

    name = request.REQUEST.get('name')
    href = request.REQUEST.get('href')
    sort_num = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')

    return FriendlyLinkBase().modify_friendly_link(
        link_id, link_type=link_type, city_id=city_id, name=name, href=href, sort_num=sort_num, des=des
    )
