# -*- coding: utf-8 -*-

import requests, re, json, time, datetime, traceback, random, base64
from pyquery import PyQuery as pq

# host = "www.a.com:8000"
host = "www.zhixuan.com"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

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
        ext = re.compile('ext=(.*)').search(href).groups()[0]
        # print u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name']
        # print href
        # print ext
        # print '1-1--1-1-1-1-1-1-1-1-1-1-1-1-1-1-1--1-1-1-1-1'

        # temp = requests.get(
        #     u'http://weixin.sogou.com' % href,
        #     headers = headers,
        #     proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
        #     timeout = 15
        # ).text
        # weixin_gzh_openid_ext = re.compile("weixin_gzh_openid_ext = \"(.*)\";w").search(temp).groups()[0]
        # print u'http://weixin.sogou.com' % href
        # print weixin_gzh_openid_ext
        # print '2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-'

        # url = u"http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid="+ mp['open_id'] +"&" + mp['ext_id'] + "&page=1"
        url = u"http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=%s&ext=%s&gzhArtKeyWord=&%s&page=1" % (mp['open_id'], ext, mp['ext_id'])
        resp = requests.get(
            url,
            headers = headers,
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
            timeout = 15,
            cookies = cookies
        )
        # print url
        # print resp.text
        # lst_article = eval(re.compile('gzh\((.+)\)').findall(resp.text)[0])["items"]
        lst_article = eval(re.compile('gzhcb\((.+)\)').findall(resp.text)[0])["items"]
        # cookies = resp.cookies
    except Exception, e:
        # traceback.print_exc()
        pass

    return lst_article, cookies


def sync_by_proxy():
    img_prefix = "http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl="
    img_prefix = "http://img01.store.sogou.com/net/a/04/link?appid=100520031&w=210&h=105&url="
    # proxies = get_active_sougou_proxy()
    
    mps = get_mps()
    count = 0
    success = 0
    index = 0

    for mp in mps:
        proxies = get_active_sougou_proxy()
        count += 1
        # url = u"http://weixin.sogou.com/gzhjs?openid=%s" % mp['open_id']
        # url = u"http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid="+ mp['open_id'] +"&" + mp['ext_id'] + "&page=1"
        # print url
        lst_article = []
        cookies = None
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
            article = article.replace("\\", "")
            temp.append({
                "url": re.compile('<url>(.+)</url>').findall(article)[0][9:-3],
                "timestamp": float(re.compile('<lastModified>(.+)</lastModified>').findall(article)[0]),
                "img": img_prefix + re.compile('<imglink>(.+)</imglink>').findall(article)[0][9:-3],
            })
        temp = sorted(temp, key=lambda x: x['timestamp'], reverse=True)
        # print temp

        for t in temp:

            time.sleep(4)

            try:
                url = u"http://weixin.sogou.com" + t['url']

                print url
                timestamp = t['timestamp']
                img = t['img']
                create_time = datetime.datetime.fromtimestamp(float(timestamp))

                resp = requests.get(
                    url,
                    headers = headers,
                    timeout = 15,
                    cookies = cookies,
                    proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
                )

                print resp.text
                
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


