#!/usr/bin/env python2
# coding:utf-8



from box.music import BaiduMusicBox

BAIDU_USERNAME = ''
BAIDU_PASSWORD = ''



if __name__ == '__main__':
    parser = optparse.OptionParser()
    baidubox = BaiduMusicBox(BAIDU_USERNAME, BAIDU_PASSWORD)
    baidubox.fetch()


