# -*- coding: utf-8 -*-

from django.db import models


class Zhuanti(models.Model):

    title = models.CharField(max_length=64, unique=True)
    summary = models.TextField()
    img = models.CharField(max_length=128)
    author_name = models.CharField(max_length=128, default=u"智选")  # 作者姓名
    domain = models.CharField(max_length=16, unique=True)  # 模板名称同样使用这个字段
    # tempalte_name = models.CharField(max_length=64, unique=True)
    sort_num = models.IntegerField(default=0, db_index=True)

    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", '-id']

    def __unicode__(self):
        return '%s, %s' % (self.id, self.title)

    def get_url(self):
        return u'/zt/%s' % self.domain
