# -*- coding:utf-8 -*-
# author:zjl

from bs4 import BeautifulSoup
from urllib import request
import threading
import requests
import time
import json
import os


class CrawlThread(threading.Thread):
    def __init__(self, user_id, keyword_list, store_path, page_list):
        threading.Thread.__init__(self)
        self.user_id = user_id
        self.page_list = page_list
        self.keyword_list = keyword_list
        self.store_path = store_path

    def get_img_list(self, link_id):
        url = 'https://api.xiaoheihe.cn/bbs/app/link/tree?link_id={}&limit=20&offset=0&owner_only=0'.format(link_id) + \
               '&sort_filter=&os_type=web&version=999.0.0&hkey=39336d21ec68c3bbaf36525da1be5f1d&_time={}'.format(time.time())
        try:
            res = []
            dictionary = json.loads(request.urlopen(url).read())
            dic_list = json.loads(dictionary['result']['link']['text'])
            for dic in dic_list:
                if dic['type'] == 'img':
                    res.append(dic['url'])
            return res
        except:
            return []

    def run(self):
        for page_index in self.page_list:
            dictionary = json.loads(request.urlopen(get_url(user_id=self.user_id, offset=20*page_index)).read())
            for passage in dictionary['post_links']:
                title = passage['title'].replace('/', '|')
                flag = 0
                if not self.keyword_list:                                   # no keyword
                    flag = 1
                else:
                    for keyword in self.keyword_list:                       # or any keyword in passage title
                        if keyword in title:
                            flag = 1
                if flag:
                    if title not in os.listdir(self.store_path):            # dir not exists
                        os.mkdir(os.path.join(self.store_path, title))
                    save_path = os.path.join(self.store_path, title)
                    # passage_url = passage['share_url']
                    link_id = passage['share_url'].split('=')[-1]
                    data = self.get_img_list(link_id)
                    for i, img in enumerate(data):
                        image = requests.get(img)
                        image_content = image.content
                        with open(os.path.join(save_path, str(i)+'.jpg'), 'wb+') as f:
                            f.write(image_content)
            time.sleep(1)


def get_url(user_id=11033422, offset=0):
    local_time = str(int(time.time()))
    prefix = 'https://api.xiaoheihe.cn/bbs/web/profile/post/links?'
    suffix = 'userid={}&limit=20&offset={}&os_type=web&version=999.0.0&hkey=5560ac75e429bb94ee369d789876f875&_time={}'.format(str(user_id), str(offset), local_time)
    base_url = prefix + suffix
    return base_url


def crawler(user_id, store_path, keyword_list, thread_num=4):
    # main_url = str(request.urlopen(get_url(user_id)).read(), 'utf-8')
    # soup = BeautifulSoup(main_url, 'lxml')
    dictionary = json.loads(request.urlopen(get_url(user_id)).read())
    user_name = dictionary['user']['username']
    page_num = dictionary['total_page']
    if user_name not in os.listdir(store_path):
        os.mkdir(os.path.join(store_path, user_name))
    page_range = list(range(page_num))
    div = page_num // thread_num + 1
    threads = []

    for i in range(thread_num):
        if len(page_range) > div:
            page_list = page_range[:div]
            page_range = page_range[div:]
        else:
            page_list = page_range
            page_range = []
        threads.append(CrawlThread(user_id, keyword_list, os.path.join(store_path, user_name), page_list))
    for i in threads:
        i.start()
    for i in threads:
        i.join()


if __name__ == "__main__":
    # crawler(user_id=11033422, store_path='../../../data/', thread_num=4, keyword_list=[])
    crawler(user_id=1366505, store_path='../../../data/', thread_num=4, keyword_list=['壁纸'])
# https://docs.python.org/zh-cn/3/tutorial/classes.html