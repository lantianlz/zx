# -*- coding: utf-8 -*-

import json, datetime

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
    stock_feeds = sfb.get_all_stock_feeds()[:500]

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(stock_feeds, count=10, page=page_num).info
    stock_feeds = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    stock_feeds = sfb.format_stock_feeds(stock_feeds)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def my_stock_feeds(request, template_name='stock/stock_home.html'):
    stock_feeds = sfb.get_stock_feeds_by_user_id(request.user.id)[:100]

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
    is_follow = sfollowb.check_is_follow(stock, request.user.id) if request.user.is_authenticated else False

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


@member_required
def my_stocks(request, template_name='stock/my_stocks.html'):
    stock_follows = sfollowb.get_stock_follows_by_user_id(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(stock_follows, count=20, page=page_num).info
    stock_follows = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    stocks = [sf.stock for sf in stock_follows]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def chart_stock(request, template_name='chart/chart_stock.html'):
    today = str(datetime.datetime.now())[:10]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def chart_industry(request, template_name='chart/chart_industry.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def chart_industry_detail(request, industry_id, template_name='chart/chart_industry_detail.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
# ===================================================ajax部分=================================================================#

@member_required
@common_ajax_response
def follow_stock(request, stock_id):
    return sfollowb.follow_stock(stock_id, request.user.id)


@member_required
@common_ajax_response
def unfollow_stock(request, stock_id):
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
                "is_following": sfollowb.check_is_follow(stock_id, request.user.id)
            }
    return HttpResponse(json.dumps(infos), mimetype='application/json')


def get_stock_chain_data(request):
    date = request.REQUEST.get('date', str(datetime.datetime.now())[:10])
    
    market_value = request.REQUEST.get('market_value', '1')
    market_value_dict = {
        '0': [0, 999999],
        '1': [0, 50],
        '2': [50, 100],
        '3': [100, 200],
        '4': [200, 300],
        '5': [300, 999999]
    }

    x_data = []
    y_data = []

    for x in interface.StockDataBase().get_stock_chain_data(date, market_value_dict[market_value]):
        x_data.append('%s(%s)' % (x.stock.name, x.stock.code))
        y_data.append(round(x.turnover_change_pre_day, 2))
    
    x_data.reverse()
    y_data.reverse()

    data = {
        'x_data': x_data,
        'y_data': y_data
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')


def get_stock_chain_in_total_data(request):
    date = request.REQUEST.get('date', str(datetime.datetime.now())[:10])

    market_value = request.REQUEST.get('market_value', '1')
    market_value_dict = {
        '0': [0, 999999],
        '1': [0, 50],
        '2': [50, 100],
        '3': [100, 200],
        '4': [200, 300],
        '5': [300, 999999]
    }

    x_data = []
    y_data = []

    for x in interface.StockDataBase().get_stock_chain_in_total_data(date, market_value_dict[market_value]):
        x_data.append('%s(%s)' % (x.stock.name, x.stock.code))
        y_data.append(round(x.turnover_rate_to_all_change_per_day, 2))
    
    x_data.reverse()
    y_data.reverse()

    data = {
        'x_data': x_data,
        'y_data': y_data
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')


def get_stock_history_chain_data(request):

    stock_id = request.REQUEST.get('stock_id')

    x_data = []
    y_data = []
    y_data2 = []

    for x in interface.StockDataBase().get_stock_history_chain_data(stock_id):
        x_data.append(str(x.date)[:10])
        y_data.append(round(x.turnover_change_pre_day, 2))
        y_data2.append(round(x.turnover_rate_to_all_change_per_day, 2))
    
    x_data.reverse()
    y_data.reverse()
    y_data2.reverse()

    data = {
        'x_data': x_data,
        'y_data': y_data,
        'y_data2': y_data2,
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')
