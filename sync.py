#!/bin/python
# -*- coding: utf-8 -*-
# @File  : sync.py
# @Author: wangms
# @Date  : 2018/8/19
import sys
import time
import hashlib

class SyncBookmark(object):
    def __init__(self):
        self.browers = {
            '360se': [],
            'chrome': [],
            'firefox': []
        }

    async def listen(self):
        while True:
            for b in self.browers:
                file, md5 = self.browers[b]
                with open(file, 'r') as f:
                    newMd5 = hashlib.md5(f.read())
                if newMd5 != md5:
                    await self.distribute(b)
                    self.browers[b][1] = newMd5
            time.sleep(1)

    async def distribute(self, brower):
        pass



if __name__ == '__main__':
    sync = SyncBookmark()
    sync.listen()
