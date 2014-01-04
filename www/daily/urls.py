# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('', 
	url(r'^$', 'www.daily.views.daily_home'),
	url(r'^daily_detail/?$', 'www.daily.views.daily_detail'),
)
