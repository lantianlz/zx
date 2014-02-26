# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
                       url(r'^$', 'www.message.views.system_message'),
                       url(r'^received_like/?$', 'www.message.views.received_like'),
                       url(r'^received_answer/?$', 'www.message.views.received_answer'),
                       url(r'^at_answer/?$', 'www.message.views.at_answer'),

                       )
