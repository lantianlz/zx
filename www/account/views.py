# -*- coding: utf-8 -*-

import urllib
from django.contrib import auth
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from www.account.interface import UserBase
from www.misc.decorators import member_required


def login(request, template_name='account/login.html'):
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    if request.POST:
        next_url = request.REQUEST.get('next_url')
        if next_url:
            request.session['next_url'] = urllib.unquote_plus(next_url)
        user = auth.authenticate(username=email, password=password)
        if user:
            auth.login(request, user)
            return HttpResponse(u'user %s login ok' % email)
        else:
            return HttpResponse(u'user %s password error' % email)
    else:
        return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def home(request):
    return HttpResponse(u'user is %s:%s' % (request.user.nick, request.user.email))
