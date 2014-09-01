# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
import datetime


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

    def get_short_name(self):
        import re
        p = re.compile(u'.+?证券', re.DOTALL | re.IGNORECASE)
        names = p.findall(self.name or "")
        if names:
            name = names[0]
            if len(name) > 5:
                name = name.replace(u"证券", u"")
            return name
        return self.name


class Department(models.Model):
    company = models.ForeignKey(Company)
    name = models.CharField(max_length=128, unique=True)
    unique_id = models.IntegerField(unique=True)
    des = models.TextField(null=True)
    cm_count = models.IntegerField(verbose_name=u'入驻客户经理数量', default=0, db_index=True)

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

    class Meta:
        ordering = ["-sort_num", "-cm_count", "id"]

    def get_url(self):
        return '/kaihu/department_detail/%s' % self.id

    def get_short_name(self):
        return self.name.replace(self.company.name, self.company.get_short_name()).replace(u"证券营业部", u"营业部")


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
    is_show = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-sort_num", "id"]

    def get_url(self):
        if self.location_type == 2:
            return 'http://%s.%s' % (self.pinyin_abbr, settings.SERVER_DOMAIN)
        return ''

    def get_city_name_for_seo(self):
        keys = [u"市", u"自治州", u"地区"]
        name = self.city
        for key in keys:
            name = name.replace(key, '')
        return name

    def get_baidu_search_url(self):
        return (u"http://www.baidu.com/s?wd=%s股票开户&rn=100" % self.get_city_name_for_seo()).encode("utf8")


class CustomerManager(models.Model):
    pay_type_choices = ((0, u'未付费'), (1, u'付费'))

    user_id = models.CharField(max_length=32, unique=True)
    city_id = models.IntegerField(verbose_name=u'城市信息', db_index=True)
    department = models.ForeignKey(Department)
    end_date = models.DateField(verbose_name=u'到期时间', db_index=True)
    vip_info = models.CharField(verbose_name=u'认证信息', max_length=64)
    pay_type = models.IntegerField(choices=pay_type_choices, db_index=True, default=0)

    img = models.CharField(verbose_name=u'个人真实照片', max_length=64, null=True)
    qq = models.CharField(verbose_name=u'qq号码', max_length=32, null=True)
    entry_time = models.DateField(verbose_name=u'入行时间', null=True)
    mobile = models.CharField(verbose_name=u'手机号', max_length=32, null=True)
    real_name = models.CharField(verbose_name=u'真实姓名', max_length=32, null=True)
    id_card = models.CharField(verbose_name=u'身份证', max_length=32, null=True)
    id_cert = models.CharField(verbose_name=u'从业资格证编号', max_length=32, null=True)
    des = models.TextField(verbose_name=u'个人简介', null=True)

    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pay_type", "-sort_num", "id"]


class FriendlyLink(models.Model):
    link_type_choices = ((0, u'开户子站单个城市的链接'), (1, u'开户子站home页链接'), (2, u'主站内页链接'), (3, u'主站首页链接'))

    name = models.CharField(max_length=32)
    href = models.CharField(max_length=128)
    city_id = models.IntegerField(verbose_name=u'城市信息', db_index=True, null=True)
    img = models.CharField(max_length=64, null=True)
    des = models.CharField(max_length=128, null=True)
    link_type = models.IntegerField(default=0, choices=link_type_choices)
    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = [("name", "city_id", 'link_type'), ]
        ordering = ["-sort_num", "id"]


class Article(models.Model):
    title = models.CharField(max_length=64, unique=True)
    content = models.TextField()

    city_id = models.IntegerField(verbose_name=u'城市信息', db_index=True)
    department_id = models.IntegerField(verbose_name=u'营业部信息', db_index=True, null=True)
    from_url = models.CharField(max_length=250, unique=True, null=True)

    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sort_num", "-id"]

    def get_url(self):
        return '/kaihu/article/%s' % self.id

    def get_summary(self):
        """
        @attention: 通过内容获取摘要
        """
        from common import utils
        return utils.get_summary_from_html_by_sub(self.content)


class News(models.Model):
    title = models.CharField(max_length=64, unique=True)
    content = models.TextField()
    department_name = models.CharField(max_length=32, db_index=True)
    from_url = models.CharField(max_length=250, unique=True)

    sort_num = models.IntegerField(default=0, db_index=True)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ["-sort_num", "-create_time", "-id"]

    def get_url(self):
        return '/kaihu/news/%s' % self.id

    def get_summary(self):
        """
        @attention: 通过内容获取摘要
        """
        from common import utils
        return utils.get_summary_from_html_by_sub(self.content)
