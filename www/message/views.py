# -*- coding: utf-8 -*-

# from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.misc.decorators import member_required


@member_required
def message_home(request, template_name='message/message_home.html'):
    #todo 更新最后活跃时间
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def message_detail(request, template_name='message/message_detail.html'):
    #todo 更新最后活跃时间
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def system_message(request, template_name='message/system_message.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def new_message(request, template_name='message/new_message.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))