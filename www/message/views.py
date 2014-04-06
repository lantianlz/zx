# -*- coding: utf-8 -*-
import json
import logging

from django.http import HttpResponse  # , HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page, debug
from www.misc import qiniu_client
from www.misc.decorators import member_required
from www.tasks import async_clear_count_info_by_code
from www.account import interface as interface_account
from www.question import interface as interface_question
from www.message import interface


urb = interface.UnreadCountBase()
lb = interface_question.LikeBase()
ab = interface_question.AnswerBase()
ub = interface_account.UserBase()


@member_required
def system_message(request, template_name='message/system_message.html'):
    system_messages = urb.get_system_message(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(system_messages, count=10, page=page_num).info
    system_messages = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='system_message')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def received_like(request, template_name='message/received_like_m.html'):

    likes = lb.get_to_user_likes(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(likes, count=10, page=page_num).info
    likes = page_objs[0]
    page_params = (page_objs[1], page_objs[4])
    likes = lb.format_likes(likes)
    likes_count = page_objs[5]

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='received_like')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def received_answer(request, template_name='message/received_answer.html'):
    answers = ab.get_user_received_answer(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(answers, count=10, page=page_num).info
    answers = page_objs[0]
    page_params = (page_objs[1], page_objs[4])
    answers = ab.format_answers(answers)

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='received_answer')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def at_answer(request, template_name='message/at_answer.html'):
    answers = ab.get_at_answers(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(answers, count=10, page=page_num).info
    answers = page_objs[0]
    page_params = (page_objs[1], page_objs[4])
    answers = ab.format_answers(answers)

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='at_answer')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# ===================================================ajax部分=================================================================#
@member_required
def get_unread_count_total(request):

    count = urb.get_unread_count_total(request.user)
    r = dict(flag='0', result=count)
    return HttpResponse(json.dumps(r), mimetype='application/json')


def show_received_like(request, template_name='message/show_received_like.html'):
    '''
    显示指定用户收到的赞列表 用于分享  无需登录
    '''
    user_id = request.REQUEST.get('user_id', None)
    if not user_id:
        return render_to_response(template_name, locals(), context_instance=RequestContext(request))

    user = ub.get_user_by_id(user_id)
    if not user:
        return render_to_response(template_name, locals(), context_instance=RequestContext(request))

    request.user = user
    
    likes = lb.get_to_user_likes(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(likes, count=10, page=page_num).info
    likes = page_objs[0]
    page_params = (page_objs[1], page_objs[4])
    likes = lb.format_likes(likes)
    likes_count = page_objs[5]

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='received_like')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def share_received_like(request):
    '''
    后台生成分享的图片
    '''
    import os
    from django.conf import settings
    
    result = {'flag': -1, 'result': '操作失败'}

    # 拼装获取指定用户赞的页面url
    url = "%s://%s/message/show_received_like?user_id=%s" % (
        request.META['wsgi.url_scheme'], 
        request.META['HTTP_HOST'],
        request.user.id
    )

    # 定义生成临时图片位置
    file_name = '%s/static_local/temp_share/capty_%s.png' % (os.path.dirname(settings.SITE_ROOT), utils.uuid_without_dash())
    temp = None

    try:
        # 调用子程序 生成图片
        cmd = 'python %s/common/capty.py %s %s' % (os.path.dirname(settings.SITE_ROOT), url, file_name)
        flag, msg = utils.exec_command(cmd, 20)
        if not flag:
            result = {'flag': -1, 'result': u'服务器响应超时, 请重试'}
        else:
            # 读取临时文件上传到七牛
            temp = open(file_name, 'rb')
            flag, img_name = qiniu_client.upload_img(temp)
            if flag:
                result = {'flag': 0, 'result': '%s/%s' % (settings.IMG0_DOMAIN, img_name.split('!')[0])}
            else:
                result = {'flag': -1, 'result': u'分享失败, 请重试'}
    except Exception, e:
        logging.error(debug.get_debug_detail(e))
        result = {'flag': -1, 'result': u'分享失败, 请重试'}
    finally:
        # 善后
        if temp:
            temp.close()
            os.remove(file_name)

    return HttpResponse(json.dumps(result))
