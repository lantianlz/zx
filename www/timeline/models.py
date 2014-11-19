# -*- coding: utf-8 -*-

from django.db import models


class UserFollow(models.Model):
    source_choices = ((0, u'站内直接关注'), (1, u'新浪微博关注'))

    from_user_id = models.CharField(max_length=32, db_index=True)
    to_user_id = models.CharField(max_length=32, db_index=True)
    is_two_way = models.BooleanField()  # 是否是双向关注
    source = models.IntegerField(default=0, choices=source_choices)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        unique_together = ("from_user_id", "to_user_id")
        ordering = ['-id']


class Feed(models.Model):
    feed_type_choices = ((1, u'提问'), (2, u'赞'), (3, u'回答'), (4, u"股票动态"))
    source_choices = ((0, u'关注的用户产生内容'), (1, u'关注股票产生的内容'), (2, u'关注话题产生的内容'))
    state_choices = ((0, u'已删除'), (1, u'系统发布'), (2, u'用户发布'))

    user_id = models.CharField(max_length=32, db_index=True)  # 用户产生的内容的时候为user_id，股票产生的内容的时候为stock_id
    content = models.CharField(max_length=1024, null=True)
    obj_id = models.CharField(max_length=64, default=0)  # 对象的id

    feed_type = models.IntegerField(choices=feed_type_choices, db_index=True)
    source = models.IntegerField(default=0, choices=source_choices, db_index=True)
    state = models.IntegerField(default=1, choices=state_choices, db_index=True)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ['-id']
