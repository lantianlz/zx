# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response

from www.account.interface import RecommendUserBase


@staff_required
def important_question(request, template_name='admin/important_question.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
