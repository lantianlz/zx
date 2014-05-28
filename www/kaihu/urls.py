# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.kaihu.views',
                       url(r'^$', 'home'),
                       url(r'^department_detail/(?P<department_id>\d+)$', 'department_detail'),
                       url(r'^get_customer_manager$', 'get_customer_manager'),


                       url(r'^(?P<city_abbr>\w+)$', 'department_list'),  # 此处必须放到最后，避免被误匹配
                       )
