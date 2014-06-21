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
    from www.account.interface import UserCountBase

    last_feed_id = request.REQUEST.get('last_feed_id', '').strip()
    feeds = fb.get_user_timeline(request.user.id, last_feed_id)

    need_get_recommended_user = False
    # timeline的feed数大于5并且关注的人数大于3才不推荐
    if not last_feed_id and (len(feeds) < 5 or UserCountBase().get_user_count_info(request.user.id)['following_count'] < 3):
        need_get_recommended_user = True
    return HttpResponse(json.dumps(dict(feeds=feeds, need_get_recommended_user=need_get_recommended_user)), mimetype='application/json')


@member_required
@common_ajax_response
def follow_people(request, to_user_id):
    return ufb.follow_people(request.user.id, to_user_id)


@member_required
@common_ajax_response
def unfollow_people(request, to_user_id):
    return ufb.unfollow_people(request.user.id, to_user_id)
