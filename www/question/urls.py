# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.question.views',
                       url(r'^$', 'question_home'),
                       url(r'^(?P<question_id>\d+)$', 'question_detail'),
                       # url(r'^question_detail/(?P<question_id>\w+)$', 'question_detail'),
                       url(r'^type/(?P<question_type>\w+)$', 'question_home'),
                       url(r'^topic/(?P<tag_domain>\w+)$', 'topic_question'),
                       url(r'^topics', 'topics'),
                       url(r'^get_topic_info_by_id', 'get_topic_info_by_id'),
                       url(r'^ask_question$', 'ask_question'),
                       url(r'^modify_question/(?P<question_id>\w+)$', 'modify_question'),

                       url(r'^create_answer/(?P<question_id>\w+)$', 'create_answer'),
                       url(r'^modify_answer$', 'modify_answer'),
                       url(r'^like_answer$', 'like_answer'),
                       url(r'^remove_answer$', 'remove_answer'),
                       url(r'^remove_question$', 'remove_question'),

                       url(r'^important$', 'important_question'),
                       url(r'^set_important$', 'set_important'),
                       url(r'^cachel_important$', 'cachel_important'),
                       url(r'^set_answer_bad$', 'set_answer_bad'),
                       url(r'^cancel_answer_bad$', 'cancel_answer_bad'),
                       )
