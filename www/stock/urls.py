# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.stock.views',
                       url(r'^$', 'stock_home'),
                       )
