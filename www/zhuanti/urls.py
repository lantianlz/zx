# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.zhuanti.views',
                       url(r'^$', 'index'),
                       url(r'^(?P<zhuanti_domain>\w+)$', 'zhuanti_detail'),
                       )
