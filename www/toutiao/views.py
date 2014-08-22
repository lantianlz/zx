# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import page, utils
from www.timeline.interface import FeedBase


def toutiao_list(request, template_name='toutiao/toutiao_list.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def toutiao_detail(request, toutiao_id=None, template_name='toutiao/toutiao_detail.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
