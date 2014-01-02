#! /usr/bin/env python
# coding:utf-8
import os
import urllib
import urllib2
import cookielib

def undeflate(data):
    import zlib
    return zlib.decompress(data, -zlib.MAX_WBITS)

class Opener(object):
    def open(self, url):
        raise NotImplementedError

    def ungzip(self, fileobj):
        import gzip
        gz = gzip.GzipFile(fileobj=fileobj, mode='rb')
        try:
            return gz.read()
        finally:
            gz.close()

class BuiltinOpener(Opener):
    def __init__(self, cookie_filename=None):
        self.cjar = cookielib.LWPCookieJar()
        self.cookie_filename = cookie_filename
        if os.path.isfile(cookie_filename):
            self.cjar.load(cookie_filename)
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cjar)
        self.opener = urllib2.build_opener(self.cookie_processor, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)

    def open(self, url, method='GET', params={}, headers={}):
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
            resp = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print "Error code: ", e
        else:
            self.cjar.save(self.cookie_filename)
            is_gzip = resp.headers.dict.get('content-encoding') == 'gzip'
            is_deflate = resp.headers.dict.get('content-encoding') == 'deflate'
            if is_gzip:
                return self.ungzip(resp)
            if is_deflate:
                return undeflate(resp)
            return resp.read()
