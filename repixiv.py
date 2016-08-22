# -*- coding: utf-8 -*-
"""
Created on 2016-08-22

@author: Tmn07
"""

import requests
from bs4 import BeautifulSoup
from dl import download
import re
# import zipfile
from os import system

def write_down(data, filename='test.html'):
    fp = open(filename, 'w')
    fp.write(data)
    fp.close()


# p1 = repixiv.PixivSpider('519043202','qq963852741')
class PixivSpider(object):
    base = "http://www.pixiv.net/"

    def __init__(self, pid, pwd):
        self.s = requests.Session()
        self.login(pid, pwd)
        print('登陆成功')
        self.dl = download()

    def login(self, pid, pwd):
        url = 'https://www.pixiv.net/login.php'

        login_data = {
            'mode': 'login',
            'pass': pwd,  # 你的账号密码
            'pixiv_id': pid,  # 你的pixivid
            'return_to': '/',
            'skip': 1
        }

        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Referer': 'https://www.pixiv.net/login.php?return_to=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        try:
            r = self.s.post(url, headers=header, data=login_data, timeout=10)
            # print (r.status_code)
        except Exception as e:
            print (e)
            exit()

    def get_originurl(self, url):
        # 格式有问题。。
        l1 = url.split('/')
        del l1[3]
        del l1[3]
        l1[3] = 'img-original'
        l1[-1] = l1[-1][:-15] + l1[-1][-4:]
        return '/'.join(l1)

    def international_spider(self):
        url = "http://www.pixiv.net/ranking_area.php?type=detail&no=6"
        try:
            r = self.s.get(url)
            content = r.text
            main_soup = BeautifulSoup(content, 'lxml')

            all_div = main_soup.find_all("div", "ranking-item")
            for div in all_div:
                # rank = div.h1.a.string
                # todo：存数据库？
                data = div.find(class_="data")
                author = data.find(class_="icon-text").string
                name = data.a.string

                work_wrapper = div.find(class_="work_wrapper")
                min_src = work_wrapper.find("img", class_="_thumbnail")['data-src']

                url = work_wrapper.a['href']
                if 'multiple' in work_wrapper.a['class']:
                    # 图集
                    self.member_illust_spider(self.base + url, 1)
                elif 'ugoku-illust' in work_wrapper.a['class']:
                    # 动图
                    pass
                else:

                    src = self.member_illust_spider(self.base + url)
                    print (src)
                    try:
                        self.dl.download(min_src, name + "_sm")
                        self.dl.download(src, name)
                    except Exception as e:
                        print (e)
                        print ("  " + min_src + "  " + name + "  download fail")

        except Exception as e:
            print (e)
            exit()

    def member_illust_spider(self, url, tag=0):
        # todo: 图集？动图？
        if tag == 0:
            try:
                r = self.s.get(url)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'lxml')
                    return soup.find('div', class_="ui-modal-close-box").img['data-src']
                else:
                    print (url)
                    print('重试ing')
                    self.member_illust_spider(url, 0)
            except Exception as e:
                print (e)
        elif tag == 1:
            # manga里获取页数。
            url = url.replace('medium', 'manga')
            r = self.s.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            # write_down(r.text)
            page_num = soup.find('span', class_='total').string
            print (page_num)
            manga_url = url
            manga_big_url = url.replace('manga', 'manga_big')
            for i in range(int(page_num)):
                # manga_big 获取originalurl和name
                header = {
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
                    'Referer': manga_url
                }
                url = manga_big_url + '&page=' + str(i)

                r = self.s.get(url, headers=header)
                write_down(r.text)
                soup = BeautifulSoup(r.text, 'lxml')
                img_url = soup.img['src']
                dirname = soup.title.string.split('/')[0]
                print(img_url)
                self.dl.download_muli(img_url, url, dirname)

                # r = self.get_originurl()
        elif tag == 2:
            r = self.s.get(url)
            write_down(r.text)
            pattern = re.compile('FullscreenData.*?:"(.*?)\.zip')
            res = pattern.search(r.text).groups()
            url = res[0] + '.zip'
            url = url.replace('\\', '')
            print (url)
            r = self.s.get(url)
            with open('content.zip','wb') as f:
                f.write(r.content)
            self.dl.unzip()

            # 'http:\\/\\/i1.pixiv.net\\/img-zip-ugoira\\/img\\/2016\\/08\\/16\\/00\\/01\\/05\\/58466372_ugoira1920x1080.zip'


if __name__ == '__main__':
    ps = PixivSpider('xxx', 'xxx')
    ps.international_spider()
    # ps.member_illust_spider('http://www.pixiv.net/member_illust.php?mode=medium&illust_id=58485741',1)
    # ps.member_illust_spider('http://www.pixiv.net/member_illust.php?mode=medium&illust_id=58466372', 2)
