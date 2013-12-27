#! /usr/bin/env python
import urllib2
import urllib
import cookielib
import os
import re
import copy
import time
import json

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


def get_by_url(url, params):
    url = '%s?%s' %(url, urllib.urlencode(params))
    req = urllib2.Request(url = url)
    resp = urllib2.urlopen(req).read()
    return resp

class BaiduMusicBox(object):

    def __init__(self, username, password):
        super(BaiduMusicBox, self).__init__()
        self.data = copy.deepcopy(PostData)

        self.data.update({
            'username': username,
            'password': password
        })
        self.is_login = False
        self.cjar = cookielib.LWPCookieJar(COOKIE_FILE)
        if os.path.isfile(COOKIE_FILE):
            self.cjar.revert()
            for cookie in self.cjar:
                if cookie.name == "BDUSS" and cookie.domain == ".baidu.com":
                    print 'login Success'
                    self.is_login = True
                    self.__bduss = cookie.value
                    print 'cookie dbuss: ', self.__bduss
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cjar))
        urllib2.install_opener(opener)
        urllib2.urlopen('http://play.baidu.com/')


    def get_token(self):
        print 'request token...'
        response = urllib2.urlopen(apiUrl).read()
        tokenreg = re.search(
            "bdPass\.api\.params\.login_token='(?P<tokenVal>\w+)';", response)
        if tokenreg:
            token = tokenreg.group("tokenVal")
            return token
        return None

    def __signin(self):
        print 'login...'
        self.data["token"] = self.get_token()

        req = urllib2.Request(
            url=loginUrl,
            headers=HTTPHeader,
            data=urllib.urlencode(self.data))

        resp = urllib2.urlopen(req).read()
        bdussreg = re.search("hao123Param=(?P<bdussVal>\w+)&", resp)
        if bdussreg:
            self.__bduss = bdussreg.group('bdussVal')
            print 'get __bduss:', self.__bduss

        error_code = re.findall("error\=(\d+)", resp)
        if error_code:
            error_code = int(error_code[0])
            if error_code == 257:
                print 'need Verification Code'
            elif error_code == 2:
                print 'invlid user'
            elif error_code == 4:
                print 'password error'

        print 'Login Success!'
        self.is_login = True
        self.cjar.save()

        self.__login_cross_domain()

    def __login_cross_domain(self):
        params = {
            'bdu' : self.__bduss,
            't'   : int(time.time())
        }
        url='%s?%s' % (crossUrl,urllib.urlencode(params))
        req = urllib2.Request(url)
        print 'cross domain '
        urllib2.urlopen(req)
        print 'cross domain success'
        self.cjar.save()

    def get_playlist(self):
        if not self.is_login:
            print 'no login.'
            self.__signin()
        params = {
            't'   : int(time.time())
        }
        print 'Request play list...'
        resp = get_by_url(playlistUrl, params)
        return json.loads(resp)
        
    def download_playlist(self):
        playlist = self.get_playlist()
        if playlist['errorCode'] == 22000:
            playlist = playlist['data']['play_list']
            if playlist:
                for l in playlist:
                    self.get_list_detail(l['listId'])
    
    def get_list_detail(self, listid):
        params = {
            'sid' : 1,
            'playListId' : listid,
            '_' : int(time.time())
        }
        print 'get playlist detail for playListId', listid
        resp = get_by_url(playlistDetailUrl, params)
        resp_data = json.loads(resp)
        ids = resp_data['data']['songIds']
        print 'get songIds', ids
        if ids:
            for sid in ids:
                self.get_song_format(sid)

    def get_song_format(self, songid):
        params = {'songIds': songid}
        print 'get song format...', songid
        resp = get_by_url(songFormatUrl, params)
        resp_data = json.loads(resp)
        formats = resp_data['data']['data']
        formats.pop('original')
        #songIds=516015&rate=320&format=mp3
        for k,v in formats.items():
            pp = {
                'songIds' : v['songId'],
                'rate' : v['rate'],
                'format' : v['format']
            }
            filename = '%s_%s.%s' %(v['songId'],k, v['format'])
            print 'download .', filename
            response = get_by_url(downloadUrl, pp)
            f = open(filename, 'wb+')
            f.write(response)
            f.close()

            print filename, 'done!'





baidubox = BaiduMusicBox('594611460@qq.com', '19871010')
baidubox.download_playlist()
