# -*- coding: utf-8 -*-

import time
import random
import requests
import json
import logging
from django.conf import settings

from common import cache, debug
from www.misc import consts
from www.question.interface import QuestionBase


dict_err = {
    60100: u'暂无绑定的设备，请取消关注公众号后重新扫描二维码',
}
dict_err.update(consts.G_DICT_ERROR)


weixin_api_url = 'https://api.weixin.qq.com'
dict_weixin_app = {
    'zhixuan_test': {'app_id': 'wx00d185b89113874f', 'app_secret': 'dce7dca2d686edc52e61246a0630fd73', 'app_type': 'gh_4fae99286289',
                     'token': 'zhixuan_test', 'url': ''},
    'zhixuan': {'app_id': '', 'app_secret': '', 'app_type': '',
                'token': 'zhixuan', 'url': ''},
}


class WexinBase(object):

    def __init__(self):
        self.cache = cache.Cache()

    def __del__(self):
        del self.cache

    def get_base_text_response(self):
        '''
        @note: 文字信息模板
        '''
        return u'''
        <xml>
        <ToUserName><![CDATA[%(to_user)s]]></ToUserName>
        <FromUserName><![CDATA[%(from_user)s]]></FromUserName>
        <CreateTime>%(timestamp)s</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[%(content)s]]></Content>
        </xml>
        '''

    def get_base_base_news_response(self, items=None):
        '''
        @note: 图文信息模板
        '''
        return u'''
        <xml>
        <ToUserName><![CDATA[%(to_user)s]]></ToUserName>
        <FromUserName><![CDATA[%(from_user)s]]></FromUserName>
        <CreateTime>%(timestamp)s</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>%(articles_count)s</ArticleCount>
        <Articles>
        ''' + (items or self.get_base_news_item_response()) + \
            '''
        </Articles>
        </xml>
        '''

    def get_base_news_item_response(self):
        return u'''
        <item>
        <Title><![CDATA[%(title)s]]></Title> 
        <Description><![CDATA[%(des)s]]></Description>
        <PicUrl><![CDATA[%(picurl)s]]></PicUrl>
        <Url><![CDATA[%(hrefurl)s]]></Url>
        </item>
        '''

    def get_base_content_response(self, to_user, from_user, content):
        base_xml = self.get_base_text_response()
        return base_xml % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()),
                               content=content)

    def get_error_response(self, to_user, from_user, error_info):
        base_xml = self.get_base_text_response()
        return base_xml % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()),
                               content=error_info)

    def get_subscribe_event_response(self, to_user, from_user):
        content = (u'欢迎关注智选，这里有最新鲜的投资资讯、最睿智的投资问答。\n'
                   u'点击底部菜单立即开启智选之旅，智选定不负你的关注')
        return self.get_base_content_response(to_user, from_user,
                                              content=content)

    def get_hotest_response(self, to_user, from_user):
        items = ''
        for question in QuestionBase().get_all_important_question()[:4]:
            items += (self.get_base_news_item_response() % dict(title=question.iq_title.replace('%', '%%'), des='', picurl=question.img,
                                                                hrefurl='%s%s' % (settings.MAIN_DOMAIN, question.get_url())))

        base_xml = self.get_base_base_news_response(items)
        return base_xml % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()), articles_count=4)

    def format_input_xml(self, xml):
        '''
        @note: 标签替换为小写，以便pyquery能识别
        '''
        for key in ['ToUserName>', 'FromUserName>', 'CreateTime>', 'MsgType>', 'Content>', 'MsgId>', 'PicUrl>',
                    'MediaId>', 'Format>', 'ThumbMediaId>', 'Event>', 'EventKey>', 'Ticket>', 'Recognition>',
                    'DeviceID>', 'SessionID>', 'DeviceType>', 'OpenID>']:
            xml = xml.replace(key, key.lower())
        return xml

    def get_response(self, xml):
        from pyquery import PyQuery as pq
        xml = self.format_input_xml(xml)
        jq = pq(xml)
        to_user = jq('tousername')[0].text
        from_user = jq('fromusername')[0].text
        events = jq('event')
        app_key = self.get_app_key_by_app_type(to_user)
        logging.error(u'收到一个来自app：%s 的请求' % app_key)

        # click事件
        if events:
            event = events[0].text.lower()
            if event in ('subscribe',):
                return self.get_subscribe_event_response(to_user, from_user)
            elif event in ('click'):
                event_key = jq('eventkey')[0].text.lower()
                if event_key == 'hotest':
                    return self.get_hotest_response(to_user, from_user)

        # 语音识别上传
        recognitions = jq('recognition')
        if recognitions:
            recognition = recognitions[0].text.lower()
            logging.error(u'收到用户发送的语音数据，内容如下：%s' % recognition)
            if u'干货' in recognition or u'精选' in recognition or u'来一发' in recognition:
                questions = QuestionBase().get_all_important_question()
                question = questions[random.randint(0, len(questions))]
                items = self.get_base_news_item_response() % dict(title=question.iq_title.replace('%', '%%'), des='', picurl=question.img,
                                                                  hrefurl='%s%s' % (settings.MAIN_DOMAIN, question.get_url()))

                return self.get_base_base_news_response(items) % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()), articles_count=1)

        # 文字识别
        msg_types = jq('msgtype')
        if msg_types:
            msg_type = msg_types[0].text
            if msg_type == 'text':
                content = jq('content')[0].text.strip()
                logging.error(u'收到用户发送的文本数据，内容如下：%s' % content)

    def get_app_key_by_app_type(self, app_type):
        for key in dict_weixin_app:
            if dict_weixin_app[key]['app_type'] == app_type:
                return key
        raise Exception, u'app_key not found by: %s' % app_type

    def send_msg_to_weixin(self, content, to_user, app_key, msg_type='text', img_info=''):
        '''
        @note: 发送信息给微信
        '''
        # json的dumps字符串中中文微信不识别，修改为直接构造
        if msg_type == 'text':
            data = u'{"text": {"content": "%s"}, "msgtype": "%s", "touser": "%s"}' % (content, msg_type, to_user)
        else:
            data = u'{"news":{"articles": %s}, "msgtype":"%s", "touser": "%s"}' % (img_info, msg_type, to_user)

        data = data.encode('utf8')

        access_token = self.get_weixin_access_token(app_key)
        url = '%s/cgi-bin/message/custom/send?access_token=%s' % (weixin_api_url, access_token)
        r = requests.post(url, data=data, timeout=30)
        r.raise_for_status()
        content = json.loads(r.content)
        logging.error('send msg to weixin resp is %s' % (content,))

    def get_weixin_access_token(self, app_key):
        # 本地调试模式不走缓存
        if settings.LOCAL_FLAG:
            key = 'weixin_access_token_for_%s' % app_key
            access_token = self.cache.get(key)
            if access_token is None:
                access_token, expires_in = self.get_weixin_access_token_directly(app_key)
                if access_token:
                    self.cache.set(key, access_token, int(expires_in))
        else:
            access_token, expires_in = self.get_weixin_access_token_directly(app_key)
        return access_token

    def get_weixin_access_token_directly(self, app_key):
        access_token, expires_in = '', 0
        content = ''
        url = '%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (weixin_api_url, dict_weixin_app[app_key]['app_id'],
                                                                                    dict_weixin_app[app_key]['app_secret'])
        try:
            r = requests.get(url, timeout=20)
            content = r.content
            r.raise_for_status()
            content = json.loads(content)
            access_token = content['access_token']
            expires_in = content['expires_in']
        except Exception, e:
            logging.error(u'get_weixin_access_token rep is %s' % content)
            logging.error(debug.get_debug_detail(e))
        assert access_token
        return access_token, expires_in
