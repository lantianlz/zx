# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('',
	url(r'^oauth/qq$', 'www.account.views_oauth.oauth_qq'),
	url(r'^oauth/weibo$', 'www.account.views_oauth.oauth_weibo'),
	url(r'^user_profile$', 'www.account.views.user_profile'),
	url(r'^user_settings$', 'www.account.views.user_settings'),
	url(r'^user_settings/change_pwd$', 'www.account.views.change_pwd'),
	url(r'^user_settings/change_email$', 'www.account.views.change_email'),
	url(r'^user_settings/bind_mobile$', 'www.account.views.bind_mobile'),
	url(r'^user_settings/security_question$', 'www.account.views.security_question'),
	url(r'^user_settings/bind_community$', 'www.account.views.bind_community'),
)
