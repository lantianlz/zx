# -*- coding: utf-8 -*-

import urllib
from django.contrib import auth
from django.http import HttpResponse

from www.account.interface import UserBase
from www.decorators.decorators import member_required


def login(request):
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    next_url = request.REQUEST.get('next_url')
    if next_url:
        request.session['next_url'] = urllib.unquote_plus(next_url)

    user = auth.authenticate(username=email, password=password)
    if user:
        auth.login(request, user)
        return HttpResponse(u'user %s login ok' % email)
    else:
        return HttpResponse(u'user %s password error' % email)


@member_required
def home(request):
    return HttpResponse(u'user is %s:%s' % (request.user.nick, request.user.email))
