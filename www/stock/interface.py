# -*- coding: utf-8 -*-

import datetime
from django.db import transaction

from common import debug, utils
from www.misc import consts
from www.stock.models import Stock, StockFeed


dict_err = {
    80100: u'股票不存在',
    80101: u'股票名称或者代码已经存在',
    80102: u'股票名称已经存在',
    80103: u'股票代码已经存在',
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

    def get_stocks_by_name(self, name):
        stocks = self.get_all_stocks(None)

        if name:
            stocks = stocks.filter(name__contains=name)

        return stocks

    def create_stock(self, name, code, belong_board, belong_market, img, origin_uid, des=None, sort_num=0, state=False):
        try:
            assert name and code and belong_board and belong_market and img
        except:
            return 99800, dict_err.get(99800)

        if Stock.objects.filter(name=name) or Stock.objects.filter(code=code):
            return 80101, dict_err.get(80101)

        try:
            stock = Stock.objects.create(
                name=name, code=code, belong_board=belong_board, belong_market=belong_market,
                img=img, origin_uid=origin_uid, des=des, sort_num=sort_num, state=state
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

            transaction.commit(using=DEFAULT_DB)
            return 0, feed
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def get_all_stock_feeds(self, state=True):
        ps = dict(stock__state=True)
        if state is not None:
            ps.update(state=state)
        return StockFeed.objects.select_related("stock").filter(**ps)

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
