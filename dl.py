import os
import time
import requests
from io import BytesIO
import zipfile


class download(object):
    basedir = 'download'

    def __init__(self):
        # 年月日做文件夹名
        tdir = time.strftime('%Y-%m-%d')
        ddir = self.basedir + '/' + tdir
        if not os.path.exists(ddir):
            os.mkdir(ddir)
        self.basedir = ddir + '/'

    def unzip(self, r, name):
        # system('unzip content.zip -d ' + self.basedir)
        zipdata = BytesIO()
        zipdata.write(r.content)

        ddir = self.basedir + '/' + name
        if not os.path.exists(ddir):
            os.mkdir(ddir)

        with zipfile.ZipFile(zipdata, 'r') as zfile:
            for filename in zfile.namelist():
                data = zfile.read(filename)
                with open(ddir + '/' + filename, 'w+b') as f:
                    f.write(data)

    def download(self, url, name):
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Referer': 'http://www.pixiv.net/ranking_area.php?type=detail&no=6'
        }
        try:
            r = requests.get(url, headers=header, timeout=5)

            if r.status_code == 200:
                filename = self.basedir + name + url[-4:]

                if os.path.exists(filename.replace('/', '')):
                    filename = self.basedir + name + 'o' + url[-4:]

                with open(filename, 'wb') as f:
                    f.write(r.content)
            else:
                print('重试。。')
                self.download(url, name)
        except Exception as e:
            print('重试。。')
            print(e)
            self.download(url, name)
            # f.close()

        print(name + " downloaded~")

    def download_muli(self, url, ref_url, dir, page):
        header = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Referer': ref_url
        }

        ddir = self.basedir + '/' + dir
        if not os.path.exists(ddir):
            os.mkdir(ddir)

        try:
            r = requests.get(url, headers=header)

            if r.status_code == 200:
                with open(ddir + '/' + str(page) + url[-4:], 'wb') as f:
                    f.write(r.content)
            else:
                # print(r.status_code)
                # print(r.text)
                print(url)
                print('重试ing')
                self.download_muli(url, ref_url, dir, page)
        except Exception as e:
            print(e)
