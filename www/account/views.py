# -*- coding: utf-8 -*-

import urllib
import json
from pprint import pprint
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.account import interface
from www.misc.decorators import member_required

ub = interface.UserBase()


def show_index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/question')
    else:
        return HttpResponseRedirect('/login')


def login(request, template_name='account/login.html'):
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    if request.POST:
        user = auth.authenticate(username=email, password=password)
        if user:
            auth.login(request, user)
            next_url = request.session.get('next_url') or '/home'
            request.session.update(dict(next_url=''))
            return HttpResponseRedirect(next_url)
        else:
            error_msg = u'用户名或者密码错误'
    else:
        # 从REUQEST中或者HTTP_REFERER中获取
        next_url = utils.get_next_url(request)
        if next_url:
            request.session['next_url'] = urllib.unquote_plus(next_url)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def regist(request, template_name='account/regist.html'):
    email = request.POST.get('email', '').strip()
    nick = request.POST.get('nick', '').strip()
    password = request.POST.get('password', '').strip()
    if request.POST:
        flag, result = ub.regist_user(email, nick, password, ip=utils.get_clientip(request))
        if flag:
            user = auth.authenticate(username=email, password=password)
            auth.login(request, user=user)
            next_url = request.session.get('next_url') or '/home'
            request.session.update(dict(next_url=''))
            return HttpResponseRedirect(next_url)
        else:
            error_msg = result
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def forget_password(request, template_name='account/forget_password.html'):
    if request.POST:
        email = request.POST.get('email')
        flag, result = ub.send_forget_password_email(email)
        if not flag:
            error_msg = result
        else:
            success_msg = u'找回密码邮件已经发送，请登录邮箱后操作'

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def reset_password(request, template_name='account/reset_password.html'):
    if not request.POST:
        code = request.REQUEST.get('code')
        user = ub.get_user_by_code(code)
        if not user:
            error_msg = interface.dict_err.get(112)
            return render_to_response('account/forget_password.html', locals(), context_instance=RequestContext(request))
        else:
            request.session['reset_password_code'] = code
    else:
        new_password_1 = request.POST.get('new_password_1')
        new_password_2 = request.POST.get('new_password_2')
        code = request.session['reset_password_code']
        flag, result = ub.reset_password_by_code(code, new_password_1, new_password_2)
        if not flag:
            error_msg = result
        else:
            success_msg = u'密码修改成功，请重新登录'
            user = result
            user.backend = 'www.middleware.user_backend.AuthBackend'
            auth.login(request, user)
            request.session['reset_password_code'] = ''
            return HttpResponseRedirect('/home')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def get_user_by_nick(request, nick):
    user = ub.get_user_by_nick(nick)
    if user:
        return HttpResponseRedirect(user.get_url())
    else:
        err_msg = u'未找到对应user'
        return HttpResponse(err_msg)


@member_required
def user_profile(request, id=None, template_name='account/user_profile.html'):
    if not id:
        user = request.user
    else:
        user = ub.get_user_by_id(id)
        if not user:
            err_msg = u'未找到对应user'
            return HttpResponse(err_msg)
    is_me = (request.user == user)

    from www.question.interface import QuestionBase, AnswerBase
    qb = QuestionBase()
    ab = AnswerBase()
    user_question_count, user_answer_count, user_liked_count = qb.get_user_qa_count_info(user.id)
    questions = qb.format_quesitons(qb.get_question_by_user_id(user.id))
    answers = ab.format_answers(ab.get_user_sended_answer(user.id))

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def user_settings(request, template_name='account/change_profile.html'):
    if request.POST:
        nick = request.POST.get('nick')
        gender = request.POST.get('gender')
        birthday = request.POST.get('birthday')

        flag, result = ub.change_profile(request.user, nick, gender, birthday)
        if not flag:
            error_msg = result
        else:
            success_msg = u'修改资料成功'
            request.user = result
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def change_pwd(request, template_name='account/change_pwd.html'):
    if request.POST:
        old_password = request.POST.get('old_password')
        new_password_1 = request.POST.get('new_password_1')
        new_password_2 = request.POST.get('new_password_2')

        flag, result = ub.change_pwd(request.user, old_password, new_password_1, new_password_2)
        if not flag:
            error_msg = result
        else:
            success_msg = u'密码修改成功'
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def change_email(request, template_name='account/change_email.html'):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        flag, result = ub.change_email(request.user, email, password)
        if not flag:
            error_msg = result
        else:
            success_msg = u'邮箱修改成功'
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def verify_email(request, template_name='account/change_email.html'):
    code = request.GET.get('code')

    if not code:
        ub.send_confirm_email(request.user)
        success_msg = u'验证邮件发送成功，请登陆邮箱操作'
    else:
        flag, result = ub.check_email_confim_code(request.user, code)
        if flag:
            request.user = result
            success_msg = u'邮箱验证成功'
        else:
            error_msg = result
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def bind_community(request, template_name='account/bind_community.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def bind_mobile(request, template_name='account/bind_mobile.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def security_question(request, template_name='account/security_question.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def invitation(request, template_name='account/invitation.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def test500(request):
    raise Exception, u'test500 for send error email'


# ===================================================ajax部分=================================================================#
@member_required
def get_user_info_by_id(request):
    '''
    根据用户id获取名片信息
    '''
    user_id = request.REQUEST.get('user_id', None)

    infos = {
        'success': False
    }

    if user_id:
        infos = {
            'success': True,
            'id': 'e0f87ed0712b11e3b894000c290d194c',
            'name': '半夜没事乱溜达',
            'avatar': '/static/img/common/user3.jpg',
            'desc': '在那山的这边海的那边有一群程序员，他们老实又胹腆，他们苦逼又没钱。他们一天到晚坐在那里熬夜写软件，饿了就咬一口方便面～～哦苦命的程序员，哦苦命的程序员，只要一改需求他们就要重新搞一遍，但是期限只剩下两天。',
            'question_count': 125,
            'answer_count': 326,
            'like_count': 224,
            'is_follow': True
        }

    return HttpResponse(json.dumps(infos))
