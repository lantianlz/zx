# -*- coding: utf-8 -*-

import urllib
from pprint import pprint
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.account.interface import UserBase
from www.misc.decorators import member_required


#@member_required
def question_home(request, template_name='question/question_home.html'):
    #todo 更新最后活跃时间
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


#@member_required
def question_detail(request, template_name='question/question_detail.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def ask_question(request, template_name='question/ask_question.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))