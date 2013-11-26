# -*- coding: utf-8 -*-

from django.db import models


class User(models.Model):
    state_choices = ((0, u'无效用户'), (1, u'有效用户'))
    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    email = models.CharField(max_length=64, unique=True)
    mobilenumber = models.CharField(max_length=32, null=True, unique=True)
    username = models.CharField(max_length=32, null=True, unique=True)
    password = models.CharField(max_length=128)

    state = models.IntergerField(default=1, choices=state_choices, db_index=True)
    last_login = models.DateTimeField(db_index=True)
    create_time = models.DateTimeField(db_index=True)


class Profile(models.Model):
    gender_choices = ((0, u'未知'), (1, u'男'), (2, u'女'))
    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    nick = models.CharField(max_length=32, unique=True)

    birthday = models.DateField(default='2000-01-01', db_index=True)
    gender = models.IntergerField(default=0, choices=gender_choices, db_index=True)
    avatar = models.CharField(max_length=256, default='')
    email_verified = models.BoolField(default=False)
    mobile_verified = models.BoolField(default=False)
    ip = models.CharField(max_length=32)

    create_time = models.DateTimeField(db_index=True)


class UserChangeLog(models.Model):
    change_type_choices = ((0, u'密码'), (1, u'邮箱'), (2, u'手机'))
    change_type = models.IntergerField(choices=change_type_choices)
    before = models.CharField(max_length=64, db_index=True)
    to = models.CharField(max_length=64, db_index=True)
    ip = models.CharField(max_length=32)
    create_time = models.DateTimeField(db_index=True)


class LastActive(models.Model):
    pass
