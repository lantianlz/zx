# -*- coding: utf-8 -*-

from django.db import models


class Question(models.Model):
    user_id = models.CharField(max_length=32, db_index=True)
    title = models.CharField(max_length=128)
    content = models.TextField()
    question_type = models.ForeignKey('QuestionType')
    views_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    last_answer_time = models.DateTimeField(db_index=True)
    sort_num = models.IntegerField(default=-999, db_index=True)
    zan_num = models.IntegerField(default=0)
    ip = models.CharField(max_length=32, null=True)
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", '-zan_num', "-last_answer_time"]

    def get_url(self):
        return u'/question/question_detail/%s' % self.id

    def get_summary(self):
        maxlength = 100
        return (self.content[:maxlength] + u'...') if self.content.__len__() > maxlength else self.content

    @property
    def user(self):
        from www.account.interface import UserBase
        user = UserBase().get_user_by_id(self.user_id)
        return user


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


class QuestionType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=16, unique=True)
    domain = models.CharField(max_length=16, unique=True)
    sort_num = models.IntegerField(default=-999, db_index=True)
    state = models.BooleanField(default=True)

    def get_url(self):
        return u'/question/type/%s' % self.domain or self.value
