# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse  # , HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.misc.decorators import member_required
from www.tasks import async_clear_count_info_by_code
from www.question import interface as interface_question
from www.message import interface


urb = interface.UnreadCountBase()
lb = interface_question.LikeBase()
ab = interface_question.AnswerBase()


@member_required
def system_message(request, template_name='message/system_message.html'):
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def received_like(request, template_name='message/received_like.html'):

    likes = lb.get_to_user_likes(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(likes, count=5, page=page_num).info
    likes = page_objs[0]
    page_params = (page_objs[1], page_objs[4])
    likes = lb.format_likes(likes)

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='received_like')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def received_answer(request, template_name='message/received_answer.html'):
    answers = ab.get_my_received_answer(request.user.id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(answers, count=5, page=page_num).info
    answers = page_objs[0]
    page_params = (page_objs[1], page_objs[4])
    answers = ab.format_answers(answers)

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='received_answer')
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def at_answer(request, template_name='message/at_answer.html'):
    unread_count_info = urb.get_unread_count_info(request.user)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


# ===================================================ajax部分=================================================================#
@member_required
def get_unread_count_total(request):

    count = urb.get_unread_count_total(request.user)
    r = dict(flag='0', result=count)
    return HttpResponse(json.dumps(r), mimetype='application/json')
