# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.stock.views',
                       url(r'^$', 'stock_home'),
                       url(r'^(?P<stock_id>\d+)$', 'stock_detail'),
                       url(r'^feed/(?P<feed_id>\d+)$', 'stock_feed'),
                       url(r'^search$', 'stock_search'),
                       )
