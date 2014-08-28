# -*- coding: utf-8 -*-

import requests
from pyquery import PyQuery as pq

from common import cache
from www.misc.decorators import cache_required
from www.misc import consts
from www.toutiao.models import ArticleType, WeixinMp, Article


dict_err = {
    90100: u'公众号openid重复',
    90101: u'公众号名称重复',
    90102: u'公众号id重复',
    90103: u'类型名称重复',
    90104: u'类型域名重复',
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
        img = jq(".img-box img").attr("extra").split("url=")[1].strip().replace("'", "")
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


class ArticleBase(object):

    def __init__(self):
        pass

    def get_all_articles(self, state=True):
        ps = dict()
        if state is not None:
            ps.update(dict(state=state))
        return Article.objects.select_related("weixin_mp").filter(**ps)
