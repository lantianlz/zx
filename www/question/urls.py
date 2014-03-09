# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.question.views',
                       url(r'^$', 'question_home'),
                       url(r'^type/(?P<question_type>\w+)$', 'question_home'),
                       url(r'^tag/(?P<tag_domain>\w+)$', 'tag_question'),
                       url(r'^question_detail/(?P<question_id>\w+)$', 'question_detail'),
                       url(r'^ask_question$', 'ask_question'),
                       url(r'^modify_question/(?P<question_id>\w+)$', 'modify_question'),

                       url(r'^create_answer/(?P<question_id>\w+)$', 'create_answer'),
                       url(r'^like_answer$', 'like_answer'),
                       url(r'^remove_answer$', 'remove_answer'),

                       url(r'^important$', 'important_question'),
                       )
