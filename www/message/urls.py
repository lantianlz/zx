# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$', 'www.message.views.system_message'),
                       url(r'^received_like/?$', 'www.message.views.received_like'),
                       url(r'^received_answer/?$', 'www.message.views.received_answer'),
                       url(r'^at_answer/?$', 'www.message.views.at_answer'),
                       url(r'^get_unread_count_total/?$', 'www.message.views.get_unread_count_total'),
                       url(r'^share_received_like/?$', 'www.message.views.share_received_like'),
                       url(r'^show_received_like/?$', 'www.message.views.show_received_like'),
                       )
