# -*- coding: utf-8 -*-
import json
import logging

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def home(request, template_name='kaihu/department_list.html'):
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def department_detail(request, department_id, template_name='kaihu/department_detail.html'):
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))