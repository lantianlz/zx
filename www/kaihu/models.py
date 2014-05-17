# -*- coding: utf-8 -*-

from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=64, unique=True)
    unique_id = models.IntegerField(unique=True)
    des = models.TextField(null=True)

    img = models.CharField(max_length=128)
    img_alt = models.CharField(max_length=256, null=True)
    department_count = models.IntegerField(default=0, db_index=True)
    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)


class Department(models.Model):
    company = models.ForeignKey(Company)
    name = models.CharField(max_length=128, unique=True)
    unique_id = models.IntegerField(unique=True)
    des = models.TextField(null=True)

    img = models.CharField(max_length=128)
    img_alt = models.CharField(max_length=256, null=True)
    addr = models.CharField(verbose_name=u'地址', max_length=512, null=True)
    tel = models.CharField(verbose_name=u'固定电话', max_length=32, null=True)
    manager_name = models.CharField(verbose_name=u'负责人姓名', max_length=16, null=True)
    zip_code = models.CharField(verbose_name=u'邮政编码', max_length=32, null=True)
    licence = models.CharField(verbose_name=u'评定等级like A0008', max_length=32, null=True, db_index=True)
    assess_date = models.DateField(verbose_name=u'评定日期', null=True)

    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)
