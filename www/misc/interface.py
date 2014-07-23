# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from www.misc import consts
from www.misc.decorators import cache_required


dict_err = {
}
dict_err.update(consts.G_DICT_ERROR)


@cache_required(cache_key='sitemap', expire=1800)
def generate_sitemap(must_update_cache=False):
    site_xml = u"""<?xml version="1.0" encoding="utf-8"?>
    <urlset>
        %s
    </urlset>
    """
    urls = ''
    data = get_sitemap_url()
    for d in data:
        urls +=  u"""
        <url>
           <loc>%s</loc>
           <lastmod>%s</lastmod>
           <changefreq>daily</changefreq>
           <priority>0.5</priority>
       </url>
       """ % (d[0], d[1])
    return site_xml % urls


def get_sitemap_url():
    from www.question.interface import TopicBase
    from www.question.models import Question
    from www.stock.models import StockFeed

    data = []
    for question in Question.objects.filter(state=True).order_by('-id'):
        data.append([u'%s/question/%s\n' % (settings.MAIN_DOMAIN, question.id), question.last_answer_time])

    for topic in TopicBase().get_all_topics_for_show():
        data.append([u'%s/topic/%s\n' % (settings.MAIN_DOMAIN, topic.domain), datetime.datetime.now().strftime('%Y-%m-%d')])

    for stock_feed in StockFeed.objects.filter(state=True).order_by("-create_time")[:2000]:
        data.append([u'%s%s\n' % (settings.MAIN_DOMAIN, stock_feed.get_url()), stock_feed.create_time.strftime('%Y-%m-%d')])

    return data
