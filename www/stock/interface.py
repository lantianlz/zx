# -*- coding: utf-8 -*-

import datetime
from django.db import transaction

from common import debug
from www.misc import consts
from www.stock.models import Stock, StockFeed


dict_err = {
    80100: u'股票不存在',
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


class StockFeedBase(object):

    def __init__(self):
        pass

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
