# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.stock.views',
                       url(r'^$', 'stock_home'),
                       url(r'^my_stock_feeds$', 'my_stock_feeds'),
                       url(r'^all$', 'stock_all'),
                       url(r'^(?P<stock_code>\d+)$', 'stock_detail'),
                       url(r'^feed/(?P<stock_feed_id>\d+)$', 'stock_feed'),
                       url(r'^search$', 'stock_search'),
                       url(r'^my_stocks$', 'my_stocks'),

                       url(r'^follow/(?P<stock_id>\d+)$', 'follow_stock'),
                       url(r'^unfollow/(?P<stock_id>\d+)$', 'unfollow_stock'),
                       url(r'^get_stock_info_by_id$', 'get_stock_info_by_id'),

                       url(r'^chart_stock$', 'chart_stock'),
                       url(r'^chart_industry$', 'chart_industry'),
                       url(r'^chart_industry/(?P<industry_id>\d+)$', 'chart_industry_detail'),

                       # 个股前十
                       url(r'^get_stock_chain_data$', 'get_stock_chain_data'),
                       url(r'^get_stock_chain_in_total_data$', 'get_stock_chain_in_total_data'),

                       # 个股历史
                       url(r'^get_stock_history_chain_data$', 'get_stock_history_chain_data'),
                       )
