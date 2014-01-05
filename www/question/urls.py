# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.question.views',
                       url(r'^$', 'question_home'),
                       url(r'^type/(?P<type>\w+)$', 'question_home'),
                       url(r'^question_detail/?$', 'question_detail'),
                       url(r'^ask_question/?$', 'ask_question'),
                       )
