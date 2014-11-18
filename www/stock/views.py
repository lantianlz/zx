# -*- coding: utf-8 -*-

import json

from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page
from www.misc.decorators import member_required, common_ajax_response
from www.stock import interface

sb = interface.StockBase()
sfb = interface.StockFeedBase()
sfollowb = interface.StockFollowBase()


def stock_home(request, template_name='stock/stock_home.html'):
    stock_feeds = sfb.get_all_stock_feeds()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(stock_feeds, count=10, page=page_num).info
    stock_feeds = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    stock_feeds = sfb.format_stock_feeds(stock_feeds)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_detail(request, stock_code, template_name='stock/stock_detail.html'):
    stock = sb.get_stock_by_code(stock_code)
    if not stock:
        raise Http404
    stock_feeds = sfb.get_stock_feeds_by_stock(stock)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(stock_feeds, count=10, page=page_num).info
    stock_feeds = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_feed(request, stock_feed_id, template_name='stock/stock_feed.html'):
    stock_feed = sfb.get_stock_feed_by_id(stock_feed_id)
    if not stock_feed:
        raise Http404

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_all(request, template_name='stock/stock_all.html'):
    stocks = sb.get_all_stocks()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(stocks, count=20, page=page_num).info
    stocks = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_search(request, template_name='stock/stock_search.html'):
    stock_key_words = request.REQUEST.get('key_words', '')
    stocks = sb.search_stocks(stock_key_words)[:20]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# ===================================================ajax部分=================================================================#

@member_required
@common_ajax_response
def follow_people(request, stock_id):
    return sfollowb.follow_stock(stock_id, request.user.id)


@member_required
@common_ajax_response
def unfollow_people(request, stock_id):
    return sfollowb.unfollow_stock(stock_id, request.user.id)


def get_stock_info_by_id(request):
    '''
    @note: 根据股票id获取名片信息
    '''
    stock_id = request.REQUEST.get('stock_id', '').strip()

    infos = {}
    if stock_id:
        stock = sb.get_stock_by_id(stock_id)
        if stock:
            infos = {
                "id": stock.id,
                "name": stock.name,
                "code": stock.code,
                "des": stock.des,
                "img": stock.img,
                "url": stock.get_url(),
                "feed_count": stock.feed_count,
                "following_count": stock.following_count,
                "is_following": False
            }
    return HttpResponse(json.dumps(infos), mimetype='application/json')
