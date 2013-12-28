# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response


def static_view(request, template_name):
    '''
    @note: 静态模板采用通用目录
    '''
    return render_to_response('static_templates/%s.html' % template_name, locals(), context_instance=RequestContext(request))
