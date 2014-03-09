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
    like_count = models.IntegerField(default=0)
    is_important = models.BooleanField(default=False)   # 是否是精华帖
    ip = models.CharField(max_length=32, null=True)
    is_hide_user = models.BooleanField(default=False)
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", '-like_count', "-last_answer_time"]

    def get_url(self):
        return u'/question/%s' % self.id

    def get_summary(self):
        """
        @attention: 通过内容获取摘要
        """
        from common import utils
        return utils.get_summary_from_html_by_sub(self.content)

    def get_user(self):
        from www.account.interface import UserBase
        user = UserBase().get_user_by_id(self.user_id)
        return user


class Answer(models.Model):
    from_user_id = models.CharField(verbose_name=u'回答者', max_length=32, db_index=True)
    to_user_id = models.CharField(verbose_name=u'提问者', max_length=32, db_index=True)
    content = models.TextField()
    question = models.ForeignKey(Question)
    sort_num = models.IntegerField(verbose_name=u'排序值', default=-999, db_index=True)
    like_count = models.IntegerField(verbose_name=u'赞的次数', default=0)
    ip = models.CharField(max_length=32, null=True)
    is_bad = models.BooleanField(default=False)  # 是否是无用回复，无用回复需要折叠
    state = models.BooleanField(default=True)
    create_time = models.DateTimeField(db_index=True, auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", "-like_count", "-id"]

    def get_from_user(self):
        from www.account.interface import UserBase
        user = UserBase().get_user_by_id(self.from_user_id)
        return user

    def get_summary(self):
        """
        @attention: 通过内容获取摘要
        """
        from common import utils
        return utils.get_summary_from_html_by_sub(self.content)


class AtAnswer(models.Model):
    answer = models.ForeignKey(Answer)
    user_id = models.CharField(max_length=36)

    class Meta:
        unique_together = [('user_id', 'answer')]
        ordering = ["-id"]


class QuestionType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=16, unique=True)
    domain = models.CharField(max_length=16, unique=True)
    sort_num = models.IntegerField(default=-999, db_index=True)
    state = models.BooleanField(default=True)

    def get_url(self):
        return u'/question/type/%s' % self.domain or self.value


class Like(models.Model):

    """
    @note: 喜欢
    """
    answer = models.ForeignKey(Answer)
    question = models.ForeignKey(Question)  # 冗余字段，用于改提问下所有的喜欢
    from_user_id = models.CharField(verbose_name=u'发起赞的人', max_length=32, db_index=True)
    to_user_id = models.CharField(verbose_name=u'被赞者', max_length=32, db_index=True)
    ip = models.IPAddressField(db_index=True)
    is_anonymous = models.BooleanField(verbose_name=u'是否匿名', db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id', ]

    def __unicode__(self):
        return '%s, %s' % (self.from_user_id, self.to_user_id)


class Tag(models.Model):

    """
    @note: 标签
    """
    name = models.CharField(max_length=16, unique=True)
    domain = models.CharField(max_length=16, unique=True)  # 自定义域名支持
    question_type = models.ForeignKey(QuestionType)
    img = models.CharField(max_length=128, default='')  # 子分类可能有图片
    sort_num = models.IntegerField(default=-999, db_index=True)
    is_show = models.BooleanField(default=True)  # 过滤的时候是否显示
    state = models.BooleanField(default=True)
    data_body = models.TextField(default='')

    class Meta:
        ordering = ['-sort_num', '-id']

    def __unicode__(self):
        return '%s' % self.id

    def get_url(self):
        # 标签
        return u'/question/topic/%s' % self.domain


class TagQuestion(models.Model):

    '''
    @note: 标签对应提问
    '''
    tag = models.ForeignKey('Tag')
    question = models.ForeignKey('Question')
    sort_num = models.IntegerField(default=-999, db_index=True)

    class Meta:
        unique_together = [("tag", "question")]
        ordering = ['-sort_num', '-id']

    def __unicode__(self):
        return '%s, %s' % (self.tag_id, self.question_id)
