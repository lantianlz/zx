# -*- coding: utf-8 -*-


"""
@note: utils方法封装
@author: lizheng
@date: 2013-12-09
"""

import re
import datetime
import random
import requests
import json

from django.conf import settings


def uuid_without_dash():
    import uuid
    return str(uuid.uuid1()).replace('-', '')


def get_clientip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
        arr_ip = client_ip.split(',', 1)
        return arr_ip[0].strip()
    elif 'HTTP_X_REAL_IP' in request.META:
        return request.META['HTTP_X_REAL_IP']
    else:
        return request.META.get('REMOTE_ADDR', u'127.0.0.1')


def time_format(value):
    import time

    if not value:
        return 'datetime error'
    d = value
    if not isinstance(value, datetime.datetime):
        d = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    now_date = datetime.datetime.now()
    ds = time.time() - time.mktime(d.timetuple())  # 秒数
    # dd = now_date - d  # 日期相减对象
    if ds <= 5:
        return u'刚刚'
    if ds < 60:
        return u'%d秒前' % ds
    if ds < 3600:
        return u'%d分钟前' % (ds / 60,)
    d_change = now_date.day - d.day
    if ds < 3600 * 24 * 3:
        if d_change == 0:
            return u'今天%s' % d.strftime('%H:%M:%S')
        if d_change == 1:
            return u'昨天%s' % d.strftime('%H:%M:%S')
        if d_change == 2:
            return u'前天%s' % d.strftime('%H:%M:%S')
    y_change = now_date.year - d.year
    if y_change == 0:
        return u'%s' % d.strftime('%m-%d %H:%M:%S')
    if y_change == 1:
        return u'去年%s' % d.strftime('%m-%d %H:%M:%S')
    return u'%s年前%s' % (y_change, unicode(d.strftime('%m月%d日'), 'utf8'))


def send_email(emails, title, content, type='text'):
    from django.core.mail import send_mail, EmailMessage

    if not emails:
        return

    if not isinstance(emails, (list, tuple)):
        # if 'mrzhixuan' in emails:
        #     return
        emails = [emails, ]

    emails = [email for email in emails if not 'mrzhixuan' in email]
    if type != 'html':
        send_mail(title, content, settings.EMAIL_FROM, emails, fail_silently=True)
    else:
        msg = EmailMessage(title, content, settings.EMAIL_FROM, emails)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    return 0


def get_next_url(request):
    from urlparse import urlparse
    next_url = request.REQUEST.get('next_url')
    if not next_url:
        referrer = request.META.get('HTTP_REFERER')
        if referrer and referrer.startswith(settings.MAIN_DOMAIN):
            referrer = list(urlparse(referrer))[2]
            if referrer != request.path:
                if referrer not in ('/', '/regist', '/reset_password', '/forget_password'):
                    for key in ("regist", ):
                        if referrer.find(key) == -1:
                            # referrer的query参数会丢失
                            next_url = referrer + '?' + list(urlparse(referrer))[4]
    return next_url or '/home'


def filter_script(htmlstr):
    '''
    @note: html内容过滤 去掉script,link,外联style,标签上面的事件，标签上面样式含expression,javascript
    '''
    # 先过滤CDATA
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile('<\s*script[^>]*>.*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_link = re.compile('<\s*link[^>]*>', re.I)  # 外联link
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释

    # 过滤html元素节点里面的 expression,javascript,document,cookie,on
    # re_expression = re.compile('<[^>]*(expression|javascript|document|cookie|\s+on)+[^>]*>[^<]*<\s*/\s*[^>]*\s*>', re.I)

    # 去掉多余的空行
    blank_line = re.compile('(\r?\n)+')
    s = blank_line.sub(' ', htmlstr)

    s = re_cdata.sub('', s)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_link.sub('', s)  # 外联link
    s = re_comment.sub('', s)  # 去掉HTML注释
    # s = re_expression.sub('', s)  # 去掉样式中expression表达式

    re_expression = re.compile('<[^>]*( on)[^>]*>', re.I)
    s = re_expression.sub('', s)  # 去掉html带on事件的

    # 去掉多余的空行
    # s = blank_line.sub('\n', s)

    # 替换超链
    s = replace_href_to_open_blank(s)
    return s


def render_email_template(template_name='', context={}):
    '''
    @note: 渲染模板
    '''
    from django.template.loader import render_to_string

    if not template_name:
        return ''
    context.update(now=datetime.datetime.now())
    context.update(MAIN_DOMAIN=settings.MAIN_DOMAIN)

    return render_to_string(template_name, context)
    # t = template.loader.get_template(template_name)
    # c = template.Context(context)
    # return t.render(c)


# 判断user是否为user对象获取user id
get_uid = lambda user: user.id if hasattr(user, 'id') else str(user)


def select_at(s):
    """
    @note: 寻找at对象名称
    """
    #@提到的用户名称必须是：中文，英文字符，数字，下划线，减号这四类
    p = re.compile(u'@([\w\-\u4e00-\u9fa5]+)', re.I)
    return list(set(p.findall(s)))  # 去掉重复提到的人


def replace_at_html(content):
    """
    @note: 从内容中提取@信息
    """
    def _re_sub(match):
        """
        @note: callback for re.sub
        """
        nick = match.group(1)
        return '@<a href="/n/%(nick)s">%(nick)s</a>' % dict(nick=nick)

    tup_re = (u'@([\w\-\u4e00-\u9fa5]+)', _re_sub)
    p = re.compile(tup_re[0], re.DOTALL | re.IGNORECASE)
    content = p.sub(tup_re[1], content)
    return content


def replace_href_to_open_blank(content):
    """
    @note: 替换链接在新窗口中打开并且设置nofollow
    """
    def _re_sub(match):
        """
        @note: callback for re.sub
        """
        atag = match.group(0)
        href = match.group(1)
        if 'zhixuan.com' not in href:
            data = '%s%s%s' % (atag[:2], ' rel="nofollow"', atag[2:])
            if "_blank" not in data:
                data = '%s%s%s' % (atag[:2], ' target="_blank"', atag[2:])
            return data
        return atag

    p = re.compile(u'<a.+?(href=.+?)>.+?</a>', re.DOTALL | re.IGNORECASE)
    content = p.sub(_re_sub, content)
    return content


def get_summary_from_html(content, max_num=100):
    """
    @note: 通过内容获取摘要
    """
    summary = ''
    # 提取标签中的文字
    r = u'<.+?>([^\/\\\&\<\>]+?)</\w+?>'
    p = re.compile(r, re.DOTALL | re.IGNORECASE)
    rs = p.findall(content)
    for s in rs:
        if summary.__len__() > max_num:
            summary += '......'
            break
        if s:
            summary += s
    # 没有标签的
    if not summary:
        r = u'[\u4e00-\u9fa5\w\@]+'
        p = re.compile(r, re.DOTALL | re.IGNORECASE)
        rs = p.findall(content)
        for s in rs:
            if summary.__len__() > max_num:
                summary += '......'
                break
            if s:
                summary += s
    return summary


def get_summary_from_html_by_sub(content, max_num=100, filter_nbsp=False):
    """
    @note: 通过内容获取摘要，采用替换标签的方式实现
    """
    if content is None:
        return content
    tag_script = re.compile('<\s*script[^>]*>[\s\S]*?<\s*/\s*script\s*>', re.I)
    tag_style = re.compile('<\s*style[^>]*>[\s\S]*?<\s*/\s*style\s*>', re.I)
    content = tag_script.sub('', content)
    content = tag_style.sub('', content)

    if filter_nbsp:
        tag_nbsp = re.compile('\&\w+?;', re.I)
        content = tag_nbsp.sub('', content)

    tag_s = re.compile('<.+?>')
    tag_e = re.compile('</\w+?>')
    content = tag_s.sub('', content)
    content = tag_e.sub(' ', content)
    if content.__len__() > max_num:
        content = content[:max_num] + '......'
    return content


def get_random_code(length=16):
    # 去掉0, 1, l, o, O
    str_src = ('23456789'
               'abcdefghijkmnpqrstuvwxyz'
               'ABCDEFGHIJKLMNPQRSTUVWXYZ')
    postfix = ''
    for i in xrange(length):
        postfix += str_src[random.randint(0, len(str_src) - 1)]
    return postfix


def exec_command(command, timeout=25):
    import commands
    content = commands.getoutput(command)
    return True, content


class DictLikeObject(dict):

    '''
    @note: 格式化字典对象为object
    '''

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, name, value):
        self[name] = value


def format_object_to_dict(obj):
    '''
    @note: 将一个对象格式化为一个字典
    '''
    data = DictLikeObject()

    dict_obj = obj.__dict__
    keys = dict_obj.keys()
    for key in keys:
        if isinstance(dict_obj[key], (int, bool, long, float, unicode, str,
                                      list, tuple, set, dict, type(None))):
            data[key] = dict_obj[key]
        elif isinstance(dict_obj[key], (datetime.datetime, datetime.date)):
            data[key] = str(dict_obj[key])
        # else:
        #     print key
    return data


def get_sub_domain_from_http_host(http_host):
    '''
    @note: 从http host中获取子域名前缀
    '''
    import urlparse
    if http_host:
        http_host = ('http://%s' % http_host) if not http_host.startswith('http') else http_host
        prefix = urlparse.urlparse(http_host)[1].split('.', 1)[0]
        return prefix


def get_chinese_length(text):
    """
    @note: 获取长度，中文算1个，字母算半个
    """
    str_count = 0
    for c in text:
        if ord(c) > 127:
            str_count += 2
        else:
            str_count += 1
    return str_count / 2


def get_baidu_rank(key):
    """
    @note: 获取关键词在百度中的排名 
    """
    from pyquery import PyQuery as pq

    for page in range(0, 1):
        url = u"http://www.baidu.com/s?wd=" + key + "&pn=" + \
            str(page) + u"&oq=" + key + "&ie=utf-8&usm=2&rn=100"
        rep = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"})
        text = rep.text

        text = pq(text)
        for i, div in enumerate(text(".c-container")):
            if "zhixuan" in pq(div).html():
                return i + 1
    return "101"


def get_city_by_ip_from_taobao(ip):
    url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s" % ip
    data = dict(city="", country="")
    for i in range(2):
        try:
            resp = requests.get(url, timeout=3)
            city_info = json.loads(resp.text)
            assert city_info["code"] == 0
            data = dict(city=city_info["data"]["city"], country=city_info["data"]["country"])
        except Exception:
            pass
        break
    return data


def get_family_name(name):
    """
    @note: 获取姓氏
    """
    name = name.strip()
    ks = [u"欧阳", u"太史", u"端木", u"上官", u"司马", u"东方", u"独孤", u"南宫", u"夏侯", u"诸葛", u"尉迟", u"皇甫", u"公孙",
          u"慕容", u"钟离", u"长孙", u"宇文", u"司徒", u"百里", u"呼延", u"轩辕", u"东郭", u"司空", u"闾丘", u"令狐"]

    for key in ks:
        if key in name:
            return key
    return name[0]
