#! /usr/bin/env python
# coding:utf-8
import os
import re
import copy
import time
import json
from box import constants
from box import errors
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

    def fetch(self):
        response = self.api.get_playlist()
        if response:
            for plist in response:
                print 'get playlist detail for playList >> ', plist['listTitle']
                songids = self.api.get_list_detail(plist.get('listId'))
                songlist = self.api.get_song_info(songids)
                for song in songlist:
                    self.__do_download(song)

    def __do_download(self, song):
        song_formats = self.api.get_song_format(song.get('songId'))
        for v in song_formats.values():
            if v:
                params = {
                    'songIds': v['songId'],
                    'rate': v['rate'],
                    'format': v['format']
                }
                filename = '%s_%s.%s' % (song.get('songName'), v['rate'], v['format'])
                download(constants.downloadUrl, params, os.path.join(self.download_dir, filename))
