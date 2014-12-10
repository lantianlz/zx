# -*- coding: utf-8 -*-

from django.db import models


class Stock(models.Model):
    board_choices = ((0, u'主板'), (1, u"中小企业板"), (2, u"创业板"), (3, u"B股"), (4, u"其他"))
    market_choices = ((0, u'沪股市'), (1, u"深圳股市"))

    name = models.CharField(max_length=64, unique=True)
    origin_uid = models.CharField(max_length=16, unique=True)
    code = models.CharField(max_length=16, unique=True)
    des = models.TextField(null=True)
    main_business = models.TextField(null=True)  # 主营业务
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
        return u'/stock/%s' % self.code


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
        ordering = ["-create_time", "id"]

    def get_url(self):
        return u'/stock/feed/%s' % self.id


class StockFollow(models.Model):
    source_choices = ((0, u'站内直接关注'), (1, u''))

    user_id = models.CharField(max_length=32, db_index=True)
    stock = models.ForeignKey(Stock)
    source = models.IntegerField(default=0, choices=source_choices)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        unique_together = ("user_id", "stock")
        ordering = ['-id']


class StockData(models.Model):
    stock = models.ForeignKey("Stock")
    date = models.DateField(db_index=True)
    market_value = models.FloatField(default=0)
    open_price = models.FloatField()
    close_price = models.FloatField()
    low_price = models.FloatField()
    high_price = models.FloatField()
    volume = models.FloatField(db_index=True)  # 成交手数量
    turnover = models.FloatField(db_index=True)  # 成交金额
    turnover_rate_to_all = models.FloatField(db_index=True, default=0)  # 占总交易额的百分比
    turnover_rate_to_all_change_per_day = models.FloatField(db_index=True, default=0)  # 占总比的变化
    turnover_change_pre_day = models.FloatField(db_index=True, default=0)  # 相对于前一天的变化的百分比

    class Meta:
        unique_together = ("stock", "date")
        ordering = ['-date', '-id']

    def __unicode__(self):
        return "%s:%s" % (self.id, self.date)


class Kind(models.Model):

    """
    @note: 行业分类
    """
    group_choices = ((0, u"行业"), (1, u"概念"))

    name = models.CharField(max_length=64, unique=True)
    group = models.IntegerField(db_index=True, default=0, choices=group_choices)
    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)


class StockKind(models.Model):

    """
    @note: 股票对应的行业
    """
    stock = models.ForeignKey("Stock")
    kind = models.ForeignKey("Kind")


class KindData(models.Model):
    kind = models.ForeignKey("Kind")
    date = models.DateField(db_index=True)
    turnover = models.FloatField(db_index=True)  # 成交金额
    turnover_rate_to_all = models.FloatField(db_index=True, default=0)  # 占总交易额的百分比
    turnover_rate_to_all_change_per_day = models.FloatField(db_index=True, default=0)  # 占总比的变化
    turnover_change_pre_day = models.FloatField(db_index=True, default=0)  # 相对于前一天的变化的百分比

    class Meta:
        unique_together = ("kind", "date")
        ordering = ['-date', '-id']
