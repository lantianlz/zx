# -*- coding: utf-8 -*-

# from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.misc.decorators import member_required


@member_required
def system_message(request, template_name='message/system_message.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def received_like(request, template_name='message/received_like.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def received_answer(request, template_name='message/received_answer.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def at_answer(request, template_name='message/at_answer.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
