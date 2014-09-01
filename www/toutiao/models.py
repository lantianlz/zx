# -*- coding: utf-8 -*-

from django.db import models
import datetime


class ArticleType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    domain = models.CharField(max_length=16, unique=True)
    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-sort_num", "-id"]

    def get_url(self):
        return '/toutiao/type/%s' % self.domain


class WeixinMp(models.Model):
    open_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=64, unique=True)
    weixin_id = models.CharField(max_length=64, unique=True)
    des = models.TextField(null=True)
    vip_info = models.CharField(max_length=256, null=True)
    img = models.CharField(max_length=256)
    qrimg = models.CharField(max_length=256)  # 二维码地址
    is_silence = models.BooleanField(default=True, db_index=True)
    sort_num = models.IntegerField(default=0, db_index=True)
    article_type = models.ForeignKey(ArticleType, null=True)
    state = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-sort_num", "-id"]

    def get_url(self):
        return '/toutiao/mp/%s' % self.id


class Article(models.Model):
    title = models.CharField(max_length=64, unique=True)
    content = models.TextField()

    article_type = models.ForeignKey(ArticleType, null=True)
    weixin_mp = models.ForeignKey(WeixinMp)
    from_url = models.CharField(max_length=250, unique=True, null=True)
    is_silence = models.BooleanField(default=False, db_index=True)  # 是否显示在首页中
    img = models.CharField(max_length=256)
    views_count = models.IntegerField(default=0)
    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ["-sort_num", "-create_time"]

    def get_url(self):
        return '/toutiao/article/%s' % self.id

    def get_summary(self):
        """
        @attention: 通过内容获取摘要
        """
        from common import utils
        return utils.get_summary_from_html_by_sub(self.content)


class BanKey(models.Model):

    """
    @note：抓取禁止关键词维护
    """
    key = models.CharField(max_length=16, unique=True)
