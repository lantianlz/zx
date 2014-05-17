# -*- coding: utf-8 -*-

import json
import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response

from www.account.interface import RecommendUserBase, UserBase, UserCountBase


@staff_required
def topic(request, template_name='admin/topic.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@staff_required
def search(request):
    topic_name = request.POST.get('topic_name')
    page_index = request.POST.get('page_index', 1)
    data = []
    return HttpResponse(json.dumps(data), mimetype='application/json')
