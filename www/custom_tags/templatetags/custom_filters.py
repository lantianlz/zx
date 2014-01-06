# -*- coding: utf-8 -*-
"""
@attention: 自定义过滤器文件
@author: lizheng
"""

import re
from django import template
from django.shortcuts import render_to_response
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.paginator import Page


register = template.Library()


"""
@attention: 以下是几个demo
"""


# escape类型输出demo
@register.filter
def initial_letter_filter(text, autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = '<strong>%s</strong>' % (esc(text))
    return mark_safe(result)
initial_letter_filter.needs_autoescape = False


# def str_display(str_in, maxlength):
#     """
#     @attention: 截断输入字符串,超过最大长度加...
#     """
#     maxlength = int(maxlength)
#     return (str_in[:maxlength] + u'...') if str_in.__len__() > maxlength else str_in
@register.filter
def str_display(str_in, str_parms):
    """
    @attention: 截断输入字符串,超过最大长度加... 中文算2个字符
    @note: maxlength最长字符数
    """
    from django.utils.encoding import smart_unicode
    str_in = smart_unicode(str_in)
    parms = str(str_parms).split(':')
    if len(parms) > 1:
        suffix = parms[1]
    else:
        suffix = u'...'
    maxlength = int(parms[0]) * 2
    str_out = []
    str_count = 0
    for c in str_in:
        if ord(c) > 127:
            str_count += 2
        else:
            str_count += 1
        if str_count > maxlength:
            break
        str_out.append(c)
    if maxlength < str_count:
        str_out.append(suffix)
    return u''.join(str_out)


def get_page_url(url, page=1):
    """
    @attention: 获取分页对应的url
    """
    if url.find('?') == -1:
        return u'%s?page=%s' % (url, page)
    if url.find('page=') == -1:
        return u'%s&page=%s' % (url, page)
    re_pn = re.compile('page=\d+', re.IGNORECASE)
    url = re_pn.sub('page=%s' % page, url)
    return url


@register.filter('paging')
def paging(value, request, get_page_onclick=None, page_onclick_params={}):
    """
    @attention: 根据总页数和页码分页
    """
#    try:
    if not value:
        return u'paging params can not be null'

    if isinstance(value, Page):
        page = value.number
        total_page = value.paginator.num_pages
    else:
        page = int(value[0] if value[0] else 1)
        page = 1 if page < 1 else page
        total_page = int(value[1])
    if total_page == 1:
        return ''

    if page > total_page:
        return u'paging params wrong'

    url = request.get_full_path()

    page_limit = 9
    page_half_limit = 4

    # 总页数小于一页总数
    if total_page <= page_limit:
        page_items = range(1, total_page + 1)
    else:
        start = page - page_half_limit if page - page_half_limit >= 1 else 1
        end = page + page_half_limit if page + page_half_limit <= total_page else total_page
        page_items = range(start, end + 1)

    # 加上头
    if page_items[0] != 1:
        page_items.insert(0, 1)
        if page_items[1] > 2:
            page_items.insert(1, '...')
    # 加上尾
    if page_items[-1] != total_page:
        if page_items[-1] < total_page - 1:
            page_items.append('...')
        page_items.append(total_page)

    pre_url = get_page_url(url, page - 1)
    next_url = get_page_url(url, page + 1)
    page_items_with_url = [(p, get_page_url(url, p) if p != '...' else '') for p in page_items]
    return mark_safe(render_to_response('include/_paging.html', locals()).content)

    # s, s_pre, s_next = '', '', ''
    # if page > 1:
    #     if not get_page_onclick:
    #         s_pre = u'<li title="上一页"><a href="%s">&laquo;</a></li>' % (get_page_url(url, page - 1))
    #     else:
    #         s_pre = u'<li title="上一页"><a href="javascript:void(0);" onclick="%s">&laquo;</a></li>' % (get_page_onclick(page - 1, **page_onclick_params))
    # if page < total_page:
    #     if not get_page_onclick:
    #         s_next = u'<li title="下一页"><a href="%s">&raquo;</a></li>' % (get_page_url(url, page + 1))
    #     else:
    #         s_next = u'<li title="下一页"><a href="javascript:void(0);" onclick="%s">&raquo;</a></li>' % (get_page_onclick(page + 1, **page_onclick_params))

    # for p in page_items:
    #     if p == page:
    #         s += u'<li class="active"><a>%s</a></li>' % (p)
    #     elif p == '...':
    #         s += u'<li class="disabled"><a href="%s">%s</a></li>' % ('javascript:void(0);', p)
    #     else:
    #         if not get_page_onclick:
    #             s += u'<li><a href="%s">%s</a></li>' % (get_page_url(url, p), p)
    #         else:
    #             s += u'<li><a href="javascript:void(0);" onclick="%s">%s</a></li>' % (get_page_onclick(p, **page_onclick_params), p)
    # return mark_safe('<div class="pagination pagination-right"><ul>%s%s%s</ul></div>' % (s_pre, s, s_next))


@register.filter
def number_format(value):
    chinese_number = [u"零", u"一", u"二", u"三", u"四", u"五", u"六", u"七"]
    return chinese_number[value]


@register.filter
def change_http_data(content):
    """
    @attention: 转换http://www.的文字为超链接
    @param content: 要转换的内容
    @return: 转换后的数据
    @author: lizheng
    @date:  2011-02-22
    """
    # 替换带有左右空格等空白字符的http数据链接
    r = '\s+(https?\:\/\/[\w\/\.\?\&\=\~\-\_]+)(\s+|$)'

    p = re.compile(r, re.DOTALL | re.IGNORECASE)
    if p.findall(content or ""):
        content = p.sub(u' <a href="%s" target="_blank">%s</a> ' % (r'\1', r'\1'), content)

    return content


# 格式化时间输出
from common.utils import time_format
register.filter('time_format', time_format)
