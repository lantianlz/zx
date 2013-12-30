# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('', 
	url(r'^$', 'www.question.views.question_home'),
	url(r'^question_detail/?$', 'www.question.views.question_detail'),
	url(r'^ask_question/?$', 'www.question.views.ask_question'),
)
