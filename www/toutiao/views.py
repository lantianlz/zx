# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page, utils
from www.toutiao import interface

ab = interface.ArticleBase()


def toutiao_list(request, article_type=None, template_name='toutiao/toutiao_list.html'):
    if not article_type:
        articles = ab.get_all_articles()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def toutiao_detail(request, toutiao_id=None, template_name='toutiao/toutiao_detail.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
