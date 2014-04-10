# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.timeline.views',
                       url(r'^$', 'user_timeline'),
                       )
