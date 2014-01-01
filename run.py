#!/usr/bin/env python2
# coding:utf-8

from box.music import BaiduMusicBox

BAIDU_USERNAME = '594611460@qq.com'
BAIDU_PASSWORD = 'xxxxxx'

if __name__ == '__main__':
    baidubox = BaiduMusicBox(BAIDU_USERNAME, BAIDU_PASSWORD)
    baidubox.fetch()
