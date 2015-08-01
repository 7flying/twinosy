# -*- coding: utf-8 -*-

from core import Core

def banner():
    print """ _____        _                   
|_   _|      (_)                      
  | |_      ___ _ __   ___  ___ _   _ 
  | \ \ /\ / / | '_ \ / _ \/ __| | | |
  | |\ V  V /| | | | | (_) \__ \ |_| |
  \_/ \_/\_/ |_|_| |_|\___/|___/\__, |
                                 __/ |
     The nosy Twitter analyser  |___/\n"""

def usage():
    banner()

class Shell(object):

    def __init__(self):
        self.core = Core(self)
        self.on = False

    def init(self):
        self.on = True
        banner()
        self.loop()

    def loop(self):
        while self.on:
            read = raw_input('twinosy > ').strip()
            evl = read.split()
            self._eval_input(evl)

    def _eval_input(self, commands):
        print commands
        args = []
        if len(commands) > 1:
            args = commands[1:]
        if commands[0] in self.core.commands:
            self.core.commands[commands[0]]['fn'](*args)

if __name__ == '__main__':
    s = Shell()
    s.init()
