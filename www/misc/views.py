# -*- coding: utf-8 -*-

import base64
import json
import urllib
import os

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.conf import settings

from common import utils, debug
from www.misc.decorators import member_required
from www.misc import qiniu_client


def static_view(request, template_name):
    '''
    @note: 静态模板采用通用目录
    '''
    file_name = os.path.abspath(os.path.join(settings.SITE_ROOT, './templates/static_templates/%s.html' % template_name))
    if not os.path.exists(file_name):
        raise Http404

    return render_to_response('static_templates/%s.html' % template_name, locals(), context_instance=RequestContext(request))


def txt_view(request, txt_file_name):
    '''
    @note: txt文件展示，主要是提供给搜索引擎
    '''
    file_name = os.path.abspath(os.path.join(settings.SITE_ROOT, '../static_local/%s.txt' % txt_file_name))
    if not os.path.exists(file_name):
        raise Http404
    return HttpResponse(open(file_name))


def sitemap(request):
    '''
    @note: site文件动态提供
    '''
    from www.misc.interface import generate_sitemap
    return HttpResponse(generate_sitemap(), mimetype='application/xml')


def baidu_map(request, template_name="other/baidu_map.html"):
    '''
    @note: 网站地图，给百度准备
    '''
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def link_view(request):
    '''
    @note: 交换友链等验证链接
    '''
    return HttpResponse('ok')


def friendly_links(request, template_name="static_templates/links.html"):
    '''
    @note: 全站友情链接
    '''
    from www.kaihu.interface import FriendlyLinkBase
    flinks = FriendlyLinkBase().get_friendly_link_by_link_type(link_type=2)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def qiniu_img_return(request):
    '''
    @note: 七牛设置图片回调url
    '''
    from www.account.interface import UserBase

    upload_ret = base64.b64decode(request.GET.get('upload_ret', ''))
    try:
        ur = json.loads(upload_ret)
    except:
        ur = {}
    img_key = ur.get('key', '')
    img_type = ur.get('img_type', '')
    if img_key and img_type.startswith('avatar'):
        user = request.user
        user.avatar = '%s/%s' % (settings.IMG0_DOMAIN, img_key)
        user.save()

        # 更新缓存
        UserBase().get_user_by_id(user.id, must_update_cache=True)

        # 上传完头像之后 跳转到设置页面时带上 需要裁剪参数
        return HttpResponseRedirect('/account/user_settings?crop_avatar=true')
    return HttpResponse('上传图片出错，请重新上传 <a href="javascript:history.go(-1);">立即返回</a>')


@member_required
def save_img(request):
    imgFile = request.FILES.get('imgFile')
    flag = False

    try:
        flag, img_name = qiniu_client.upload_img(imgFile, img_type='editor')
    except Exception, e:
        debug.get_debug_detail(e)

    if flag:
        result = dict(error=0, url='%s/%s' % (settings.IMG0_DOMAIN, img_name))
    else:
        result = dict(error=1, message='系统错误，请确认上传的文件格式为图片')

    return HttpResponse(json.dumps(result))


@member_required
def crop_img(request):
    '''
    裁剪图片
    这里使用的是七牛的裁剪接口,具体参见 http://docs.qiniutek.com/v3/api/foimg/#imageMogr
    将剪裁坐标传递给七牛，七牛会返回按此参数剪裁后的图片回来，然后再将此图片作为用户头像上传给七牛
    '''
    from www.account.interface import UserBase

    def _verfiy_int(target, r):
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
    result = dict(flag='-1', result=u'参数错误')
    if all((_verfiy_int(x, [0, 300]), _verfiy_int(y, [0, 300]), _verfiy_int(w, [25, 300]), _verfiy_int(h, [25, 300]))):
        img_name_original = request.user.avatar.rsplit('/', 1)[1]
        # 剪切不支持缩略图，修改成重新获取一次图片
        flag, img_name_450 = qiniu_client.upload_img(urllib.urlopen(request.user.get_avatar_450()))
        if flag:
            # 拼接给七牛的参数
            post_url = '%s/%s?imageMogr2/crop/!%sx%sa%sa%s' % (settings.IMG0_DOMAIN, img_name_450, w, h, x, y)

            # 上传图片
            flag, img_name = qiniu_client.upload_img(urllib.urlopen(post_url), img_type='newest_avatar')
            if flag:
                url = '%s/%s' % (settings.IMG0_DOMAIN, img_name)
                # 将新的图片地址指向当前用户
                user = request.user
                user.avatar = url
                user.save()

                # 更新缓存
                UserBase().get_user_by_id(user.id, must_update_cache=True)
                result = dict(flag='0', result=u'ok')

                # 删除多余的两张图片节省空间
                qiniu_client.batch_delete([img_name_original, img_name_450])
            else:
                result = dict(flag='-1', result=u'剪裁失败, 请稍后重试')

    return HttpResponse(json.dumps(result), mimetype='application/json')


def show_index_for_all_domain(request):
    from www.account.views import show_index
    from www.kaihu.views import department_list, home as kaihu_home

    # 通配符域名的情况下，跳转到不同的views
    sub_domain = utils.get_sub_domain_from_http_host(request.META.get('HTTP_HOST', ''))
    if sub_domain and sub_domain not in ("127", "192"):
        if sub_domain == 'kaihu':
            return kaihu_home(request)
        if sub_domain not in ('www', ):
            return department_list(request, city_abbr=sub_domain)

    return show_index(request)
