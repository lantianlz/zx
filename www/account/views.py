# -*- coding: utf-8 -*-

import urllib
import json
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, user_agent_parser
from www.misc import qiniu_client
from www.account import interface
from www.misc.decorators import member_required
from www.account.interface import user_profile_required
from www.timeline.interface import UserFollowBase
from www.tasks import async_clear_count_info_by_code

ub = interface.UserBase()
ib = interface.InvitationBase()
ufb = UserFollowBase()


def show_index(request):
    if request.user.is_authenticated():
        #from www.question.views import question_home
        # return question_home(request)

        from www.timeline.views import show_user_timeline
        return show_user_timeline(request)
    else:
        return login(request)
        # return HttpResponseRedirect('/login')


def login(request, template_name='account/login_bg.html'):
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

    user_agent_dict = user_agent_parser.Parse(request.META.get('HTTP_USER_AGENT'))
    # 手机客户端换模板
    if user_agent_dict['device']['family'] != 'Other':
        template_name = 'account/login.html'

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def regist(request, invitation_code=None, template_name='account/regist.html'):
    email = request.POST.get('email', '').strip()
    nick = request.POST.get('nick', '').strip()
    password = request.POST.get('password', '').strip()
    invitation = None
    invitation_code = invitation_code or request.session.get('invitation_code', '')
    if invitation_code:
        invitation = ib.get_invitation_by_code(invitation_code)
        if invitation:
            request.session['invitation_code'] = invitation.code
    if not invitation:
        return HttpResponse(u'网站内测中，只能通过邀请注册，邀请码获取可以联系QQ: 2659790310')
    if request.POST:
        flag, result = ub.regist_user(email, nick, password, ip=utils.get_clientip(request),
                                      invitation_code=request.session.get('invitation_code'))
        if flag:
            user = auth.authenticate(username=email, password=password)
            auth.login(request, user=user)
            next_url = request.session.get('next_url') or '/home'
            request.session.update(dict(next_url='', invitation_code=''))
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
        err_msg = u'用户不存在'
        return HttpResponse(err_msg)


@member_required
@user_profile_required
def user_questions(request, user_id, template_name='account/user_questions.html'):
    '''
    提问 - 个人主页
    '''
    user = user_id  # 装饰器转换了对象

    from www.question.interface import QuestionBase
    qb = QuestionBase()
    questions = QuestionBase().format_quesitons(qb.get_question_by_user_id(user.id))

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
@user_profile_required
def user_answers(request, user_id, template_name='account/user_answers.html'):
    '''
    回答 - 个人主页
    '''
    user = user_id  # 装饰器转换了对象

    from www.question.interface import AnswerBase
    ab = AnswerBase()
    answers = ab.format_answers(ab.get_user_sended_answer(user.id))

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
@user_profile_required
def user_following(request, user_id, template_name='account/user_following.html'):
    '''
    关注 - 个人主页
    '''
    user = user_id  # 装饰器转换了对象

    user_followings = ufb.format_following(ufb.get_following_by_user_id(user.id))
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
@user_profile_required
def user_followers(request, user_id, template_name='account/user_followers.html'):
    '''
    粉丝 - 个人主页
    '''
    user = user_id  # 装饰器转换了对象
    user_followers = ufb.format_follower(ufb.get_followers_by_user_id(user.id))

    # 异步清除未读消息数
    async_clear_count_info_by_code(request.user.id, code='fans')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def user_settings(request, template_name='account/change_profile.html'):
    img_key = 'avatar_%s' % utils.uuid_without_dash()   # 七牛上传图片文件名
    uptoken = qiniu_client.get_upload_token(img_key)    # 七牛图片上传token
    if request.POST:
        nick = request.POST.get('nick')
        gender = request.POST.get('gender')
        birthday = request.POST.get('birthday')
        des = request.POST.get('des')

        flag, result = ub.change_profile(request.user, nick, gender, birthday, des)
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
    invitation = ib.get_invitation_by_user_id(request.user.id)
    invitation_users = ib.format_invitation_user(ib.get_invitation_user(request.user.id))
    invitation_users_count = len(invitation_users)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def test500(request):
    raise Exception, u'test500 for send error email'


# ===================================================ajax部分=================================================================#
def get_user_info_by_id(request):
    '''
    @note: 根据用户id获取名片信息
    '''
    user_id = request.REQUEST.get('user_id')
    infos = {}
    if user_id:
        user = ub.get_user_by_id(user_id)
        if user:
            infos = dict(user_id=user.id, nick=user.nick, avatar=user.get_avatar_65(), des=user.des or '', gender=user.gender,
                         is_follow=ufb.check_is_follow(request.user.id, user_id) if request.user.id != user_id else False)

            user_count_info = interface.UserCountBase().get_user_count_info(user_id)
            user_question_count, user_answer_count, user_liked_count = user_count_info['user_question_count'], \
                user_count_info['user_answer_count'], user_count_info['user_liked_count']
            infos.update(dict(user_question_count=user_question_count, user_answer_count=user_answer_count, user_liked_count=user_liked_count))

    return HttpResponse(json.dumps(infos))
