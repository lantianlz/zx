# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'www.account.views.show_index'),
                       url(r'^login$', 'www.account.views.login'),
                       url(r'^logout$', 'www.account.views.logout'),
                       url(r'^regist$', 'www.account.views.regist'),
                       url(r'^reset_password$', 'www.account.views.reset_password'),
                       url(r'^forget_password$', 'www.account.views.forget_password'),
                       url(r'^home$', 'www.question.views.question_home'),
                       url(r'^n/(?P<nick>.*)$', 'www.account.views.get_user_by_nick'),
                       url(r'^account/', include('account.urls')),
                       url(r'^question/', include('question.urls')),
                       url(r'^recommend/', include('recommend.urls')),
                       url(r'^message/', include('message.urls')),
                       url(r'^admin/', include('admin.urls')),

                       url(r'^500$', 'www.account.views.test500'),
                       url(r'^s/(?P<template_name>.*)$', 'www.misc.views.static_view'),
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                       )
