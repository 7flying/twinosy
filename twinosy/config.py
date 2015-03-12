# -*- coding: utf-8 -*-
from sys import stdout

DEBUG_MODE = True
LEVEL = 'DEBUG'

def print_(what):
    if DEBUG_MODE:
        print ' [ %s ] %s' % (LEVEL, str(what))


def print_same_line(what, first=False):
    if DEBUG_MODE:
        if first:
            stdout.write(' [ ' + LEVEL + ' ] ' + str(what))
        else:
            stdout.write(str(what))
            stdout.flush()

def print_end():
    if DEBUG_MODE:
        stdout.write("\n")
        stdout.flush()
