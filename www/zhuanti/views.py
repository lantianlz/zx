# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from www.zhuanti.interface import ZhuantiBase


def index(request, template_name='zhuanti/zhuanti_list.html'):
    zhuantis = ZhuantiBase().get_all_zhuantis()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def zhuanti_detail(request, zhuanti_domain):
    zhuanti = ZhuantiBase().get_zhuanti_by_id_or_domain(zhuanti_domain)
    if not zhuanti:
        raise Http404

    template_name = 'zhuanti/zhuanti_%s.html' % zhuanti.domain
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
