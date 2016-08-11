import os
import urllib2


class download(object):
    def __init__(self, opener):
        self.opener = opener
        if not os.path.exists("download/"):
            os.mkdir('download')

    def download(self, url, name):
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

        jpg = page.read()

        f = open('download/' + name + '.jpg', 'wb')
        f.write(jpg)
        f.close()
        print(name + " downloaded~")
