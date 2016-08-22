# coding:UTF-8

import urllib
import urllib2
import cookielib
from download import *
from bs4 import BeautifulSoup


class PixivSpider(object):
    base = "http://www.pixiv.net/"

    def __init__(self, pid, password):
        self.opener = self.login(pid, password)
        self.dl = download(self.opener)
        pass

    def login(self, pid, pwd):
        url = 'https://www.pixiv.net/login.php'

        # build_opener函数是用来自定义opener对象的函数

        login_data = urllib.urlencode({
            'mode': 'login',
            'pass': pwd,  # 你的账号密码
            'pixiv_id': pid,  # 你的pixivid
            'return_to': '/',
            'skip': 1
        })
        # 这个是p站的登陆信息
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Referer': 'https://www.pixiv.net/login.php?return_to=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        # 登陆所使用的请求头信息
        request = urllib2.Request(
            url,
            data=login_data,
            headers=header)
        try:
            filename = 'cookie.txt'
            cookie = cookielib.MozillaCookieJar(filename)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

            response = opener.open(request)
            # 利用前面的请求头信息与cookie信息进行登陆
            cookie.save(ignore_discard=True, ignore_expires=True)
            return opener
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print "ERROR!!!reason:", e.reason
            return False

    def international_spider(self, opener):
        # todo: open可能会报错
        url = "http://www.pixiv.net/ranking_area.php?type=detail&no=6"
        page = opener.open(url)
        content = page.read()
        main_soup = BeautifulSoup(content, 'lxml')
        # 全是jpg?
        all_div = main_soup.find_all("div", "ranking-item")
        for div in all_div:
            # rank = div.h1.a.string
            # todo：存数据库。
            data = div.find(class_="data")
            author = data.find(class_="icon-text").string
            name = data.a.string

            work_wrapper = div.find(class_="work_wrapper")
            min_src = work_wrapper.find("img", class_="_thumbnail")['data-src']
            url = work_wrapper.a['href']
            src = self.member_illust_spider(self.base + url)
            print (src)
            # self.download(min_src, opener)
            try:
                self.dl.download(min_src, name + "_sm")
                self.dl.download(src, name)
            except Exception, e:
                print e,
                print "  " + min_src + "  " + name + "  download fail"

            # break
        pass

    def member_illust_spider(self, url):
        # todo：其他referer？
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Referer': 'http://www.pixiv.net/ranking_area.php?type=detail&no=6'
        }
        request = urllib2.Request(
            url=url,
            headers=header
        )

        page = self.opener.open(request)
        content = page.read()
        main_soup = BeautifulSoup(content, 'lxml')
        return main_soup.find('div', class_="_layout-thumbnail").img['src']

    def search(self, name):
        url = "http://www.pixiv.net/search.php"
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        }
        get_data = {
            'word': name,
            'order': 'date_d',
            'p': 1
        }
        search_data = urllib.urlencode(get_data)

        request = urllib2.Request(
            url,
            data=search_data,
            headers=header)

        page = self.opener.open(request)

        self.all_dist = {}

        content = page.read()
        i = 1
        while 1:
            tag = self.find(content)
            print 'page %d th over..' % i
            i += 1
            print tag
            if tag:
                # header['Referer'] = url+'?'+search_data
                get_data['p'] = i
                search_data = urllib.urlencode(get_data)
                # print (self.base+str(tag))
                request = urllib2.Request(
                    url=url+str(tag),
                    data=search_data,
                    headers=header)
                page = self.opener.open(request)
                content = page.read()
            else:
                break
            if i == 5:
                break
        fp = open(name+".txt",'w')
        sorted_key = sorted(self.all_dist.keys(), reverse=True)
        for i in sorted_key:
            fp.write("favor_num:"+str(i)+"--")
            fp.write(str(self.all_dist[i]))
            fp.write("\n")
        # print self.all_dist
        fp.close()


    def find(self, page):
        # print page
        main_soup = BeautifulSoup(page, "lxml")
        items = main_soup.find_all(class_="image-item")

        for item in items:
            ul = item.ul
            if ul is None:
                continue
            else:
                url = item.a['href']
                #/member_illust.php?mode=medium&illust_id=58385142
                illust_id =url.split('illust_id=')[1]
                collection_num = int(ul.a.text)
                if collection_num in self.all_dist.keys():
                    self.all_dist[collection_num].append(illust_id)
                else:
                    self.all_dist[collection_num] = [illust_id]

        nextspan = main_soup.find(class_="next")
        if nextspan is None:
            return False
        else:
            try:
                return nextspan.a['href']
            except Exception,e:
                print e
                return False


    def start(self):
        if not self.opener:
            return False

        self.international_spider(self.opener)
        # name = raw_input('what do you want to search?')
        # self.search(name)
        pass


if __name__ == '__main__':
    ps = PixivSpider('xxx', 'xxx')
    ps.start()
