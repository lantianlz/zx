# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.question.views',
                       url(r'^$', 'question_home'),
                       url(r'^type/(?P<question_type>\w+)$', 'question_home'),
                       url(r'^question_detail/(?P<question_id>\w+)$', 'question_detail'),
                       url(r'^ask_question$', 'ask_question'),
                       url(r'^create_answer/(?P<question_id>\w+)$', 'create_answer'),
                       url(r'^get_tags$', 'get_tags'),
                       url(r'^get_tags_by_question_type$', 'get_tags_by_question_type'),
                       url(r'^like_answer$', 'like_answer')
                       )
