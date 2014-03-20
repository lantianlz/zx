# -*- coding: utf-8 -*-

import base64
import json
import time
import urllib

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.conf import settings

from www.misc.decorators import member_required
from www.misc import qiniu_client


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
    # print ur
    img_key = ur.get('key', '')
    img_type = ur.get('img_type', '')
    if img_key and img_type.startswith('avatar'):
        user = request.user
        user.avatar = '%s/%s' % (settings.IMG0_DOMAIN, img_key)
        user.save()

        # 上传完头像之后 跳转到设置页面时带上 需要裁剪参数
        return HttpResponseRedirect('/account/user_settings?crop_avatar=true')
    return HttpResponse('上传图片出错，请重新上传 <a href="javascript:history.go(-1);">立即返回</a>')


@member_required
def save_img(request):
    imgFile = request.FILES.get('imgFile')
    flag, img_name = qiniu_client.upload_img(imgFile)
    if flag:
        result = dict(error=0, url='%s/%s' % (settings.IMG0_DOMAIN, img_name))
    else:
        result = dict(error=-1, url='')

    return HttpResponse(json.dumps(result), mimetype='application/json')


@member_required
def crop_img(request):
    '''
    裁剪图片
    这里使用的是七牛的裁剪接口,具体参见 http://docs.qiniutek.com/v3/api/foimg/#imageMogr
    将剪裁坐标传递给七牛，七牛会返回按此参数剪裁后的图片回来，然后再将此图片作为用户头像上传给七牛
    '''
    result = {'success': True, 'msg': u''}

    def verify_int(target, r):
        '''
        验证参数合法性
        target: 要验证的值
        r: 范围
        '''
        if target and target.isdigit():
            if (r[0] <= int(target)) and (int(target) <= r[1]):
                return True

        return False

    x = request.REQUEST.get('x', None)
    y = request.REQUEST.get('y', None)
    w = request.REQUEST.get('w', None)
    h = request.REQUEST.get('h', None)
    print x, y, w, h
    if verify_int(x, [0, 300]) \
        and verify_int(y, [0, 300]) \
        and verify_int(w, [25, 300]) \
        and verify_int(h, [25, 300]):

        # 拼接给七牛的参数
        post_url = '%s?imageMogr/v2/auto-orient/crop/!%sx%sa%sa%s' % (request.user.avatar, w, h, x, y)
        
        # 上传图片
        flag, img_name = qiniu_client.upload_img(urllib.urlopen(post_url))
        if flag:
            url = '%s/%s' % (settings.IMG0_DOMAIN, img_name)
            # 将新的图片地址指向当前用户
            user = request.user
            user.avatar = url
            user.save()
        else:
            result = {'success': False, 'msg': u'剪裁失败, 请稍后重试'}
    else:
        result = {'success': False, 'msg': u'参数错误'}
    return HttpResponse(json.dumps(result))