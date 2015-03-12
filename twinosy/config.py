# -*- coding: utf-8 -*-

DEBUG_MODE = True
LEVEL = 'DEBUG'

def print_(what):
    if DEBUG_MODE:
        print ' [ %s ] %s' % (LEVEL, str(what))
