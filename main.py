# -*- coding:utf-8 -*-
# Time: 2022/7/2 16:21
# Author: 佚名

import re
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor

def get_page(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    html = response.text
    if '<relative-time datetime=' in html:
        title = re.findall('<title>.*?/(.*?)</title>', html)[0].replace(' · GitHub', '')
        updatetime = re.findall('<relative-time datetime="(.*?)".*?</relative-time>', html)[0]
        utc_date2 = datetime.datetime.strptime(updatetime, "%Y-%m-%dT%H:%M:%SZ")
        local_date = utc_date2 + datetime.timedelta(hours=8)
        updatetime = datetime.datetime.strftime(local_date, "%Y-%m-%d")
        info.append(title + '[' + updatetime + '] ' + url)
    else:
        title = re.findall('<title>.*?/(.*?)</title>', html)[0].replace(' · GitHub', '')
        updatetime = re.findall('<local-time datetime="(.*?)".*?</local-time>', html)[0]
        utc_date2 = datetime.datetime.strptime(updatetime, "%Y-%m-%dT%H:%M:%SZ")
        local_date = utc_date2 + datetime.timedelta(hours=8)
        updatetime = datetime.datetime.strftime(local_date, "%Y-%m-%d")
        info.append(title + '[' + updatetime + '] ' + url)

def check():
    new_text = []
    update_text = ''
    with open('url.txt', 'r', encoding='utf-8') as f:
        urls = f.read().split('\n')
        f.close()
        spool = 24
        # 监测更新
        with ThreadPoolExecutor(max_workers=spool) as pool:
            pool.map(get_page, urls)
        num = 0
        for item in info:
            if num > 0:
                start_text = '\n'
            else:
                start_text = ''
            title = re.findall('(.*?)\[', item)[0]
            with open('update_info.txt', 'r', encoding='utf-8') as f:
                text = f.read()
                if title in text:
                    new_time = int(re.findall('\[(.*?)]', item)[0].replace('-', ''))
                    time = int(re.findall('%s\[(.*?)]' % title, text)[0].replace('-', ''))
                    url = re.findall('] (.*?)', item)[0]
                    old_title = item.replace(re.findall('\[(.*?)]', item)[0],
                                             re.findall('%s\[(.*?)]' % title, str(text))[0])
                    if new_time > time:
                        item = start_text + item
                        new_text.append(item)
                        update_text = update_text + '[NEW]' + title + ' 更新时间：' + str(new_time)
                        print('[NEW]' + title, '更新时间：', new_time, url)
                    else:
                        old_title = start_text + old_title
                        new_text.append(old_title)
                else:
                    item = start_text + item
                    new_text.append(item)
            num = num + 1
    with open('update_info.txt', 'w', encoding='utf-8') as f:
        for len in new_text:
            f.write(len)
    f.close()
    send(update_text)

def send(update_text):
    if update_text == '':
        print('暂无更新')
    else:
        params = {
            'text': 'GitHub 监控',
            'desp': update_text,
        }
        token = '自行申请Token'
        requests.post(token, params=params)
if __name__ == '__main__':
    info = []
    check()
