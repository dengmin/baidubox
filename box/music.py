#! /usr/bin/env python
# coding:utf-8
import os
import copy
from box import constants
from api import BaiduAPI
from box.opener import BuiltinOpener
from box.download import download

COOKIE_FILE = constants.COOKIE_FILE

class BaiduMusicBox(object):

    def __init__(self, username, password):
        super(BaiduMusicBox, self).__init__()
        self.data = copy.deepcopy(constants.PostData)
        self.opener = BuiltinOpener(COOKIE_FILE)
        self.__init_download_dir()
        self.api = BaiduAPI(self.opener, username, password)

    def __init_download_dir(self):
        """初始化下载目录"""
        current_pwd = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.split(current_pwd)[0]
        download_dir = os.path.join(parent_dir, 'downloads')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        self.download_dir = download_dir

    def search(self,keyword):
        response = self.api.search(keyword)
        songs = response.get('song_list')
        for song in songs:
            print song.get('song_id'),song.get('title')

    def collect_list(self):
        print u'我的收藏'
        response = self.api.get_collect_list()
        print u'配额: %s ,共收藏 %s 首' %(response.get('quota'), response.get('total'))
        song_id_list = response.get("songList")
        song_id_list = [str(item.get('id')) for item in song_id_list]
        songList = self.api.get_song_info(song_id_list)
        for song in songList:
            self.__do_download(song)

    def get_listen_history(self):
        print u'我的播放记录'
        response = self.api.get_listen_history()
        song_id_list = response.get('songList')
        song_id_list = map(str, song_id_list)
        songList = self.api.get_song_info(song_id_list)
        for song in songList:
            print song.get('songName')
            self.__do_download(song)

    def fetch(self):
        response = self.api.get_playlist()
        if response:
            for plist in response:
                print u'获取播放列表 >> ', plist['listTitle']
                songids = self.api.get_list_detail(plist.get('listId'))
                songlist = self.api.get_song_info(songids)
                for song in songlist:
                    self.__do_download(song)

    def __do_download(self, song):
        song_formats = self.api.get_song_format(song.get('songId'))
        flac_fmt = [v for v in  song_formats.values() if v and v['format'] == 'flac']
        if flac_fmt:
            item = flac_fmt[0]
        else:
            print '[ %s ] no flac format!' %(song.get('songName')) , 'download mp3 format'
            mp3_fmt = [v for v in song_formats.values() if v and v['format'] == 'mp3']
            #取出比特率最高的
            item = max(mp3_fmt, key=lambda x:x['rate'])
        params = {
            'songIds': item['songId'],
            'rate': item['rate'],
            'format': item['format']
        }
        artistName = song.get('artistName') if song.get('artistName') else 'UnKnown'
        filename = '%s-%s.%s' % (artistName, song.get('songName'), item['format'])
        download(constants.downloadUrl, params, os.path.join(self.download_dir, filename))



