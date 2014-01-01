#! /usr/bin/env python
# coding:utf-8

class BaseError(Exception):
    def __init__(self, msg):
        super(BaseError, self).__init__()
        self.msg = msg

    def __str__(self):
        print self.msg

class NeedVerificationError(BaseError): pass
class InvalidUserError(BaseError): pass
class PasswordError(BaseError): pass
class LoginError(BaseError): pass
class RequestTokenError(BaseError): pass

class ApiError(BaseError): pass
