# -*- coding: utf-8 -*-

from django.db import models


class UserFollow(models.Model):
    source_tuple = ((0, u'站内直接关注'), (1, u'新浪微博关注'))

    from_user_id = models.CharField(max_length=32, db_index=True)
    to_user_id = models.CharField(max_length=32, db_index=True)
    is_two_way = models.BooleanField()  # 是否是双向关注
    source = models.IntegerField(default=0, choices=source_tuple)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        unique_together = ("from_user_id", "to_user_id")
        ordering = ['-id']
