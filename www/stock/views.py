# -*- coding: utf-8 -*-

# import json

from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page
from www.stock import interface
sb = interface.StockBase()
sfb = interface.StockFeedBase()


def stock_home(request, template_name='stock/stock_home.html'):
    stock_feeds = sfb.get_all_stock_feeds()

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(stock_feeds, count=100, page=page_num).info
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
    page_objs = page.Cpt(stock_feeds, count=100, page=page_num).info
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
    page_objs = page.Cpt(stocks, count=50, page=page_num).info
    stocks = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_search(request, template_name='stock/stock_search.html'):

    stock_key_words = request.REQUEST.get('key_words', '')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
