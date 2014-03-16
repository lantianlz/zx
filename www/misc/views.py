# -*- coding: utf-8 -*-

import base64
import json
import time

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.conf import settings

from www.misc.decorators import member_required


def static_view(request, template_name):
    '''
    @note: 静态模板采用通用目录
    '''
    return render_to_response('static_templates/%s.html' % template_name, locals(), context_instance=RequestContext(request))


@member_required
def qiniu_img_return(request):
    '''
    @note: 七牛设置图片回调url
    '''
    upload_ret = base64.b64decode(request.GET.get('upload_ret', ''))
    try:
        ur = json.loads(upload_ret)
    except:
        ur = {}
    print ur
    img_key = ur.get('key', '')
    img_type = ur.get('img_type', '')
    if img_key and img_type.startswith('avatar'):
        user = request.user
        user.avatar = '%s/%s' % (settings.IMG0_DOMAIN, img_key)
        user.save()

        return HttpResponseRedirect('/account/user_settings')
    return HttpResponse('上传图片出错，请重新上传 <a href="javascript:history.go(-1);">立即返回</a>')


@member_required
def save_img(request):
    result = {
        "error": 0,
        "url": "http://www.baidu.com/img/bdlogo.gif"
    }
    return HttpResponse(json.dumps(result))