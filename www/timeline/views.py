# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.misc.decorators import member_required

from www.timeline import interface


ufb = interface.UserFollowBase()


@member_required
def user_timeline(request):
    return render_to_response('timeline/user_timeline.html', locals(), context_instance=RequestContext(request))


@member_required
def follow_people(request, to_user_id):
    errcode, errmsg = ufb.follow_people(request.user.id, to_user_id)
    r = dict(errcode=errcode, errmsg='ok' if errcode == 0 else errmsg)
    return HttpResponse(json.dumps(r), mimetype='application/json')

@member_required
def unfollow_people(request, to_user_id):
    errcode, errmsg = ufb.unfollow_people(request.user.id, to_user_id)
    r = dict(errcode=errcode, errmsg=errmsg)
    return HttpResponse(json.dumps(r), mimetype='application/json')