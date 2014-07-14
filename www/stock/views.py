# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response


def stock_home(request, template_name='stock/stock_home.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
