#! /usr/bin/env python
# coding:utf-8
import urllib2
import urllib
import cookielib
import os
import re
import copy
import time
import json
import sys
from download import download

BAIDU_USERNAME = '594611460@qq.com'
BAIDU_PASSWORD = 'xxxxxx'

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
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cjar))
        urllib2.install_opener(opener)
        urllib2.urlopen('http://play.baidu.com/')

    def request(self, url, method='GET', params={}, headers={}):
        params = urllib.urlencode(params)
        if method == 'POST':
            request = urllib2.Request(url, params)
        else:
            url = '%s?%s' % (url, params)
            request = urllib2.Request(url, None)
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print "Error code: ", e
        else:
            self.cjar.save()
            return response.read()

    def get_token(self):
        print 'request token...'
        response = self.request(url=apiUrl)
        tokenreg = re.search(
            "bdPass\.api\.params\.login_token='(?P<tokenVal>\w+)';", response)
        if tokenreg:
            token = tokenreg.group("tokenVal")
            return token
        return None

    def __signin(self):
        print 'login...'
        self.data["token"] = self.get_token()
        resp = self.request(url=loginUrl, headers=HTTPHeader,
                            params=self.data, method='POST')
        bdussreg = re.search("hao123Param=(?P<bdussVal>\w+)&", resp)
        print bdussreg
        if bdussreg:
            self.__bduss = bdussreg.group('bdussVal')

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
            self.__login_cross_domain()
        else:
            print 'login failure'
            sys.exit(-1)

    def __login_cross_domain(self):
        params = {
            'bdu': self.__bduss,
            't': int(time.time())
        }
        print 'cross domain '
        self.request(url=crossUrl, params=params)

    def get_playlist(self):
        '''获取我的歌单'''
        if not self.is_login:
            print 'no login.'
            self.__signin()

        print 'Request play list...'
        resp = self.request(url=playlistUrl, params={'t': int(time.time())})
        return json.loads(resp)

    def download_playlist(self):
        playlist = self.get_playlist()
        if playlist['errorCode'] == 22000:
            playlist = playlist['data']['play_list']
            if playlist:
                for l in playlist:
                    songids = self.get_list_detail(l['listId'])
                    self.get_song_info(songids)

    def get_list_detail(self, listid):
        '''获取一个歌单下面的所有歌曲的id'''
        params = {
            'sid': 1,
            'playListId': listid,
            '_': int(time.time())
        }
        print 'get playlist detail for playListId', listid
        resp = self.request(url=playlistDetailUrl, params=params)
        resp_data = json.loads(resp)
        ids = resp_data['data']['songIds']
        return ids

    def get_song_info(self, songids):
        '''
        传入歌曲的id列表 返回这些歌曲的详细信息
        '''
        print 'get songinfo.'
        response = self.request(
            url=songInfoUrl, method='POST', params={'songIds': ','.join(songids)})
        response = json.loads(response.decode('gbk'))
        songlist = response['data']['songList']
        for song in songlist:
            self.do_download(song)

    def do_download(self, song):
        song_formats = self.get_song_format(song.get('songId'))
        for k, v in song_formats.items():
            pp = {
                'songIds': v['songId'],
                'rate': v['rate'],
                'format': v['format']
            }
            filename = '%s_%s.%s' % (song.get('songName'), k, v['format'])
            download(downloadUrl, pp, filename)

    def get_song_format(self, songid):
        if songid:
            params = {'songIds': songid}
            print 'get song format...', songid
            resp = self.request(url=songFormatUrl, params=params)
            resp_data = json.loads(resp)
            formats = resp_data['data']['data']
            formats.pop('original')
            return formats


if __name__ == '__main__':
    baidubox = BaiduMusicBox(BAIDU_USERNAME, BAIDU_PASSWORD)
    baidubox.download_playlist()
