# -*- coding: utf-8 -*-

from django.db import models


class Question(models.Model):
    user_id = models.CharField(max_length=32, db_index=True)
    title = models.CharField(max_length=128)
    content = models.TextField()

    views_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    last_answer_time = models.DateTimeField(db_index=True)
    sort_num = models.IntegerField(default=-999, db_index=True)
    zan_num = models.IntegerField(default=0)
    ip = models.CharField(max_length=32, null=True)
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-sort_num", "-last_answer_time"]


class Answer(models.Model):
    user_id = models.CharField(max_length=32, db_index=True)
    content = models.TextField()

    question = models.ForeignKey(Question)
    sort_num = models.IntegerField(default=-999, db_index=True)
    zan_num = models.IntegerField(default=0)
    ip = models.CharField(max_length=32, null=True)
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-sort_num", "-id"]
