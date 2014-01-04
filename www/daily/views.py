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
def daily_home(request, template_name='daily/daily_home.html'):
    #todo 更新最后活跃时间
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


#@member_required
def daily_detail(request, template_name='daily/daily_detail.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


