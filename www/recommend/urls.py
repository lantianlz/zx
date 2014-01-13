# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('', 
	url(r'^$', 'www.recommend.views.recommend_home'),
	url(r'^recommend_detail/?$', 'www.recommend.views.recommend_detail'),
)
