# -*- coding: utf-8 -*-

import logging
from django.db import transaction

from common import debug, cache
from www.misc.decorators import cache_required
from www.misc import consts
from www.message.interface import UnreadCountBase
from www.account.interface import UserBase, UserCountBase
from www.stock.interface import StockFollowBase
from www.timeline.models import UserFollow, Feed


dict_err = {
    30100: u'自己关注自己不被允许',
    30101: u'查无此人',
    30102: u'feed不存在或者已删除',
}
dict_err.update(consts.G_DICT_ERROR)

TIMELINE_DB = 'timeline'
MAX_TIMELINE_LEN = 100
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

            UserBase().format_user_with_count_info(obj.user)
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

            # 更新用户timeline，后续修改成异步的
            FeedBase().get_user_timeline_feed_ids(from_user_id, must_update_cache=True)

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
            return 99900, dict_err.get(99900)

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

            # 更新用户timeline，后续修改成异步的
            FeedBase().get_user_timeline_feed_ids(from_user_id, must_update_cache=True)

            # 更新关注和粉丝总数信息
            UserCountBase().update_user_count(user_id=from_user_id, code='following_count', operate='minus')
            UserCountBase().update_user_count(user_id=to_user_id, code='follower_count', operate='minus')

            transaction.commit(using=TIMELINE_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(using=TIMELINE_DB)
            return 99900, dict_err.get(99900)

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


class FeedBase(object):

    def __init__(self):
        pass

    def format_feeds_by_id(self, feed_ids):
        from www.question.interface import QuestionBase, AnswerBase
        from www.stock.interface import StockFeedBase

        feeds = []
        for feed_id in feed_ids:
            feed = self.get_feed_by_id(feed_id)
            dict_feed = dict(feed_id=feed.id, create_time=feed.create_time.strftime('%Y-%m-%d %H:%M:%S'), feed_type=feed.feed_type)

            if feed.source == 0:  # 用户产生的动态
                user = UserBase().get_user_by_id(feed.user_id)
                obj_info = dict(user_id=feed.user_id, user_avatar=user.get_avatar_65(), user_nick=user.nick)
                if feed.feed_type in (1,):
                    obj_info.update(QuestionBase().get_question_summary_by_id(feed.obj_id))
                elif feed.feed_type in (2, 3):
                    obj_info.update(AnswerBase().get_answer_summary_by_id(feed.obj_id))
            if feed.source == 1:  # 股票产生的动态
                obj_info = StockFeedBase().get_stock_feed_summary_by_id(feed.obj_id)

            dict_feed.update(obj_info)
            feeds.append(dict_feed)

        return feeds

    def create_feed(self, user_id, obj_id, feed_type, content=None):
        assert user_id and obj_id

        source = 1 if str(feed_type) == "4" else 0
        feed = Feed.objects.create(user_id=user_id, feed_type=feed_type, obj_id=obj_id, source=source)

        # 更新订阅者timeline
        self.push_feed_to_follower(user_id, feed)
        return 0, feed

    def push_feed_to_follower(self, user_id, feed):
        '''
        @note: 推送feed到粉丝的队列中
        '''
        # 推自己
        # cache.CacheQueue(key='user_timeline_%s' % user_id, max_len=MAX_TIMELINE_LEN, time_out=3600 * 24 * 7).push(feed.id)

        # 推粉丝
        if feed.source == 0:    # 取用户粉丝
            followers = UserFollowBase().get_followers_by_user_id(user_id)
            user_ids = [follower.from_user_id for follower in followers]
        elif feed.source == 1:  # 取股票粉丝
            followers = StockFollowBase().get_followers_by_stock_id(feed.user_id)
            user_ids = [follower.user_id for follower in followers]

        for user_id in user_ids:
            cache_queue = cache.CacheQueue(key='user_timeline_%s' % user_id, max_len=MAX_TIMELINE_LEN, time_out=3600 * 24 * 7)
            if cache_queue.exists():
                cache_queue.push(feed.id)

    def pop_feed_from_follower(self, user_id, feed_id):
        '''
        @note: 从粉丝的队列中推出feed
        '''
        followers = UserFollowBase().get_followers_by_user_id(user_id)
        for follower in followers:
            cache_queue = cache.CacheQueue(key='user_timeline_%s' % follower.from_user_id, max_len=MAX_TIMELINE_LEN, time_out=3600 * 24 * 7)
            if cache_queue.exists():
                cache_queue.pop(feed_id)

    def get_user_timeline(self, user_id, last_feed_id='', page_count=5):
        page_count = int(page_count)
        assert 1 < page_count < 10

        feed_ids = self.get_user_timeline_feed_ids(user_id)
        if feed_ids:
            index = feed_ids.index(str(last_feed_id)) if last_feed_id else -1
            feed_ids = feed_ids[index + 1:index + 1 + page_count]

        return self.format_feeds_by_id(feed_ids)

    def get_user_timeline_feed_ids(self, user_id, must_update_cache=False):
        cache_queue = cache.CacheQueue(key='user_timeline_%s' % user_id, max_len=MAX_TIMELINE_LEN, time_out=3600 * 24 * 7)
        feed_ids = []
        if not cache_queue.exists() or must_update_cache:
            feed_ids = self.get_user_timeline_feed_ids_from_db(user_id)
            if feed_ids is not None or must_update_cache:
                cache_queue.init(feed_ids)
        else:
            feed_ids = cache_queue[0:-1]
        return feed_ids

    def get_user_timeline_feed_ids_from_db(self, user_id):
        '''
        @note: 从数据库中直接获取用户timeline
        '''
        assert user_id
        user_following_user_ids = [f.to_user_id for f in UserFollowBase().get_following_by_user_id(user_id)]
        user_following_user_ids.extend([f.stock_id for f in StockFollowBase().get_stock_follows_by_user_id(user_id)])
        # user_following_user_ids.append(user_id)  # 包含自己产生的feed

        if user_following_user_ids:
            feeds = Feed.objects.filter(user_id__in=user_following_user_ids)[:100]
            return [f.id for f in feeds]
        else:
            return []

    @cache_required(cache_key='feed_%s', expire=3600 * 24, cache_config=cache.CACHE_TIMELINE)
    def get_feed_by_id(self, feed_id, must_update_cache=False):
        try:
            return Feed.objects.get(id=feed_id)
        except Feed.DoesNotExist:
            return ''

    def remove_feed(self, user_id, obj_id, feed_type=1):
        '''
        @note: 删除feed
        '''
        try:
            feed = Feed.objects.get(user_id=user_id, feed_type=feed_type, obj_id=obj_id)
        except Feed.DoesNotExist:
            return 30102, dict_err.get(30102)

        self.pop_feed_from_follower(user_id, feed.id)
        feed.delete()

        return 0, dict_err.get(0)

    def get_feed_ids_by_feed_type(self, feed_type, user_ids):
        return [feed.id for feed in Feed.objects.filter(feed_type=feed_type, user_id__in=user_ids)]
