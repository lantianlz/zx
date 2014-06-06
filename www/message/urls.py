# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns('www.message.views',
                       url(r'^$', 'system_message'),
                       url(r'^received_like/?$', 'received_like'),
                       url(r'^received_answer/?$', 'received_answer'),
                       url(r'^at_answer/?$', 'at_answer'),
                       url(r'^invite_answer/?$', 'invite_answer'),
                       url(r'^share_received_like/?$', 'share_received_like'),
                       url(r'^show_received_like/?$', 'show_received_like'),

                       url(r'^get_unread_count_total/?$', 'get_unread_count_total'),
                       url(r'^show_invite_user$', 'show_invite_user'),
                       url(r'^invite_user_answer$', 'invite_user_answer'),
                       url(r'^get_all_valid_global_notice$', 'get_all_valid_global_notice'),
                       )
