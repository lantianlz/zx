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
    city_id = models.IntegerField(verbose_name=u'城市信息', db_index=True, null=True)
    district_id = models.IntegerField(verbose_name=u'区信息', db_index=True, null=True)

    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)


class City(models.Model):
    location_type_choices = ((0, u'区域'), (1, u'省'), (2, u'市'), (3, u'区'))
    province_type_choices = ((0, u'省'), (1, u'自治区'), (2, u'直辖市'), (3, u'特别行政区'))

    area = models.CharField(max_length=32, null=True, db_index=True)
    province = models.CharField(max_length=32, null=True, db_index=True)
    city = models.CharField(max_length=32, null=True, db_index=True)
    district = models.CharField(max_length=32, null=True, db_index=True)
    pinyin = models.CharField(verbose_name=u'city对应的拼音', max_length=32, null=True, unique=True)
    pinyin_abbr = models.CharField(verbose_name=u'city对应的拼音缩写', max_length=32, null=True, unique=True)
    location_type = models.IntegerField(choices=location_type_choices, db_index=True, null=True)
    province_type = models.IntegerField(choices=province_type_choices, db_index=True, null=True)
    sort_num = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["-sort_num", "id"]

    def get_url(self):
        if self.location_type == 2:
            return '/kaihu/%s' % self.pinyin_abbr
        return ''
