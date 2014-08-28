# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.toutiao.views',
                       url(r'^$', 'toutiao_list'),
                       url(r'^type/(?P<article_type>\w+)$', 'toutiao_list'),
                       url(r'^article/(?P<article_id>\d+)$', 'toutiao_detail'),
                       )
