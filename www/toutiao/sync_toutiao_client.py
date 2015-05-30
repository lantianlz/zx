# -*- coding: utf-8 -*-

import requests, re, json, time, datetime, traceback, random
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

def get_SUV():
    return str(int(round(time.time() * 1000 * 1000) + round(random.random() * 1000)))

def get_cookies():
    cookies = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

    for x in range(50):

        url = "http://weixin.sogou.com/weixin?query=%s" % random.choice('abcdefghijklmnopqrstuvwxyz')
    
        res = requests.get(url, headers=headers)
        temp = res.cookies.get_dict()
        temp['SUV'] = get_SUV()
        print temp
        cookies.append(temp)

        time.sleep(6)

    return cookies

def is_active_sougou_proxy(proxy):

    url = "http://weixin.sogou.com/gzhjs?openid=oIWsFtzU9XFaZY7vsx3qkvrDQ86A"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}
    flag = False

    try:
        req = requests.get(
            url, 
            headers = headers, 
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}, 
            timeout = 7
        )
        flag = req.text.find('oIWsFtzU9XFaZY7vsx3qkvrDQ86A') > -1
    except Exception, e:
        flag = False

    return flag


def get_active_sougou_proxy():

    PROXY_URL = "http://proxy-list.org/english/search.php?search=CN.transparent&country=CN&type=transparent&port=any&ssl=any"
    PROXY_URL = "http://proxy-list.org/chinese/index.php?p=1&setlang=chinese"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

    req = requests.get(PROXY_URL, headers=headers, timeout=10)
    
    dom = pq(req.text)

    proxy = ''
    proxies = []
    for x in dom('.table').eq(0).find('li.proxy'):
        proxy = x.text.strip()
        proxies.append(proxy)
        # if is_active_sougou_proxy(proxy):
        #     break
        # else:
        #     print u'无效代理==>[ %s ]' % proxy
        #     pass
    print u'代理===>%s' % proxies
    return proxies



def sync():

    mps = get_mps()
    # cookies_list = get_cookies()
    print u'cookie更新完毕'
    count = 0
    success = 0

    # cookies = requests.get(
    #         "http://weixin.sogou.com",
    #         headers = headers,
    #         timeout = 10
    #     ).cookies
    # print cookies
    # time.sleep(5)

    # cookies_str = "ABTEST=6|1430562799|v1; IPLOC=CN5101; SUID=52BAB86E2708930A000000005544A7F4; PHPSESSID=nal4dakj4dfppst9bp6819d2e5; SUIR=1430562806; SUID=52BAB86E5EC90D0A000000005544A7F6; SNUID=D0383AEC828697945E51B3838324047A; SUV=000E779A6EB8BA525544A806CE60F405; LSTMV=380%2C162; LCLKINT=4707"
    # cookies = {}
    # for i in cookies_str.split(';'):
    #     temp = i.split('=', 1)
    #     cookies[temp[0].strip()] = temp[1]

    for mp in mps:
        count += 1
        url = u"http://weixin.sogou.com/gzhjs?openid=%s" % mp['open_id']

        try:
            resp = requests.get(
                url,
                # headers = {
                #     'Referer': 'http://weixin.sogou.com',
                #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                #     'Accept-Encoding': 'gzip, deflate, sdch',
                #     'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,fr;q=0.2,es;q=0.2',
                #     'Connection': 'keep-alive',
                #     'Host': 'weixin.sogou.com',
                #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
                # },
                # cookies = dict(
                #     CXID='4CF138C2A1A03DFDB7E1254F57E109B5',
                #     SUID='60D697B6152D900A553DE47C0001824D',
                #     SUV='00ED7B2A6EB8B045553F8479CB5D6119',
                #     ABTEST='7|1430234943|v1',
                #     pgv_pvi='8401204205',
                #     pgv_info='ssi=s191820936',
                #     weixinIndexVisited='1',
                #     ad='PZllllllll2q5WSDlllllVqxmsDlllllHIKQYlllllGlllll4klll5@@@@@@@@@@',
                #     IPLOC='CN5101',
                #     SNUID='3DD4D6006E6A7B7A56D03DE56F2C840B',
                #     sct='9',
                #     wapsogou_qq_nickname='',
                #     LSTMV='767%2C444',
                #     LCLKINT='542767'
                # ),
                headers = headers,
                cookies = random.choice(cookies_list),
                timeout = 15,
                # allow_redirects = True,
                # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
            )

            lst_article = eval(re.compile('gzh\((.+)\)').findall(resp.text)[0])["items"]

            for article in lst_article:

                time.sleep(5)

                try:
                    article = article.replace("\\", "")
                    url = re.compile('<url>(.+)</url>').findall(article)[0][9:-3]
                    timestamp = re.compile('<lastModified>(.+)</lastModified>').findall(article)[0]
                    img = re.compile('<imglink>(.+)</imglink>').findall(article)[0][9:-3]
                    create_time = datetime.datetime.fromtimestamp(float(timestamp))

                    article_detail = pq(requests.get(
                        url,
                        headers = headers,
                        timeout = 15,
                        # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
                    ).text)
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
                        print u'成功!'
                        success += 1
                    else:
                        print u'失败！！[%s]' % result['code']
                except Exception, e:
                    print e
                    continue

        except Exception, e:
            print traceback.print_exc()
            continue

    print u'成功更新[ %s ]条' % success


def _get_weixin_list(proxy, url):
    lst_article = []

    try:
        resp = requests.get(
            url,
            headers = headers,
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
            timeout = 15
        )

        # lst_article = eval(re.compile('gzh\((.+)\)').findall(resp.text)[0])["items"]
        lst_article = eval(re.compile('gzhcb\((.+)\)').findall(resp.text)[0])["items"]
        
    except Exception, e:
        # traceback.print_exc()
        pass

    return lst_article


def sync_by_proxy():
    img_prefix = "http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl="
    proxies = get_active_sougou_proxy()
    
    mps = get_mps()
    count = 0
    success = 0
    index = 0

    for mp in mps:
        count += 1
        # url = u"http://weixin.sogou.com/gzhjs?openid=%s" % mp['open_id']
        url = u"http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid="+ mp['open_id'] +"&" + mp['ext_id'] + "&page=1"
        lst_article = []

        for i in range(len(proxies)):
            # 有效代理索引判断
            if index > i:
                continue

            proxy = proxies[i]
            lst_article = _get_weixin_list(proxy, url)
            
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

        for article in lst_article:

            time.sleep(4)

            try:
                article = article.replace("\\", "")
                url = re.compile('<url>(.+)</url>').findall(article)[0][9:-3]
                timestamp = re.compile('<lastModified>(.+)</lastModified>').findall(article)[0]
                img = img_prefix + re.compile('<imglink>(.+)</imglink>').findall(article)[0][9:-3]
                create_time = datetime.datetime.fromtimestamp(float(timestamp))

                article_detail = pq(requests.get(
                    url,
                    headers = headers,
                    timeout = 15,
                    # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
                ).text)
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
                        time.sleep(15)
                        break
            except Exception, e:
                print e
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
            time.sleep(900) 
        except Exception, e:
            print e



