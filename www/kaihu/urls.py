# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.kaihu.views',
	url(r'^$', 'home'),
	url(r'^(?P<department_id>\d+)$', 'department_detail'),
)