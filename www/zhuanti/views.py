# -*- coding: utf-8 -*-

import json
# import urllib
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.misc.decorators import member_required


def index(request, template_name='zhuanti/zhuanti_list.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def zhuanti_detail(request, zhuanti_domain, template_name='zhuanti/zhuanti_detail.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
