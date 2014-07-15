# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response


def stock_home(request, template_name='stock/stock_home.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_detail(request, stock_id, template_name='stock/stock_detail.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_feed(request, feed_id, template_name='stock/stock_feed.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_list(request, template_name='stock/stock_list.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def stock_search(request, template_name='stock/stock_search.html'):

    stock_key_words = request.REQUEST.get('key_words', '')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
