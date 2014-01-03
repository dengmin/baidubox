#! /usr/bin/env python
# coding:utf-8

HTTPHeader = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    'Accept-Language': 'zh-CN,en-US;q=0.8',
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Host": 'passport.baidu.com',
    "Origin": 'http://play.baidu.com',
    "Referer": 'http://play.baidu.com/',
    "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
}

PostData = {
    'staticpage': 'http://play.baidu.com/player/v2Jump.html',
    'charset': 'UTF-8',
    'tpl': "music",
    'safeflg': 0,
    'isPhone': False,
    'u': "http://play.baidu.com",
    'quick_user': 0,
    'loginmerge': True,
    'loginType': 'dialogLogin',
    'splogin': 'rate',
    'callback': "parent.bd__pcbs__whhd4w",
    'verifycode': "",
    'mem_pass': "on",
}

COOKIE_FILE = '.baidu_cookie'

apiUrl = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=music&tangram=true"
loginUrl = 'https://passport.baidu.com/v2/api/?login'
crossUrl = 'http://user.hao123.com/static/crossdomain.php'
playlistUrl = 'http://play.baidu.com/data/playlist/getlist'
playlistDetailUrl = 'http://play.baidu.com/data/playlist/getDetail'
songFormatUrl = 'http://yinyueyun.baidu.com/data/cloud/download'
downloadUrl = 'http://yinyueyun.baidu.com/data/cloud/downloadsongfile'
songInfoUrl = 'http://play.baidu.com/data/music/songinfo'
tingApiUrl = 'http://tingapi.ting.baidu.com/v1/restserver/ting'
collectListUrl = 'http://play.baidu.com/data/mbox/collectlist'
