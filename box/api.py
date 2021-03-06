#!/usr/bin/env python2
# coding:utf-8
import json
import time
import re
import copy
import os
from box import errors
from box import constants

COOKIE_FILE = constants.COOKIE_FILE

class BaiduAPI(object):
    def __init__(self, opener, username, password):
        super(BaiduAPI, self).__init__()
        self.opener = opener
        self.data = copy.deepcopy(constants.PostData)
        self.data.update({
            'username': username,
            'password': password
        })
        self.is_login = False
        self.__check_cookie()

    def __check_cookie(self):
        if os.path.isfile(COOKIE_FILE):
            self.opener.cjar.revert(COOKIE_FILE)
            for cookie in self.opener.cjar:
                if cookie.name == "BDUSS" and cookie.domain == ".baidu.com":
                    self.is_login = True
                    self.__bduss = cookie.value
                    print 'already login'
                    break

    def request(self, url, method='GET', params={}, headers={}):
        return self.opener.open(url, method, params, headers)

    def get_token(self):
        response = self.opener.open(url=constants.apiUrl)
        tokenreg = re.search("bdPass\.api\.params\.login_token='(?P<tokenVal>\w+)';", response)
        if tokenreg:
            return tokenreg.group("tokenVal")
        raise errors.RequestTokenError('get token fail!')

    def __process_cross_domain(self):
        params = {
            'bdu': self.__bduss,
            't': int(time.time())
        }
        self.request(url=constants.crossUrl, params=params)

    def __parser_errorcode(self, error_code):
        if error_code:
            error_code = int(error_code[0])
            if error_code == 257:
                raise errors.NeedVerificationError('need Verification Code')
            elif error_code == 2:
                raise errors.InvalidUserError('invlid user')
            elif error_code == 4:
                raise errors.PasswordError('password error')

    def login(self):
        self.request(url='http://play.baidu.com/')
        self.data["token"] = self.get_token()
        response = self.request(url=constants.loginUrl,
                headers=constants.HTTPHeader,
                params=self.data, method='POST')
        bdussreg = re.search("hao123Param=(?P<bdussVal>\w+)&", response)
        error_code = re.findall("error\=(\d+)", response)
        if bdussreg:
            self.__bduss = bdussreg.group('bdussVal')
            self.__parser_errorcode(error_code)

            self.__process_cross_domain()
        else:
            if error_code:
                self.__parser_errorcode(error_code)
            raise errors.LoginError('login error. please try again.')

    def __process_data(self, response):
        response = json.loads(response)
        if response.get('errorCode') == 22000 or response.get('errorCode') == 0:
            if response.get('data'):
                return response.get('data')

    def get_playlist(self):
        '''获取我的歌单'''
        if not self.is_login:
            self.login()
        response = self.request(url=constants.playlistUrl, params={'t': int(time.time())})
        response = self.__process_data(response)
        if response:
            return response.get('play_list')

    def get_list_detail(self, listid):
        '''获取一个歌单下面的所有歌曲的id'''
        if not self.is_login:
            self.login()
        params = {
            'sid': 1,
            'playListId': listid,
            '_': int(time.time())
        }
        response = self.request(url=constants.playlistDetailUrl, params=params)
        response = self.__process_data(response)
        if response:
            return response.get('songIds')

    def get_song_info(self, songids):
        '''
        传入歌曲的id列表 返回这些歌曲的详细信息
        '''
        if not self.is_login:
            self.login()
        if isinstance(songids, list):
            response = self.request(url=constants.songInfoUrl, method='POST',
                params={'songIds': ','.join(songids)})
            response = self.__process_data(response)
            if response:
                return response.get('songList')
        else:
            raise errors.ApiError('parameter songids type error, it must be list')

    def get_song_format(self, songid):
        """获取一首歌曲所支持的音频格式"""
        if not self.is_login:
            self.login()
        if songid:
            response = self.request(url=constants.songFormatUrl, params={'songIds': songid})
            response = self.__process_data(response)
            if response:
                return response.get('data')

    def get_collect_list(self, start=0, size=200):
        """我收藏的音乐"""
        if not self.is_login:
            self.login()
        params = {
            'cloud_type' : 0,
            'type'       : 'song',
            'start'      : start,
            'size'       : size,
            '_'          : int(time.time())
        }
        response = self.request(url=constants.collectListUrl, params=params,headers=constants.PLAY_HTTPHEADER)
        response = self.__process_data(response)
        if response:
            return response

    def get_listen_history(self, stype='late',start=0, size=200):
        """查询我的播放记录
        stype参数: often(我最常听), late(播放记录)
        返回 {'songList':[], 'totle': 0}
        """
        if not self.is_login:
            self.login()
        params = {
            'type'       : stype,
            'start'      : start,
            'size'       : size,
            '_'          : int(time.time())
        }
        response = self.request(url=constants.listenHistoryUrl, params=params,headers=constants.PLAY_HTTPHEADER)
        return self.__process_data(response)

    def get_download_history(self):
        """我的下载历史
        return {"songList":[],}
        """
        if not self.is_login:
            self.login()
        params = {
            'start'      : start,
            'size'       : size,
            '_'          : int(time.time())
        }
        response = self.request(url=constants.downloadHistoryUrl, params=params,headers=constants.PLAY_HTTPHEADER)

    def search(self, keyword,page_no=1, page_size=30):
        """ Search songs with keywords"""
        if keyword:
            params = {
                "method": "baidu.ting.search.common",
                "format": "json",
                "from": "bmpc",
                "version": "2.4.0",
                "page_size": page_size,
                "page_no": page_no,
                "query": keyword,
            }
            headers = {
            "Referer": "http://pc.music.baidu.com",
            "User-Agent": "bmpc_1.0.0"
            }
            response = self.request(url=constants.tingApiUrl,params=params, headers=headers)
            return json.loads(response)
