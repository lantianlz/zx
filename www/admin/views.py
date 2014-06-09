# -*- coding: utf-8 -*-

import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import verify_permission

from common import utils, page


@verify_permission('')
def home(request):
    return HttpResponseRedirect('/admin/question/important_question')


# def question(request, template_name='admin/question.html'):
#     return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# def important_question(request, template_name='admin/important_question.html'):
#     return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# def suggest_user(request, template_name='admin/suggest_user.html'):
#     return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# def topic(request, template_name='admin/topic.html'):
#     return render_to_response(template_name, locals(), context_instance=RequestContext(request))
