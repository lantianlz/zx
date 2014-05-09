# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'www.account.views.show_index'),
                       url(r'^home$', 'www.account.views.show_index'),
                       url(r'^login$', 'www.account.views.login'),
                       url(r'^logout$', 'www.account.views.logout'),
                       url(r'^regist$', 'www.account.views.regist'),
                       url(r'^regist/(?P<invitation_code>\w+)$', 'www.account.views.regist'),
                       url(r'^reset_password$', 'www.account.views.reset_password'),
                       url(r'^forget_password$', 'www.account.views.forget_password'),
                       url(r'^qiniu_img_return$', 'www.misc.views.qiniu_img_return'),
                       url(r'^save_img$', 'www.misc.views.save_img'),
                       url(r'^crop_img$', 'www.misc.views.crop_img'),

                       url(r'^n/(?P<nick>.*)$', 'www.account.views.get_user_by_nick'),
                       url(r'^p/(?P<user_id>\w+)/?$', 'www.account.views.user_questions'),
                       url(r'^p/(?P<user_id>\w+)/questions/?$', 'www.account.views.user_questions'),
                       url(r'^p/(?P<user_id>\w+)/answers/?$', 'www.account.views.user_answers'),
                       url(r'^p/(?P<user_id>\w+)/following/?$', 'www.account.views.user_following'),
                       url(r'^p/(?P<user_id>\w+)/followers/?$', 'www.account.views.user_followers'),
                       url(r'^s/(?P<template_name>.*)$', 'www.misc.views.static_view'),

                       url(r'^account/', include('account.urls')),
                       url(r'^question/', include('question.urls')),
                       url(r'^message/', include('message.urls')),
                       url(r'^timeline/', include('timeline.urls')),
                       # url(r'^recommend/', include('recommend.urls')),

                       url(r'^admin/', include('admin.urls')),
                       url(r'^500$', 'www.account.views.test500'),
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
                       )
