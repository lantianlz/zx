#coding: utf-8
import requests, re, json, time, datetime, traceback, random, socket
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class WeixinSpider(object):

    def __init__(self):
        
        self.SLEEP_TIME = 0
        self.HOST = "www.zhixuan.com"
        self.UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
        self.HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}
        self.IMG_PREFIX = "http://img01.store.sogou.com/net/a/04/link?appid=100520031&w=210&h=105&url="

        self.mps = self.get_mps()
        self.proxies = self.get_proxies()


    def get_mps(self):
        '''
        获取微信公众号数据
        '''
        url = "http://%s/toutiao/get_mps" % self.HOST
        req = requests.get(url)
        return json.loads(req.text)

    def get_proxies(self):
        '''
        获取代理
        '''
        PROXY_URL = "http://proxy-list.org/english/search.php?search=CN.transparent&country=CN&type=transparent&port=any&ssl=any"
        PROXY_URL = "http://proxy-list.org/chinese/index.php?p=1&setlang=chinese"

        req = requests.get(PROXY_URL, headers=self.HEADERS, timeout=10)
        
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

    def get_driver(self, my_proxy=None):
        '''
        获取driver
        '''
        socket.setdefaulttimeout(20)

        if my_proxy:
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': my_proxy,
                'ftpProxy': my_proxy,
                'sslProxy': my_proxy,
                'noProxy': '' 
            })

            print u'使用代理====>' + my_proxy
            driver = webdriver.Firefox(proxy = proxy)

        else:

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (self.UA)

            driver = webdriver.PhantomJS(
                desired_capabilities = dcap, 
                executable_path = '/Users/stranger/workspace/phantomjs/bin/phantomjs'
            )

        return driver
        

    def get_ext(self, mp_name):
        '''
        获取ext
        '''
        driver = self.driver
        driver.set_window_size(1120, 550)
        # driver.set_page_load_timeout(25)

        ext = ''
        try:
            # 访问微信查询链接
            url = u"http://weixin.sogou.com/weixin?type=1&query=a"
            driver.get(url)
            time.sleep(self.SLEEP_TIME)

            # 文本框输入公众号名字
            search_input = driver.find_elements_by_id('upquery')[0]
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
            for x in range(len(mp_name)):
                search_input.send_keys(mp_name[x])
                time.sleep(0.1)
            print search_input.get_attribute('value')

            # 搜索公众号 得到ext
            driver.find_elements_by_id('searchBtn')[0].click()
            time.sleep(self.SLEEP_TIME)
            # WebDriverWait(driver, 11).until(EC.presence_of_element_located((By.ID, "searchBtn")))
            # lambda the_driver: the_driver.find_element_by_id('dropdown1').is_displayed()

            print driver.title 
            href = driver.find_elements_by_class_name('wx-rb_v1')[0].get_attribute('href')
            ext = re.compile('ext=(.*)').search(href).groups()[0]
            print ext
        except Exception, e:
            print traceback.print_exc()

        return ext

    def get_article_list(self, mp_openid, ext):
        '''
        获取公众号列表
        '''
        driver = self.driver

        url = u"http://weixin.sogou.com/gzh?openid=%s&ext=%s" % (mp_openid, ext)
        print url

        driver.get(url)
        time.sleep(self.SLEEP_TIME)

        articles = driver.find_elements_by_class_name('news_lst_tab')
        dates = driver.find_elements_by_class_name('s-p')
        imgs = driver.find_elements_by_class_name('img_box2')
        data  = []
        for i in range(len(articles)):
            href = articles[i].get_attribute('href')
            create_time = dates[i].get_attribute('t')
            img = imgs[i].find_element_by_tag_name('img').get_attribute('src')
            temp = img.split('&url=')
            temp.insert(1, '&w=210&h=105&url=')
            img = "".join(temp)

            data.append([href, datetime.datetime.fromtimestamp(float(create_time)), img])

        return data

    def get_article_detail(self, data):
        '''
        获取文章详细信息
        '''
        driver = self.driver

        href = data[0]
        create_time = data[1]
        print href

        # 跳转到微信
        driver.get(href)
        time.sleep(self.SLEEP_TIME)
        title = driver.find_elements_by_id('activity-name')[0].text
        content = driver.find_elements_by_id('js_content')[0].get_attribute('innerHTML')
        url = driver.current_url
        img = data[2]
        # try:
        #     img = img_prefix + driver.find_elements_by_id('js_cover')[0].get_attribute('src')
        # except Exception, e:
        #     print traceback.print_exc()
        #     continue

        print title
        print url
        print img
        print create_time

        return title, content, url, img, create_time

    def sync_article(self, mp_id, title, content, url, img, create_time):
        '''
        同步文章到服务器
        '''
        response = requests.post(
            "http://%s/toutiao/sync_toutiao" % self.HOST,
            data = {
                'mp_id': mp_id,
                'title': title,
                'content': content,
                'url': url,
                'img': img,
                'create_time': str(create_time)
            }
        )

        return json.loads(response.text)
        


    def spider(self):
        index = 0
        for mp in self.mps:
            try:
                ext = ''

                for i in range(len(self.proxies)):
                    # 有效代理索引判断
                    if index > i:
                        continue

                    proxy = self.proxies[i]
                    self.driver = self.get_driver(proxy)
                    ext = self.get_ext(mp['name'])

                    if ext == '':
                        print u'代理无效'
                        self.driver.quit()
                    else:
                        print u'代理[ %s ]可用' % proxy
                        index = i
                        break

                # 如果代理全部失效 重新获取一次
                if ext == '':
                    self.proxies = self.get_proxies()
                    print u'如果代理全部失效 重新获取一次======'
                    continue

                article_data_list = self.get_article_list(mp['open_id'], ext)

                for article_data in article_data_list:
                    title, content, url, img, create_time = self.get_article_detail(article_data)
                    result = self.sync_article(mp['mp_id'], title, content, url, img, create_time)

                    if result['code'] == 0:
                        print u'成功!'
                    else:
                        print u'失败！！[%s]' % result['code']

                        if result['code'] == 2:
                            print u'此公众号暂无更新，跳过...'
                            time.sleep(80)
                            break

                    

            except Exception, e:
                print traceback.print_exc()
                continue

            self.driver.quit()
            # self.proxies = self.get_proxies()


    def sync(self):
        mps = self.mps

        for mp in mps:
            
            
            for proxy in self.proxies:

                try:
                    resp = requests.get(
                        u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name'],
                        headers = self.HEADERS,
                        proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
                        timeout = 15
                    )
                    print '-------'
                    cookies = resp.cookies
                    temp = pq(resp.text)
                    href = temp('.wx-rb_v1').eq(0).attr('href')
                    ext = re.compile('ext=(.*)').search(href).groups()[0]

                    print u'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8' % mp['name']
                    print href
                    print ext
                    print '1-1--1-1-1-1-1-1-1-1-1-1-1-1-1-1-1--1-1-1-1-1'

                    # url = u"http://weixin.sogou.com/gzh?openid=%s&ext=%s" % (mp['open_id'], ext)
                    # resp = requests.get(
                    #     url,
                    #     headers = self.HEADERS,
                    #     # proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
                    #     timeout = 15,
                    #     cookies = cookies
                    # )
                    # cookies = resp.cookies

                    url = u"http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&openid=%s&ext=%s&gzhArtKeyWord=&%s&page=1" % (mp['open_id'], ext, mp['ext_id'])
                    resp = requests.get(
                        url,
                        headers = self.HEADERS,
                        proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy},
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
                        headers = self.HEADERS,
                        timeout = 15,
                        cookies = cookies,
                        proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
                    )

                    print resp.text
                    print '3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3'

                    article_detail = pq(resp.text)
                    #print url
                    title = article_detail("#activity-name").html().split("<em")[0].strip()
                    content = article_detail("#js_content").html()
                    format_content = _replace_html_tag(content).strip()
                    if len(format_content) < 300:
                        continue

                except Exception, e:
                    print traceback.print_exc()
                    continue 

# def sync2():
#     UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"

#     mps = get_mps()
#     proxies = get_proxies()

#     dcap = dict(DesiredCapabilities.PHANTOMJS)
#     dcap["phantomjs.page.settings.userAgent"] = (
#         UA
#     )

#     for mp in mps:
#         try:

#             driver = webdriver.PhantomJS(desired_capabilities=dcap, executable_path='/Users/stranger/workspace/phantomjs/bin/phantomjs')
#             driver.set_window_size(1120, 550)

#             time.sleep(6)
#             # 1.访问微信
#             url = u"http://weixin.sogou.com/weixin?type=1&query=a"
#             driver.get(url)
#             print url
            
#             time.sleep(6)
#             print driver.page_source
#             search_input = driver.find_elements_by_id('upquery')[0]
#             search_input.send_keys(Keys.BACKSPACE)
#             time.sleep(0.2)
#             search_input.send_keys(Keys.BACKSPACE)
#             time.sleep(0.2)
#             for x in range(len(mp['name'])):
#                 search_input.send_keys(mp['name'][x])
#                 time.sleep(0.2)
            
#             print search_input.get_attribute('value')

#             # 2.搜索公众号 得到ext
#             driver.find_elements_by_id('searchBtn')[0].click()
#             time.sleep(6)
#             print driver.title 
#             href = driver.find_elements_by_class_name('wx-rb_v1')[0].get_attribute('href')
#             ext = re.compile('ext=(.*)').search(href).groups()[0]
#             print ext

#             url = u"http://weixin.sogou.com/gzh?openid=%s&ext=%s" % (mp['open_id'], ext)
#             print url

#             # 3.搜索具体公众号
#             driver.get(url)
#             time.sleep(6)

#             articles = driver.find_elements_by_class_name('news_lst_tab')
#             dates = driver.find_elements_by_class_name('s-p')
#             imgs = driver.find_elements_by_class_name('img_box2')
#             temps = []
#             for i in range(len(articles)):
#                 href = articles[i].get_attribute('href')
#                 create_time = dates[i].get_attribute('t')
#                 img = imgs[i].find_element_by_tag_name('img').get_attribute('src')
#                 temp = img.split('&url=')
#                 temp.insert(1, '&w=210&h=105&url=')
#                 img = "".join(temp)

#                 temps.append([href, datetime.datetime.fromtimestamp(float(create_time)), img])

#             for temp in temps:
#                 href = temp[0]
#                 create_time = temp[1]
#                 print href, create_time

#                 # 4.跳转到微信
#                 driver.get(href)
#                 time.sleep(6)
#                 title = driver.find_elements_by_id('activity-name')[0].text
#                 content = driver.find_elements_by_id('js_content')[0].get_attribute('innerHTML')
#                 url = driver.current_url
#                 img = temp[2]
#                 # try:
#                 #     img = img_prefix + driver.find_elements_by_id('js_cover')[0].get_attribute('src')
#                 # except Exception, e:
#                 #     print traceback.print_exc()
#                 #     continue

#                 print title
#                 print url
#                 print img

#                 response = requests.post(
#                     "http://%s/toutiao/sync_toutiao" % host,
#                     data = {
#                         'mp_id': mp['mp_id'],
#                         'title': title,
#                         'content': content,
#                         'url': url,
#                         'img': img,
#                         'create_time': str(create_time)
#                     }
#                 )

#                 result = json.loads(response.text)

#                 if result['code'] == 0:
#                     print u'成功!'
#                 else:
#                     print u'失败！！[%s]' % result['code']

#                     if result['code'] == 2:
#                         print u'此公众号暂无更新，跳过...'
#                         time.sleep(80)
#                         break

#         except Exception, e:
#             print traceback.print_exc()
#             continue

#         driver.quit()


    

if  __name__=='__main__':
    # while 1:
    #     time.sleep(10)
    #     sync2()

    WeixinSpider().sync()


