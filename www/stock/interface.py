# -*- coding: utf-8 -*-

import datetime
from django.db import transaction

from common import debug
from www.misc import consts
from www.stock.models import Stock, StockFeed


dict_err = {
    80100: u'股票不存在',
    80101: u'股票名称或者代码已经存在',
}
dict_err.update(consts.G_DICT_ERROR)
DEFAULT_DB = "default"


def stock_required(func):
    def _decorator(self, stock_id_or_object, *args, **kwargs):
        stock = stock_id_or_object
        if not isinstance(stock_id_or_object, Stock):
            try:
                stock = Stock.objects.get(id=stock_id_or_object, state=True)
            except Stock.DoesNotExist:
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

    def create_stock(self, name, code, belong_board, belong_market, img, des=None, sort_num=0, state=False):
        try:
            assert name and code and belong_board and belong_market and img
        except:
            return 99800, dict_err.get(99800)
        if Stock.objects.filter(name=name) or Stock.objects.filter(code=code):
            return 80101, dict_err.get(80101)

        try:
            stock = Stock.objects.create(
                name=name, code=code, belong_board=belong_board, belong_market=belong_market,
                img=img, des=des, sort_num=sort_num, state=state
            )
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, stock


class StockFeedBase(object):

    def __init__(self):
        pass

    def format_stock_feeds(self, stock_feeds):
        for stock_feed in stock_feeds:
            stock_feed.answer_content_length = len(stock_feed.answer_content)
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
