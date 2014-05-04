# -*- coding: utf-8 -*-

import logging
from django.db import transaction

from common import debug
from www.timeline.models import UserFollow
from www.message.interface import UnreadCountBase
from www.account.interface import UserBase, UserCountBase


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

    def format_followobjs(self, objs, following_or_follower):
        for obj in objs:
            if following_or_follower == 'following':
                obj.user = UserBase().get_user_by_id(obj.to_user_id)

            if following_or_follower == 'follower':
                obj.user = UserBase().get_user_by_id(obj.from_user_id)

            user_count_info = UserCountBase().get_user_count_info(obj.user.id)
            obj.user.user_question_count = user_count_info['user_question_count']
            obj.user.user_answer_count = user_count_info['user_answer_count']
            obj.user.user_liked_count = user_count_info['user_liked_count']
            obj.user.following_count = user_count_info['following_count']
            obj.user.follower_count = user_count_info['follower_count']
        return objs

    def format_following(self, objs):
        return self.format_followobjs(objs, following_or_follower='following')

    def format_follower(self, objs):
        return self.format_followobjs(objs, following_or_follower='follower')

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

            # 更新关注和粉丝总数信息
            UserCountBase().update_user_count(user_id=from_user_id, code='following_count')
            UserCountBase().update_user_count(user_id=to_user_id, code='follower_count')

            # 发送未读消息数通知
            UnreadCountBase().update_unread_count(to_user_id, code='fans')

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

            # 更新关注和粉丝总数信息
            UserCountBase().update_user_count(user_id=from_user_id, code='following_count', operate='minus')
            UserCountBase().update_user_count(user_id=to_user_id, code='follower_count', operate='minus')

            transaction.commit(using=TIMELINE_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(using=TIMELINE_DB)
            return 999, dict_err.get(999)

    def check_is_follow(self, from_user_id, to_user_id):
        return True if UserFollow.objects.filter(from_user_id=from_user_id, to_user_id=to_user_id) else False

    def get_following_by_user_id(self, user_id):
        return UserFollow.objects.filter(from_user_id=user_id)

    def get_followers_by_user_id(self, user_id):
        return UserFollow.objects.filter(to_user_id=user_id)

    def get_following_count(self, user_id):
        return UserFollow.objects.filter(from_user_id=user_id).count()

    def get_follower_count(self, user_id):
        return UserFollow.objects.filter(to_user_id=user_id).count()
