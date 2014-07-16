# -*- coding: utf-8 -*-


import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

import datetime
import re
import requests
from pyquery import PyQuery as pq
from pprint import pprint
from www.stock.models import Stock, StockFeed
from www.stock import interface


def get_shanghai_feed():
    def _replace_html_tag(text):
        tag_s = re.compile('<[^\/]+?>')
        tag_e = re.compile('</\w+?>')
        text = tag_s.sub('', text)
        text = tag_e.sub(' ', text)
        return text

    def _get_time(origin_time, pre_time):
        now = datetime.datetime.now()
        pre_year = int(pre_time.strftime("%Y"))
        pre_month = int(pre_time.strftime("%m"))
        if u"月" in origin_time:
            month = int(origin_time.split(u"月")[0])
            year = pre_year if month <= pre_month else pre_year - 1
            return datetime.datetime.strptime((u"%s年%s" % (year, origin_time)).encode("utf8"), '%Y年%m月%d日 %H:%M')
        if u"分钟" in origin_time:
            minute = int(origin_time.split(u"分钟")[0])
            return now - datetime.timedelta(minutes=minute)
        if u"小时" in origin_time:
            hour = int(origin_time.split(u"小时")[0])
            return now - datetime.timedelta(hours=hour)

        raise Exception, (u"time error:%s" % origin_time).encode("utf8")

    # url = "http://sns.sseinfo.com/ajax/userfeeds.do?typeCode=company&type=11&pageSize=10&uid=65&page=1"
    # resp = requests.get(url)
    # text = resp.text
    # print text.encode("utf8")
    text = u"""
    <div class="m_feed_item" id="item-54508">
                <div class="m_feed_detail" style="border: none;">
                    <div class="m_feed_face">
                        <a rel="face" uid="16995" href="user.do?uid=16995" title="TW1314"><img title="TW1314" alt="" width="40" height="40" src="http://rs.sns.sseinfo.com/resources/images/avatar/201403/16995.png"></a>
                        <p>TW1314</p>
                    </div>
                    <div class="m_feed_cnt">
                        <div class="m_feed_info">
                            <div class="index_ico ask_ico"></div>
                        </div>
                        <div class="m_feed_txt">
                            <a href='user.do?uid=65' >@浦发银行(600000)</a>您好，观察到公司一季度资本充足率和核心资本充足率双降是什么原因呢，会影响到公司发展吗？
                        </div>
                        <div class="m_feed_media">
                            
                        </div>
                    <div class="m_feed_func">
                        
                        
                        <div class="m_feed_handle">
                            
                        </div>
                        
                            <div class="m_feed_from">
                                <span>07月02日 16:00</span>
                                <em>来自</em>
                                        <a href="javascript:;">网站</a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 当前提问的回答存在，则显示 -->
                <div class="m_feed_detail m_qa">
                    <div class="a_tit"><em class="S_line1_c">◆</em><span class="S_bg5_c">◆</span></div>
                    <div class="m_feed_face">
                        <a rel="tag" class="ansface" uid="65" href="user.do?uid=65" title="65"><img title="浦发银行" alt="" width="30" height="30" src="http://rs.sns.sseinfo.com/resources/images/avatar/company/600000.png"></a>
                        <p>浦发银行</p>
                    </div>
                    <div class="m_feed_cnt">
                        <div class="m_feed_info">
                            <div class="index_ico answer_ico"></div>
                        </div>
                        <div class="m_feed_txt" id="m_feed_txt-54508">
                            按照银监会《商业银行资本管理办法（试行）》的统计口径一季度末资本充足率和核心资本充足率是上升的，按照老办法统计口径是有所下降。目前公司资本充足率和核心资本充足率均在监管最低要求之上，不会对公司正常经营产生负面影响。
                        </div>
                        <div class="m_feed_media">
                            
                        </div>
                </div>
                <div class="m_feed_func top10" style="margin-left: 70px;">
                            <div class="m_feed_handle">
                            <a href="javascript:love(54508);" id="love-54508"><em  ></em></a>
                            <i class="m_txt">|</i>
                            
                            <a href="javascript:favorite(54508);" id="favorite-54508">收藏 </a>
                            <i class="m_txt">|</i>
                            <a href="javascript:comment(54508);">评论<span id="totalNum_54508"></span></a>
                        </div>
                        <div class="m_feed_share">
                            <!-- 分享插件 -->
                            <i class="index_ico weibo_ico" rel="sina-54508" onclick="toWeiBo('sina', 'TW1314', 54508);">　</i>
                            <i class="index_ico qq_ico" rel="tx-54508" onclick="toWeiBo('tencent', 'TW1314', 54508);"></i>
                        </div>
                        <div class="m_feed_from" style="padding-left: 35px;">
                        <span>07月03日 10:47</span>
                            <em>来自</em>
        <a href="javascript:;">网站</a>
                        </div>
                        <div class="m_feed_comments" id="comment_list_54508"></div>
                    </div>
                
            </div>
                </div>
            
        
        
        
            
            
            <div class="m_feed_item" id="item-54361">
                <div class="m_feed_detail" style="border: none;">
                    <div class="m_feed_face">
                        <a rel="face" uid="7558" href="user.do?uid=7558" title="孔乙己"><img title="孔乙己" alt="" width="40" height="40" src="http://rs.sns.sseinfo.com/resources/images/avatar/201308/7558.png"></a>
                        <p>孔乙己</p>
                    </div>
                    <div class="m_feed_cnt">
                        <div class="m_feed_info">
                            <div class="index_ico ask_ico"></div>
                        </div>
                        <div class="m_feed_txt">
                            <a href='user.do?uid=65' >@浦发银行(600000)</a>贵公司主要是从那些方面考虑而一次性核销不良36亿？谢谢
                        </div>
                        <div class="m_feed_media">
                            
                        </div>
                    <div class="m_feed_func">
                        
                        
                        <div class="m_feed_handle">
                            
                        </div>
                        
                            <div class="m_feed_from">
                                <span>07月01日 17:14</span>
                                <em>来自</em>
                                
                                    
                                    
                                        <a href="javascript:;">网站</a>
                                    
                                    
                                    
                                    
                                    
                                
                            </div>
                        </div>
                    </div>
                </div>
                <!-- 当前提问的回答存在，则显示 -->
                <div class="m_feed_detail m_qa">
                    <div class="a_tit"><em class="S_line1_c">◆</em><span class="S_bg5_c">◆</span></div>
                    <div class="m_feed_face">
                        <a rel="tag" class="ansface" uid="65" href="user.do?uid=65" title="65"><img title="浦发银行" alt="" width="30" height="30" src="http://rs.sns.sseinfo.com/resources/images/avatar/company/600000.png"></a>
                        <p>浦发银行</p>
                    </div>
                    <div class="m_feed_cnt">
                        <div class="m_feed_info">
                            <div class="index_ico answer_ico"></div>
                        </div>
                        <div class="m_feed_txt" id="m_feed_txt-54361">
                            近些年以来，商业银行整体信贷资产质量压力加大，不良贷款呈现双升态势。公司在除了加大现金清收力度外，适当采取信贷资产损失核销，目的是为进一步加大风险防控和化解力度，确保资产质量稳定。
                        </div>
                        <div class="m_feed_media">
                            
                        </div>
                </div>
                <div class="m_feed_func top10" style="margin-left: 70px;">
                            <div class="m_feed_handle">
                            <a href="javascript:love(54361);" id="love-54361"><em  ></em></a>
                            <i class="m_txt">|</i>
                            
                            <a href="javascript:favorite(54361);" id="favorite-54361">收藏 </a>
                            <i class="m_txt">|</i>
                            <a href="javascript:comment(54361);">评论<span id="totalNum_54361"></span></a>
                        </div>
                        <div class="m_feed_share">
                            <!-- 分享插件 -->
                            <i class="index_ico weibo_ico" rel="sina-54361" onclick="toWeiBo('sina', '孔乙己', 54361);">　</i>
                            <i class="index_ico qq_ico" rel="tx-54361" onclick="toWeiBo('tencent', '孔乙己', 54361);"></i>
                        </div>
                        <div class="m_feed_from" style="padding-left: 35px;">
                        <span>07月03日 10:17</span>
                            <em>来自</em>
                            



    
    
        <a href="javascript:;">网站</a>
    
    


                        </div>
                        <div class="m_feed_comments" id="comment_list_54361"></div>
                    </div>
                
            </div>
                </div>
    """

    jq = pq(text)
    feeds = jq('.m_feed_item')
    now = datetime.datetime.now()
    for feed in feeds:
        feed = pq(feed)
        question_content = _replace_html_tag(feed(".m_feed_txt").eq(0).html()).strip()
        answer_content = _replace_html_tag(feed(".m_feed_txt").eq(1).html()).strip()

        question_time = _get_time(feed(".m_feed_from:eq(0) span").html(), now)
        answer_time = _get_time(feed(".m_feed_from:eq(1) span").html(), now)

        print question_content.encode("utf8")
        print answer_content.encode("utf8")
        print question_time, answer_time

        interface.StockFeedBase().create_feed(65, question_content, answer_content, belong_market=0, create_time=answer_time,
                                              create_question_time=question_time)


def init_stock_feed():
    get_shanghai_feed()
    print 'ok'


if __name__ == '__main__':
    init_stock_feed()
