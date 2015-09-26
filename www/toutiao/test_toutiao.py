#coding: utf-8
import requests, re, json, time, datetime, traceback, random
from pyquery import PyQuery as pq

host = "www.zhixuan.com"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}
img_prefix = "http://img01.store.sogou.com/net/a/04/link?appid=100520031&w=210&h=105&url="

def get_mps():
    
    url = "http://%s/toutiao/get_mps" % host
    req = requests.get(url)
    return json.loads(req.text)

def sync():
    mps = get_mps()

    mp = mps[0]

    resp = requests.get(
        u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name'],
        headers = headers,
        # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
        timeout = 15
    )

    cookies = resp.cookies
    temp = pq(resp.text)
    href = temp('.wx-rb_v1').eq(0).attr('href')
    ext = re.compile('ext=(.*)').search(href).groups()[0]

    print u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name']
    print href
    print ext
    print '1-1--1-1-1-1-1-1-1-1-1-1-1-1-1-1-1--1-1-1-1-1'

    url = u"http://weixin.sogou.com/gzh?openid=%s&ext=%s" % (mp['open_id'], ext)
    resp = requests.get(
        url,
        headers = headers,
        # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
        timeout = 15,
        cookies = cookies
    )
    cookies = resp.cookies

    url = u"http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=%s&ext=%s&gzhArtKeyWord=&%s&page=1" % (mp['open_id'], ext, mp['ext_id'])
    resp = requests.get(
        url,
        headers = headers,
        # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
        timeout = 15,
        cookies = cookies
    )
    print url
    print '2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2'
    lst_article = eval(re.compile('gzhcb\((.+)\)').findall(resp.text)[0])["items"]
    # cookies = resp.cookies

    article = lst_article[0]
    article = article.replace("\\", "")
    url = re.compile('<url>(.+)</url>').findall(article)[0][9:-3]
    url = u"http://weixin.sogou.com" + url
    print url
    resp = requests.get(
        url,
        headers = headers,
        timeout = 15,
        cookies = cookies,
        # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
    )

    print resp.text
    print '3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3'

def sync2():
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"

    mps = get_mps()

    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        UA
    )

    driver = webdriver.PhantomJS(desired_capabilities=dcap, executable_path='/Users/stranger/workspace/phantomjs/bin/phantomjs')
    driver.set_window_size(1120, 550)

    for mp in mps:
        try:
            time.sleep(6)
            # 1.访问微信
            url = u"http://weixin.sogou.com/weixin?type=1&query=a"
            driver.get(url)
            print url
            
            time.sleep(6)
            search_input = driver.find_elements_by_id('upquery')[0]
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.2)
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.2)
            for x in range(len(mp['name'])):
                search_input.send_keys(mp['name'][x])
                time.sleep(0.2)
            
            print search_input.get_attribute('value')

            # 2.搜索公众号 得到ext
            driver.find_elements_by_id('searchBtn')[0].click()
            time.sleep(6)
            print driver.title 
            href = driver.find_elements_by_class_name('wx-rb_v1')[0].get_attribute('href')
            ext = re.compile('ext=(.*)').search(href).groups()[0]
            print ext

            url = u"http://weixin.sogou.com/gzh?openid=%s&ext=%s" % (mp['open_id'], ext)
            print url

            # 3.搜索具体公众号
            driver.get(url)
            time.sleep(6)

            articles = driver.find_elements_by_class_name('news_lst_tab')
            dates = driver.find_elements_by_class_name('s-p')
            temps = []
            for i in range(len(articles)):
                href = articles[i].get_attribute('href')
                create_time = dates[i].get_attribute('t')

                temps.append([href, datetime.datetime.fromtimestamp(float(create_time))])

            for temp in temps:
                href = temp[0]
                create_time = temp[1]
                print href, create_time

                # 4.跳转到微信
                driver.get(href)
                time.sleep(6)
                title = driver.find_elements_by_id('activity-name')[0].text
                content = driver.find_elements_by_id('js_content')[0].get_attribute('innerHTML')
                url = driver.current_url
                try:
                    img = img_prefix + driver.find_elements_by_id('js_cover')[0].get_attribute('src')
                except Exception, e:
                    print traceback.print_exc()
                    continue

                print title
                print url
                print img

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
                else:
                    print u'失败！！[%s]' % result['code']

                    if result['code'] == 2:
                        print u'此公众号暂无更新，跳过...'
                        time.sleep(65)
                        break

        except Exception, e:
            print traceback.print_exc()
            continue


    driver.quit()

if  __name__=='__main__':
    sync2()


