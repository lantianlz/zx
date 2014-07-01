# -*- coding: utf-8 -*-

from django.db import models


class ZhuanTi(models.Model):

    state_choices = ((0, u'无效用户'), (1, u'有效用户'), (2, u'内部成员'), )

    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s, %s' % (self.id, self.title)
