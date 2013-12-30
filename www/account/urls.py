# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('',
                       url(r'^oauth/qq$', 'www.account.views_oauth.oauth_qq'),
                       url(r'^oauth/weibo$', 'www.account.views_oauth.oauth_weibo'),
                       )
