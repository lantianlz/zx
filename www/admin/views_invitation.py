# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from account.interface import InvitationBase, UserBase

@verify_permission('')
def invitation(request, template_name='admin/invitation.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('query_invitation')
def search(request):
    
    data = {
        "invite_by": {"id": "", "name": "", "avatar": ""},
        "invite": []
    }
    
    name = request.REQUEST.get("name")
    
    # 被谁邀请
    user = UserBase().get_user_by_nick(name)
    if user:
        invite_user = InvitationBase().get_invite_by_who(user.id)
        if invite_user:
            data["invite_by"]={
                "id": invite_user.id,
                "name": invite_user.nick,
                "avatar": invite_user.get_avatar_65()
            }
    
        # 邀请的人
        for iu in InvitationBase().get_invitation_user(user.id):
            temp = UserBase().get_user_by_id(iu.user_id)
            if temp == "":
                continue
                
            data["invite"].append({
                "id": temp.id,
                "name": temp.nick,
                "avatar": temp.get_avatar_65()
            })
    
    return HttpResponse(json.dumps(data), mimetype='application/json')
