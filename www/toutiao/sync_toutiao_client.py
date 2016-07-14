# -*- coding: utf-8 -*-

import requests, re, json, time, datetime, traceback, random, base64, HTMLParser
from pyquery import PyQuery as pq

# host = "www.a.com:8000"
host = "www.zhixuan.com"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}
html_parser = HTMLParser.HTMLParser()
use_proxy = True

def get_mps():
    
    url = "http://%s/toutiao/get_mps" % host
    req = requests.get(url)
    return json.loads(req.text)

def _replace_html_tag(text):
    tag_s = re.compile('<.+?>')
    tag_e = re.compile('</\w+?>')
    text = tag_s.sub('', text)
    text = tag_e.sub(' ', text)
    return text

def get_active_sougou_proxy():

    if not use_proxy:
        return ['127.0.0.1:80']

    PROXY_URL = "http://proxy-list.org/english/search.php?search=CN.transparent&country=CN&type=transparent&port=any&ssl=any"
    PROXY_URL = "http://proxy-list.org/chinese/index.php?p=1&setlang=chinese"
    PROXY_URL = "http://proxy-list.org/english/index.php"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

    req = requests.get(PROXY_URL, headers=headers, timeout=10)
    
    dom = pq(req.text)

    proxy = ''
    proxies = []
    for x in dom('.table').eq(0).find('li.proxy script'):
        proxy = x.text.replace("Proxy('", "").replace("')", "")
        proxy = base64.b64decode(proxy)
        proxies.append(proxy)
        
    print u'代理===>%s' % proxies
    return proxies

def _get_weixin_list(proxy, mp):
    lst_article = []
    cookies = None
    timestamp = time.time()

    try:
        resp = requests.get(
            u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name'],
            headers = headers,
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
            timeout = 15
        )

        cookies = resp.cookies
        temp = pq(resp.text)
        href = temp('.wx-rb_v1').eq(0).attr('href')
        print u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name']
        print href
        print '1-1--1-1-1-1-1-1-1-1-1-1-1-1-1-1-1--1-1-1-1-1'

        temp = requests.get(
            href,
            headers = {
                'Referer': u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name'],
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
            },
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
            timeout = 15,
        )
        cookies = temp.cookies

        json_str = re.compile("var msgList = '(.*)';").search(temp.text).groups()[0]
        # print html_parser.unescape(json_str)
        lst_article = eval(html_parser.unescape(json_str))
        
        lst_article = lst_article['list']
        
        # print '22-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2'
        # print len(lst_article)
        # time.sleep(15)

    except Exception, e:
        traceback.print_exc()
        pass

    return lst_article, cookies


def sync_by_proxy():
    img_prefix = "http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl="
    img_prefix = "http://img01.store.sogou.com/net/a/04/link?appid=100520031&w=210&h=105&url="
    img_prefix = "http://%s/toutiao/get_img?url=" % host
    # proxies = get_active_sougou_proxy()
    
    mps = get_mps()
    count = 0
    success = 0
    index = 0

    for mp in mps:

        proxies = get_active_sougou_proxy()

        count += 1
        
        lst_article = []
        cookies = None
        timestamp = time.time()
        proxy = ""
        temp = []

        for i in range(len(proxies)):
            # 有效代理索引判断
            if index > i:
                continue

            proxy = proxies[i]
            lst_article, cookies = _get_weixin_list(proxy, mp)
            
            if lst_article:
                print u'代理[ %s ]获取微信文章链接成功!!!' % proxy
                index = i
                break
            else:
                print u'代理[ %s ]获取微信文章链接失败' % proxy
                pass

        # print lst_article
        # 如果代理全部失效 重新获取一次
        if lst_article == []:
            index = 0
            proxies = get_active_sougou_proxy()

        # 排序
        for article in lst_article:
            
            temp.append({
                "url": html_parser.unescape(article['app_msg_ext_info']['content_url'].replace("\\", "")),
                "timestamp": article['comm_msg_info']['datetime'],
                "img": img_prefix + article['app_msg_ext_info']['cover'].replace("\\", ""),
            })

            # 是否有多条
            if article['app_msg_ext_info']['is_multi'] == 1:
                for art in article['app_msg_ext_info']['multi_app_msg_item_list']:
                    temp.append({
                        "url": html_parser.unescape(art['content_url'].replace("\\", "")),
                        "timestamp": article['comm_msg_info']['datetime'],
                        "img": img_prefix + art['cover'].replace("\\", ""),
                    })

        # print temp
        # print '3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3'
        # time.sleep(15)

        for t in temp:

            time.sleep(4)

            try:
                url = u"http://mp.weixin.qq.com" + t['url']

                # print url
                
                img = t['img']
                timestamp = t['timestamp']
                create_time = datetime.datetime.fromtimestamp(float(timestamp))

                resp = requests.get(
                    url,
                    headers = headers,
                    timeout = 15,
                    cookies = cookies,
                    proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
                )

                # print resp.text
                
                article_detail = pq(resp.text)
                #print url
                title = article_detail("#activity-name").html().split("<em")[0].strip()
                content = article_detail("#js_content").html()
                format_content = _replace_html_tag(content).strip()
                if len(format_content) < 300:
                    continue

                print '[ %s ]%s' % (count, url)
                # print img
                # printlst_article title.encode("utf8")
                # print content.encode("utf8")
                # print create_time

                # 提交到服务器
                response = requests.post(
                    "http://%s/toutiao/sync_toutiao" % host,
                    data = {
                        'mp_id': mp['mp_id'],
                        'title': title,
                        'content': content,
                        'url': url,
                        'img': img,
                        'create_time': str(create_time)
                    }
                )

                result = json.loads(response.text)
                if result['code'] == 0:
                    success += 1
                    print u'成功!'
                else:
                    print u'失败！！[%s]' % result['code']

                    if result['code'] == 2:
                        print u'此公众号暂无更新，跳过...'
                        time.sleep(10)
                        break
            except Exception, e:
                print traceback.print_exc()
                continue

    print '成功更新[ %s ]条' % success

if __name__ == "__main__":
    # c = get_cookies()
    # print c
    # print '================'
    # print random.choice(c)

    while 1:
        try:
            sync_by_proxy()
            time.sleep(10) 
        except Exception, e:
            traceback.print_exc()


