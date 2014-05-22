# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.question.interface import QuestionBase


@verify_permission('')
def customer_manager(request, template_name='admin/customer_manager.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
