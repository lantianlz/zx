# -*- coding: utf-8 -*-

from django.db import models


class UserFollow(models.Model):
    from_user_id = models.CharField(max_length=32, db_index=True)
    to_user_id = models.CharField(max_length=32, db_index=True)
    is_two_way = models.BooleanField()  # 是否是双向关注
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        unique_together = ("from_user_id", "to_user_id")
        ordering = ['-id']
