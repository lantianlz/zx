# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq
from django.db.models import F

from common import cache, debug
from www.misc.decorators import cache_required
from www.misc import consts
from www.toutiao.models import ArticleType, WeixinMp, Article


dict_err = {
    90100: u'公众号openid重复',
    90101: u'公众号名称重复',
    90102: u'公众号id重复',
    90103: u'类型名称重复',
    90104: u'类型域名重复',
    90105: u'找不到对应的头条类型',
}
dict_err.update(consts.G_DICT_ERROR)


class ArticleTypeBase(object):

    def __init__(self):
        pass

    def add_article_type(self, name, domain, sort_num=0):
        try:
            assert name and domain
        except:
            return 99800, dict_err.get(99800)

        if ArticleType.objects.filter(name=name):
            return 90103, dict_err.get(90103)

        if ArticleType.objects.filter(domain=domain):
            return 90104, dict_err.get(90104)

        at = ArticleType.objects.create(name=name, domain=domain, sort_num=sort_num)

        self.get_all_valid_article_type(must_update_cache=True)
        return 0, at

    @cache_required(cache_key='all_toutiao_article_type', expire=0, cache_config=cache.CACHE_STATIC)
    def get_all_valid_article_type(self, must_update_cache=False):
        return ArticleType.objects.filter(state=True)

    def get_article_types(self, state=None):
        objs = ArticleType.objects.all()

        if state is not None:
            objs = objs.filter(state=state)

        return objs

    def get_type_by_domain(self, domain):
        try:
            return ArticleType.objects.get(domain=domain)
        except ArticleType.DoesNotExist:
            return None

    def get_type_by_id(self, type_id, state=None):
        if not type_id:
            return None

        objs = ArticleType.objects.filter(id=type_id)

        if state:
            objs = objs.filter(state=state)

        if not objs:
            return None

        return objs[0]

    def modify_article_type(self, type_id, name, domain, sort_num=0, state=True):
        if None in (name, domain):
            return 99800, dict_err.get(99800)

        objs = ArticleType.objects.filter(id=type_id)
        if not objs:
            return 90105, dict_err.get(90105)

        objs = objs[0]

        temp = ArticleType.objects.filter(name=name)
        if temp and objs.id != temp[0].id:
            return 90103, dict_err.get(90103)

        temp = ArticleType.objects.filter(domain=domain)
        if temp and objs.id != temp[0].id:
            return 90104, dict_err.get(90104)

        try:
            objs.name = name
            objs.domain = domain
            objs.sort_num = sort_num
            objs.state = state
            objs.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        self.get_all_valid_article_type(must_update_cache=True)
        return 0, dict_err.get(0)


class WeixinMpBase(object):

    def __init__(self):
        pass

    def get_mp_info_by_open_id(self, open_id):

        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}
        resp = requests.get(u"http://weixin.sogou.com/gzh?openid=%s" % open_id, headers=headers)
        jq = pq(resp.text)
        name = jq("#weixinname").html().strip()
        weixin_id = jq(".txt-box>h4>span").html().split(u"：")[1].strip()
        des = jq(".sp-txt:eq(0)").html().strip()
        vip_info = (jq(".sp-txt:eq(1)").html() or '').strip()
        # img = jq(".img-box img").attr("extra").split("url=")[1].strip().replace("'", "")
        img = jq(".img-box img").attr("src").strip()
        qrimg = jq(".pos-box>img").attr("src").strip()

        return open_id, name, weixin_id, des, vip_info, img, qrimg

    def add_mp(self, open_id, name, weixin_id, des, vip_info, img, qrimg,
               article_type=None, is_silence=False, sort_num=0):

        try:
            assert open_id and name and weixin_id and des
        except:
            return 99800, dict_err.get(99800)

        if WeixinMp.objects.filter(open_id=open_id):
            return 90100, dict_err.get(90100)

        if WeixinMp.objects.filter(name=name):
            return 90101, dict_err.get(90101)

        if WeixinMp.objects.filter(weixin_id=weixin_id):
            return 90102, dict_err.get(90102)

        mp = WeixinMp.objects.create(open_id=open_id, name=name, weixin_id=weixin_id, des=des,
                                     vip_info=vip_info, img=img, qrimg=qrimg,
                                     article_type=article_type, is_silence=is_silence, sort_num=sort_num)
        return 0, mp

    def get_weixin_mp_by_id(self, weixin_mp_id, state=True):
        try:
            ps = dict(id=weixin_mp_id)
            if state is not None:
                ps.update(state=state)
            return WeixinMp.objects.get(**ps)
        except WeixinMp.DoesNotExist:
            return None


class ArticleBase(object):

    def __init__(self):
        pass

    def format_articles(self, articles):
        for article in articles:
            article.content = article.content.replace("data-src=", "src=")
        return articles

    def get_all_articles(self, state=True):
        ps = dict()
        if state is not None:
            ps.update(dict(state=state))
        return Article.objects.select_related("weixin_mp").filter(**ps)

    def get_articles_by_type(self, article_type):
        return Article.objects.select_related("weixin_mp").filter(article_type=article_type)

    def get_articles_by_weixin_mp(self, weixin_mp):
        return Article.objects.select_related("weixin_mp").filter(weixin_mp=weixin_mp)

    def get_article_by_id(self, article_id, state=True):
        try:
            ps = dict(id=article_id)
            if state is not None:
                ps.update(state=state)
            return Article.objects.select_related("weixin_mp").get(**ps)
        except Article.DoesNotExist:
            return None

    def get_newsest_articles_related(self, article):
        ps = dict(weixin_mp=article.weixin_mp)
        return Article.objects.filter(**ps).exclude(id=article.id).order_by("-create_time")

    def add_article_view_count(self, article_id):
        '''
        @note: 更新浏览次数
        '''
        Article.objects.filter(id=article_id).update(views_count=F('views_count') + 1)
