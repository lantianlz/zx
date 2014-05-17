# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.kaihu.views',
                       url(r'^$', 'home'),
                       url(r'^department_list/(?P<area_id>\d+)$', 'department_list'),
                       url(r'^department_detail/(?P<department_id>\d+)$', 'department_detail'),
                       )
