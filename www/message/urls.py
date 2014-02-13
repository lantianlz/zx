# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('', 
	url(r'^$', 'www.message.views.message_home'),
	url(r'^new_message/?$', 'www.message.views.new_message'),
	url(r'^system_message/?$', 'www.message.views.system_message'),
	url(r'^message_detail/?$', 'www.message.views.message_detail'),
)
