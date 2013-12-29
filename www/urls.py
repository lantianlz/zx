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
                       url(r'^home$', 'www.account.views.home'),
                       url(r'^question_detail', 'www.account.views.question_detail'),
                       url(r'^user_profile', 'www.account.views.user_profile'),
                       # Examples:
                       # url(r'^$', 'www.views.home', name='home'),
                       # url(r'^www/', include('www.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),

                       url(r'^s/(?P<template_name>.*)$', 'www.misc.views.static_view'),
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                       )
