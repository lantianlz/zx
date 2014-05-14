# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

# from common import utils
from www.misc.decorators import member_required, common_ajax_response

from www.timeline import interface


ufb = interface.UserFollowBase()
fb = interface.FeedBase()


@member_required
def show_user_timeline(request):
    return render_to_response('timeline/user_timeline.html', locals(), context_instance=RequestContext(request))


@member_required
def get_user_timeline(request):
    last_feed_id = request.REQUEST.get('last_feed_id', '')
    feeds = fb.get_user_timeline(request.user.id, last_feed_id)
    need_get_recommended_user = True if len(feeds) < 5 and not last_feed_id else False
    return HttpResponse(json.dumps(dict(feeds=feeds, need_get_recommended_user=need_get_recommended_user)), mimetype='application/json')


@member_required
@common_ajax_response
def follow_people(request, to_user_id):
    errcode, errmsg = ufb.follow_people(request.user.id, to_user_id)
    return errcode, errmsg


@member_required
@common_ajax_response
def unfollow_people(request, to_user_id):
    errcode, errmsg = ufb.unfollow_people(request.user.id, to_user_id)
    return errcode, errmsg
