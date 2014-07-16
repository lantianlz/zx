# -*- coding: utf-8 -*-

from django.db import models


class Stock(models.Model):
    board_choices = ((0, u'主板'), (1, u"中小板"), (2, u"创业板"), (3, u"B股"), (4, u"其他"))
    market_choices = ((0, u'沪股市'), (1, u"深圳股市"))

    name = models.CharField(max_length=64, unique=True)
    origin_uid = models.CharField(max_length=16, unique=True)
    code = models.CharField(max_length=16, unique=True)
    des = models.TextField(null=True)
    belong_board = models.IntegerField(choices=board_choices)   # 所属板块
    belong_market = models.IntegerField(choices=market_choices)   # 所属交易所

    img = models.CharField(max_length=128)
    feed_count = models.IntegerField(default=0, db_index=True)
    following_count = models.IntegerField(default=0, db_index=True)
    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", '-feed_count']

    def get_url(self):
        return u'/stock/%s' % self.id


class StockFeed(models.Model):
    market_choices = ((0, u'沪股市'), (1, u"深圳股市"))

    stock = models.ForeignKey(Stock)
    question_content = models.CharField(max_length=1024)
    answer_content = models.TextField()
    origin_id = models.CharField(max_length=16, unique=True, null=True)  # 对象的id
    belong_market = models.IntegerField(choices=market_choices)   # 所属交易所

    state = models.BooleanField(default=True, db_index=True)
    create_question_time = models.DateTimeField(db_index=True, null=True)
    create_time = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-id"]

    def get_url(self):
        return u'/stock/feed/%s' % self.id
