# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
                       url(r'^$', 'home'),
                       url(r'^question$', 'question'),
                       url(r'^important_question$', 'important_question'),
                       url(r'^suggest_user$', 'suggest_user'),
                       )
