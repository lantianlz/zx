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


def show_index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home')
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
        ub = UserBase()
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


@member_required
def home(request, template_name='account/question_home.html'):
    #todo 更新最后活跃时间
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
    # return HttpResponse(u'user is %s:%s' % (request.user.nick, request.user.email))


@member_required
def question_detail(request, template_name='account/question_detail.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
    

@member_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/home')
