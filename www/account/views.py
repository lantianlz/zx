# -*- coding: utf-8 -*-

from django.contrib import auth
from django.http import HttpResponse

from www.account.interface import UserBase


def login(request):
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    user = auth.authenticate(username=email, password=password)
    if user:
    	auth.login(request, user)
        return HttpResponse(u'user %s login ok' % email)
    else:
        return HttpResponse(u'user %s password error' % email)


def home(request):
    return HttpResponse(u'user is %s:%s' % (request.user.nick, request.user.email))
