# -*- coding: utf-8 -*-

import datetime
import logging
from django.db import transaction

from common import debug, utils
from www.misc import consts
from www.misc.decorators import cache_required
from www.account.interface import UserBase
from www.stock.models import Stock, StockFeed, StockFollow, StockData, Kind, StockKind, KindData

ub = UserBase()

dict_err = {
    80100: u'股票不存在',
    80101: u'股票名称或者代码已经存在',
    80102: u'股票名称已经存在',
    80103: u'股票代码已经存在',
    80104: u'最多关注10支股票',
}
dict_err.update(consts.G_DICT_ERROR)
DEFAULT_DB = "default"


def stock_required(func):
    def _decorator(self, stock_id_or_object, *args, **kwargs):
        stock = stock_id_or_object
        if not isinstance(stock_id_or_object, Stock):
            stock = StockBase().get_stock_by_id(stock_id_or_object)
            if not stock:
                return 80100, dict_err.get(80100)
        return func(self, stock, *args, **kwargs)
    return _decorator


class StockBase(object):

    def __init__(self):
        pass

    def get_all_stocks(self, state=True):
        ps = dict()
        if state is not None:
            ps.update(state=state)
        return Stock.objects.filter(**ps)

    def get_stocks_by_name(self, name, state):
        stocks = self.get_all_stocks(state)

        if name:
            stocks = stocks.filter(name__contains=name)
        return stocks

    def search_stocks(self, key):
        stocks = Stock.objects.filter(name__icontains=key, state=True)
        if not stocks:
            stocks = Stock.objects.filter(code__icontains=key, state=True)
        return stocks

    def create_stock(self, name, code, belong_board, belong_market, img, origin_uid, des=None, main_business=0, sort_num=0, state=False):
        try:
            assert name and code and belong_board and belong_market and img
        except:
            return 99800, dict_err.get(99800)

        if Stock.objects.filter(name=name) or Stock.objects.filter(code=code):
            return 80101, dict_err.get(80101)

        try:
            stock = Stock.objects.create(
                name=name, code=code, belong_board=belong_board, belong_market=belong_market, state=state,
                img=img, origin_uid=origin_uid, des=des, main_business=main_business, sort_num=sort_num
            )
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, stock

    def get_stock_by_id(self, stock_id, state=True):
        ps = dict(id=stock_id)
        if state is not None:
            ps.update(state=state)
        try:
            return Stock.objects.get(**ps)
        except Stock.DoesNotExist:
            pass

    def get_stock_by_code(self, code, state=True):
        ps = dict(code=code)
        if state is not None:
            ps.update(state=state)
        try:
            return Stock.objects.get(**ps)
        except Stock.DoesNotExist:
            pass

    def modify_stock(self, stock_id, **kwargs):

        if not stock_id or not kwargs.get('name') or not kwargs.get('code') \
                or not kwargs.get('belong_board') or not kwargs.get('belong_market'):
            return 99800, dict_err.get(99800)

        stock = self.get_stock_by_id(stock_id, None)
        if not stock:
            return 80100, dict_err.get(80100)

        temp = Stock.objects.filter(name=kwargs.get('name'))
        if temp and temp[0].id != stock.id:
            return 80102, dict_err.get(80102)

        temp = Stock.objects.filter(code=kwargs.get('code'))
        if temp and temp[0].id != stock.id:
            return 80103, dict_err.get(80103)

        try:
            for k, v in kwargs.items():
                setattr(stock, k, v)

            stock.save()

            state = kwargs.get('state', True)
            # 修改股票动态记录的状态为false
            StockFeed.objects.filter(stock__id=stock.id).update(state=state)

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)


class StockFeedBase(object):

    def __init__(self):
        pass

    def format_stock_feeds(self, stock_feeds):
        for stock_feed in stock_feeds:
            stock_feed.answer_content_length = utils.get_chinese_length(stock_feed.answer_content)
        return stock_feeds

    @stock_required
    @transaction.commit_manually(using=DEFAULT_DB)
    def create_feed(self, stock_id_or_object, question_content, answer_content,
                    belong_market, origin_id=None, create_time=None, create_question_time=None):
        try:
            from www.timeline.interface import FeedBase
            try:
                assert stock_id_or_object and question_content and answer_content
                assert belong_market is not None
            except:
                transaction.rollback(using=DEFAULT_DB)
                return 99800, dict_err.get(99800)

            stock = stock_id_or_object
            now = datetime.datetime.now()
            ps = dict(stock=stock, question_content=question_content, answer_content=answer_content, belong_market=belong_market, origin_id=origin_id)
            ps.update(create_time=create_time or now, create_question_time=create_question_time or now)
            feed = StockFeed.objects.create(**ps)

            stock.feed_count += 1
            stock.save()

            # 产生feed
            FeedBase().create_feed(stock.id, feed.id, feed_type=4)

            transaction.commit(using=DEFAULT_DB)

            return 0, feed
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def get_all_stock_feeds(self, state=True):
        # ps = dict(stock__state=True)
        ps = dict()
        if state is not None:
            ps.update(state=state)
        # return StockFeed.objects.select_related("stock").filter(**ps)
        return StockFeed.objects.prefetch_related("stock").filter(**ps)

    def get_stock_feeds_by_stock(self, stock):
        return StockFeed.objects.select_related("stock").filter(stock=stock, state=True)

    def get_stock_feed_by_id(self, stock_feed_id, state=True):
        ps = dict(id=stock_feed_id)
        if state is not None:
            ps.update(state=state)
        try:
            return StockFeed.objects.select_related("stock").get(**ps)
        except StockFeed.DoesNotExist:
            pass

    def get_stock_feeds_by_user_id(self, user_id):
        stock_ids = [sf.stock.id for sf in StockFollowBase().get_stock_follows_by_user_id(user_id)]
        feeds = StockFeed.objects.select_related("stock").filter(stock__id__in=stock_ids)
        return feeds

    @cache_required(cache_key='stock_feed_summary_%s', expire=3600)
    def get_stock_feed_summary_by_id(self, stock_feed_id_or_object, must_update_cache=False):
        '''
        @note: 获取股票动态摘要信息，用于feed展现
        '''
        from www.custom_tags.templatetags.custom_filters import str_display
        stock_feed = self.get_stock_feed_by_id(stock_feed_id_or_object, state=None) if not isinstance(stock_feed_id_or_object, StockFeed) else stock_feed_id_or_object
        stock_feed_summary = {}

        if stock_feed:
            stock = stock_feed.stock
            stock_feed_summary = dict(stock_id=stock.id, stock_code=stock.code, stock_url=stock.get_url(), stock_name=stock.name,
                                      stock_img=stock.img, stock_feed_url=stock_feed.get_url(), stock_feed_question_content=stock_feed.question_content,
                                      stock_feed_answer_content=stock_feed.answer_content,
                                      stock_feed_answer_content_short=str_display(stock_feed.answer_content, 150))
        return stock_feed_summary


class StockFollowBase(object):

    def __init__(self):
        pass

    @stock_required
    @transaction.commit_manually(using=DEFAULT_DB)
    def follow_stock(self, stock, user_id):
        try:
            from www.timeline.interface import FeedBase
            if not ub.get_user_by_id(user_id):
                transaction.rollback(using=DEFAULT_DB)
                return 99600, dict_err.get(99600)

            if StockFollow.objects.filter(user_id=user_id).count() >= 10:
                transaction.rollback(using=DEFAULT_DB)
                return 80104, dict_err.get(80104)

            try:
                uf = StockFollow.objects.create(user_id=user_id, stock=stock)
            except:
                transaction.rollback(using=DEFAULT_DB)
                return 0, dict_err.get(0)

            stock.following_count += 1
            stock.save()

            # 更新用户timeline，后续修改成异步的
            FeedBase().get_user_timeline_feed_ids(user_id, must_update_cache=True)

            transaction.commit(using=DEFAULT_DB)
            return 0, uf
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    @stock_required
    @transaction.commit_manually(using=DEFAULT_DB)
    def unfollow_stock(self, stock, user_id):
        try:
            from www.timeline.interface import FeedBase
            if not ub.get_user_by_id(user_id):
                transaction.rollback(using=DEFAULT_DB)
                return 99600, dict_err.get(99600)

            try:
                uf = StockFollow.objects.get(stock=stock, user_id=user_id)
            except StockFollow.DoesNotExist:
                transaction.rollback(using=DEFAULT_DB)
                return 0, dict_err.get(0)
            uf.delete()

            stock.following_count -= 1
            stock.save()

            # 更新用户timeline，后续修改成异步的
            FeedBase().get_user_timeline_feed_ids(user_id, must_update_cache=True)

            transaction.commit(using=DEFAULT_DB)
            return 0, dict_err.get(0)
        except Exception, e:
            logging.error(debug.get_debug_detail(e))
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def check_is_follow(self, stock_id, user_id):
        return True if StockFollow.objects.filter(stock=stock_id, user_id=user_id) else False

    def get_stock_follows_by_user_id(self, user_id):
        return StockFollow.objects.select_related("stock").filter(user_id=user_id, stock__state=True)

    def get_followers_by_stock_id(self, stock_id):
        return StockFollow.objects.select_related("stock").filter(stock=stock_id, stock__state=True)


class StockDataBase(object):
    
    def get_stock_chain_data(self, date, market_value_range, page_count=50):
        """
        获取个股成交额环比增长率
        """
        objs = StockData.objects.select_related('stock').filter(date=date, market_value__range=market_value_range).order_by('-turnover_change_pre_day')
        return objs[:page_count]

    def get_stock_percent_in_total_data(self, date, market_value_range, page_count=50):
        """
        获取个股成交额占沪深总成交额比率
        """
        objs = StockData.objects.select_related('stock').filter(date=date, market_value__range=market_value_range).order_by('-turnover_rate_to_all')
        return objs[:page_count]

    def get_stock_history_chain_data(self, stock_id, page_count=240):
        objs = StockData.objects.filter(stock_id=stock_id).order_by('-date')
        return objs[:page_count]


class KindBase(object):

    def get_all_kind(self):
        return Kind.objects.all()

    def get_kind_by_id(self, kind_id):
        return Kind.objects.get(id=kind_id)

    def search_kind_for_admin(self, name):
        objs = self.get_all_kind()

        if name:
            objs = objs.filter(name__icontains=name)
        return objs

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_kind(self, name, stocks, group=0, sort=0):
        kind = None

        if not name or not stocks:
            return 99800, dict_err.get(99800)

        try:
            kind = Kind.objects.create(
                name=name, group=group, sort_num=sort
            )

            for stock in stocks:
                StockKind.objects.create(kind=kind, stock_id=stock)
            
            # KindDataBase().update_kind_data(kind.id)

            # 异步调用
            from www.tasks import async_update_kind_data
            async_update_kind_data.delay(kind.id)

            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, kind

    @transaction.commit_manually(using=DEFAULT_DB)
    def modify_kind(self, kind_id, name, stocks, group=0, sort=0):
        

        if not name or not stocks or not kind_id:
            return 99800, dict_err.get(99800)

        try:
            kind = self.get_kind_by_id(kind_id)

            kind.name = name
            kind.group = group
            kind.sort = sort
            kind.save()

            StockKind.objects.filter(kind_id=kind_id).delete()

            for stock in stocks:
                StockKind.objects.create(kind=kind, stock_id=stock)
            
            # KindDataBase().update_kind_data(kind_id)

            # 异步调用
            from www.tasks import async_update_kind_data
            async_update_kind_data.delay(kind_id)

            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, kind

    def remove_kind(self, kind_id):
        try:
            Kind.objects.get(id=kind_id).delete()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)


class KindDataBase(object):

    def get_kind_chain_data(self, date, page_count=50):
        """
        获取行业成交额环比增长率
        """
        objs = KindData.objects.select_related('kind').filter(date=date).order_by('-turnover_change_pre_day')
        return objs[:page_count]

    def get_kind_percent_in_total_data(self, date, page_count=50):
        """
        获取行业成交额占沪深总成交额比率
        """
        objs = KindData.objects.select_related('kind').filter(date=date).order_by('-turnover_rate_to_all')
        return objs[:page_count]

    def get_kind_history_chain_data(self, kind_id, page_count=240):
        objs = KindData.objects.filter(kind_id=kind_id).order_by('-date')
        return objs[:page_count]

    def get_stock_chain_data_of_kind(self, date, kind_id, page_count=10):
        '''
        获取板块下股票数据
        '''
        objs = StockData.objects.select_related('stock').filter(date=date, stock__stock_kind__kind__id=kind_id).order_by('-turnover_change_pre_day')
        return objs[:page_count]

    def get_stock_percent_in_total_data_of_kind(self, date, kind_id, page_count=10):
        '''
        获取板块下股票数据
        '''
        objs = StockData.objects.select_related('stock').filter(date=date, stock__stock_kind__kind__id=kind_id).order_by('-turnover_rate_to_all')
        return objs[:page_count]




    def update_kind_data(self, kind_id):

        def _init_stock_kind_data(now_date, kind):

            # 获取每天股票的数据
            stock_data = {}
            for x in StockData.objects.filter(date=now_date):
                stock_data[x.stock_id] = x.turnover

            # 按照行业计算各行业总交易额
            dict_kind_trunover = {}
            for stock_kind in StockKind.objects.select_related("stock", "kind").filter(kind__id=kind):
                if not dict_kind_trunover.has_key(stock_kind.kind_id):
                    dict_kind_trunover[stock_kind.kind_id] = 0

                dict_kind_trunover[stock_kind.kind_id] += stock_data.get(stock_kind.stock_id, 0)

            for x in dict_kind_trunover:
                if not KindData.objects.filter(kind__id=x, date=now_date) and dict_kind_trunover[x] > 0:
                    KindData.objects.create(kind_id=x, date=now_date, turnover=dict_kind_trunover[x])


        def _get_kind_total_by_day(now_date):
            from django.db.models import Sum
            kind_total = {}
            kind_total[now_date] = KindData.objects.filter(date=now_date).aggregate(Sum('turnover'))['turnover__sum']

            return kind_total

        def _update_kind_turnover_rate_to_all_today(now_date, kind):
            kind_total = _get_kind_total_by_day(now_date)
            # pprint(kind_total)
            for i, kind_data in enumerate(KindData.objects.select_related("kind").filter(date=now_date, kind__id=kind)):
                if kind_total.get(kind_data.date):
                    kind_data.turnover_rate_to_all = kind_data.turnover / kind_total.get(kind_data.date)
                    kind_data.save()
                # if i % 1000 == 0:
                #     print "%s:%s ok" % (datetime.datetime.now(), i)
                # break

        def _update_kind_turnover_change_today(now_date, kind):
            for i, kind_data in enumerate(KindData.objects.select_related("kind").filter(date=now_date, kind__id=kind)):
                kind_data_pres = KindData.objects.filter(kind=kind_data.kind, date__lt=kind_data.date)[:1]
                if kind_data_pres:
                    kind_date_pre = kind_data_pres[0]

                    if kind_date_pre.turnover > 0 and kind_data.turnover > 0:
                        turnover_change_pre_day = (kind_data.turnover - kind_date_pre.turnover) / kind_date_pre.turnover * 100
                        kind_data.turnover_change_pre_day = turnover_change_pre_day

                    if kind_date_pre.turnover_rate_to_all > 0 and kind_data.turnover_rate_to_all > 0:
                        turnover_rate_to_all_change_per_day = (kind_data.turnover_rate_to_all - kind_date_pre.turnover_rate_to_all) / kind_date_pre.turnover_rate_to_all * 100
                        kind_data.turnover_rate_to_all_change_per_day = turnover_rate_to_all_change_per_day

                    kind_data.save()
                # if i % 1000 == 0:
                #     print "%s:%s ok" % (datetime.datetime.now(), i)
                # break



        # 删除此行业的数据
        KindData.objects.filter(kind__id=kind_id).delete()

        # 计算出以前365天的数据
        for i in range(365):
            temp_date = datetime.datetime.now().date() - datetime.timedelta(364-i)

            _init_stock_kind_data(temp_date, kind_id)
            _update_kind_turnover_rate_to_all_today(temp_date, kind_id)
            _update_kind_turnover_change_today(temp_date, kind_id)
