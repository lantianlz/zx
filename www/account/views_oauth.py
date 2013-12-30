# -*- coding: utf-8 -*-

import urllib
from pprint import pprint
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.account.interface import UserBase


def oauth_qq(request):
    authorize_url = 'https://graph.qq.com/oauth2.0/authorize'
    response_type = 'code'
    client_id = '1101146433'
    redirect_uri = urllib.quote_plus('http://www.zhixg.com/account/oauth/qq')
    state = 'state'

    return HttpResponseRedirect('%s?response_type=%s&client_id=%s&redirect_uri=%s&state=%s'
                                % (authorize_url, response_type, client_id, redirect_uri, state))
