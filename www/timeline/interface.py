# -*- coding: utf-8 -*-

import datetime
import logging
from django.db import transaction
from django.db.models import F

from common import utils, debug, cache
from www.timeline.models import UserFollow
from www.account.interface import UserBase


dict_err = {
    30100: u'自己关注自己不被允许',
    30101: u'查无此人',

    998: u'参数缺失',
    999: u'系统错误',
    0: u'成功'
}

TIMELINE_DB = 'timeline'

ub = UserBase()


class UserFollowBase(object):

    def __init__(self):
        pass

    @transaction.commit_manually(using=TIMELINE_DB)
    def follow_people(self, from_user_id, to_user_id):
        try:
            if from_user_id == to_user_id:
                return 30100, dict_err.get(30100)
            if not (ub.get_user_by_id(from_user_id) and ub.get_user_by_id(to_user_id)):
                return 30101, dict_err.get(30101)

            is_two_way = False
            try:
                uf = UserFollow.objects.get(from_user_id=to_user_id, to_user_id=from_user_id)
                is_two_way = True
                uf.is_two_way = True
                uf.save()
            except UserFollow.DoesNotExist:
                pass

            try:
                uf = UserFollow.objects.create(from_user_id=from_user_id, to_user_id=to_user_id, is_two_way=is_two_way)
            except:
                transaction.rollback(using=TIMELINE_DB)
                return 0, dict_err.get(0)

            transaction.commit(using=TIMELINE_DB)
            return 0, uf
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(using=TIMELINE_DB)
            return 999, dict_err.get(999)

    @transaction.commit_manually(using=TIMELINE_DB)
    def unfollow_people(self, from_user_id, to_user_id):
        try:
            if not (ub.get_user_by_id(from_user_id) and ub.get_user_by_id(to_user_id)):
                transaction.rollback(using=TIMELINE_DB)
                return 30101, dict_err.get(30101)
            try:
                uf = UserFollow.objects.get(from_user_id=from_user_id, to_user_id=to_user_id)
            except UserFollow.DoesNotExist:
                transaction.rollback(using=TIMELINE_DB)
                return 0, dict_err.get(0)

            uf.delete()
            # 解除双向好友关系
            try:
                uf = UserFollow.objects.get(from_user_id=to_user_id, to_user_id=from_user_id)
                uf.is_two_way = False
                uf.save()
            except UserFollow.DoesNotExist:
                pass
            transaction.commit(using=TIMELINE_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(using=TIMELINE_DB)
            return 999, dict_err.get(999)

    def check_is_follow(self, from_user_id, to_user_id):
        return True if UserFollow.objects.filter(from_user_id=from_user_id, to_user_id=to_user_id) else False
