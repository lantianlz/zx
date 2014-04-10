# -*- coding: utf-8 -*-

import urllib
import json
import hashlib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.misc import qiniu_client
from www.account import interface
from www.misc.decorators import member_required

@member_required
def user_timeline(request):
    return render_to_response('timeline/user_timeline.html', locals(), context_instance=RequestContext(request))
