# -*- coding: utf-8 -*-

import requests, re, json, time, datetime
from pyquery import PyQuery as pq

host = "www.a.com:8000"

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

def sync():
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

    mps = get_mps()

    for mp in mps:
        url = u"http://weixin.sogou.com/gzhjs?openid=%s" % mp['open_id']
        
        try:
            resp = requests.get(
                url,
                headers = headers,
                timeout = 15,
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

                    print url
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
                        print '成功!'
                    else:
                        print '失败！！[%s]' % result['code']
                except Exception, e:
                    print e
                    continue

        except Exception, e:
            print e
            continue

if __name__ == "__main__":
    sync()