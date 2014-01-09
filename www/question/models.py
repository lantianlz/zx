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
    is_hide_user = models.BooleanField(default=False)
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", '-zan_num', "-last_answer_time"]

    def get_url(self):
        return u'/question/question_detail/%s' % self.id

    def get_summary(self):
        """
        @attention: 通过内容获取摘要
        """
        import re

        summary = ''
        # 提取标签中的文字
        r = u'<.+?>([^\/\\\&\<\>]+?)</\w+?>'
        p = re.compile(r, re.DOTALL | re.IGNORECASE)
        rs = p.findall(self.content)
        for s in rs:
            if summary.__len__() > 100:
                summary += '......'
                break
            if s:
                summary += s
        # 没有标签的
        if not summary:
            r = u'[\u4e00-\u9fa5\w]+'
            p = re.compile(r, re.DOTALL | re.IGNORECASE)
            rs = p.findall(self.content)
            for s in rs:
                if summary.__len__() > 100:
                    summary += '......'
                    break
                if s:
                    summary += s

        return summary

    def get_user(self):
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
