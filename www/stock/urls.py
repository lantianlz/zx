# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.stock.views',
                       url(r'^$', 'stock_home'),
                       url(r'^all$', 'stock_all'),
                       url(r'^(?P<stock_code>\d+)$', 'stock_detail'),
                       url(r'^feed/(?P<stock_feed_id>\d+)$', 'stock_feed'),
                       url(r'^search$', 'stock_search'),
                       )
