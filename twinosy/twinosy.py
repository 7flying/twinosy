# -*- coding: utf-8 -*-
from sys import argv
from twitter import Twitter

if __name__ == '__main__':
    twitter = Twitter()
    twitter._login()
    twitter._sign_out()
