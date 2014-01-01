#! /usr/bin/env python
# coding:utf-8
import os
import re
import copy
import time
import json
from box import constants
from box import errors
from box.opener import BuiltinOpener
from box.download import download

COOKIE_FILE = constants.COOKIE_FILE

class BaiduMusicBox(object):

    def __init__(self, username, password):
        super(BaiduMusicBox, self).__init__()
        self.data = copy.deepcopy(constants.PostData)
        self.opener = BuiltinOpener(COOKIE_FILE)
        self.data.update({
            'username': username,
            'password': password
        })

        self.is_login = False
        if os.path.isfile(COOKIE_FILE):
            self.opener.cjar.revert(COOKIE_FILE)
            for cookie in self.opener.cjar:
                if cookie.name == "BDUSS" and cookie.domain == ".baidu.com":
                    print 'already Login'
                    self.is_login = True
                    self.__bduss = cookie.value

    def __get_token(self):
        print 'request token...'
        response = self.opener.open(url=constants.apiUrl)
        tokenreg = re.search(
            "bdPass\.api\.params\.login_token='(?P<tokenVal>\w+)';", response)
        if tokenreg:
            token = tokenreg.group("tokenVal")
            return token
        else:
            raise errors.RequestTokenError('get token fail!')

    def __signin(self):
        print 'login...'
        self.data["token"] = self.__get_token()
        resp = self.opener.open(url=constants.loginUrl,
                headers=constants.HTTPHeader,
                params=self.data, method='POST')
        bdussreg = re.search("hao123Param=(?P<bdussVal>\w+)&", resp)
        if bdussreg:
            self.__bduss = bdussreg.group('bdussVal')
            error_code = re.findall("error\=(\d+)", resp)
            if error_code:
                error_code = int(error_code[0])
                if error_code == 257:
                    raise errors.NeedVerificationError('need Verification Code')
                elif error_code == 2:
                    raise errors.InvalidUserError('invlid user')
                elif error_code == 4:
                    raise errors.PasswordError('password error')
            print 'Login Success!'
            self.is_login = True
            self.__login_cross_domain()
        else:
            raise error.LoginError('login error')

    def __login_cross_domain(self):
        params = {
            'bdu': self.__bduss,
            't': int(time.time())
        }
        print 'cross domain '
        self.opener.open(url=constants.crossUrl, params=params)

    def get_playlist(self):
        '''获取我的歌单'''
        if not self.is_login:
            print 'no login.'
            self.__signin()

        print 'Request play list...'
        resp = self.opener.open(url=constants.playlistUrl, params={'t': int(time.time())})
        return json.loads(resp)

    def download_playlist(self):
        playlist = self.get_playlist()
        if playlist['errorCode'] == 22000:
            playlist = playlist['data']['play_list']
            if playlist:
                for l in playlist:
                    print 'get playlist detail for playList >> ', l['listTitle']
                    songids = self.get_list_detail(l['listId'])
                    self.get_song_info(songids)

    def get_list_detail(self, listid):
        '''获取一个歌单下面的所有歌曲的id'''
        params = {
            'sid': 1,
            'playListId': listid,
            '_': int(time.time())
        }
        resp = self.opener.open(url=constants.playlistDetailUrl, params=params)
        resp_data = json.loads(resp)
        ids = resp_data['data']['songIds']
        return ids

    def get_song_info(self, songids):
        '''
        传入歌曲的id列表 返回这些歌曲的详细信息
        '''
        response = self.opener.open(
            url=constants.songInfoUrl, method='POST', params={'songIds': ','.join(songids)})
        response = json.loads(response.decode('gbk'))
        songlist = response['data']['songList']
        for song in songlist:
            self.__do_download(song)

    def __do_download(self, song):
        song_formats = self.get_song_format(song.get('songId'))
        for k, v in song_formats.items():
            pp = {
                'songIds': v['songId'],
                'rate': v['rate'],
                'format': v['format']
            }
            filename = '%s_%s.%s' % (song.get('songName'), k, v['format'])
            download(constants.downloadUrl, pp, filename)

    def get_song_format(self, songid):
        if songid:
            params = {'songIds': songid}
            print 'get song format...', songid
            resp = self.opener.open(url=constants.songFormatUrl, params=params)
            resp_data = json.loads(resp)
            formats = resp_data['data']['data']
            formats.pop('original')
            return formats
