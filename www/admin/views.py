# -*- coding: utf-8 -*-

import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page


def home(request, template_name='admin/home.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))