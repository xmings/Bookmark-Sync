#!/bin/python
# -*- coding: utf-8 -*-
# @File  : control.py
# @Author: wangms
# @Date  : 2018/8/19
import json, copy, os, sqlite3, hashlib
from config import _360seBookmarkFile, FirefoxBookmarkFile, ChromeBookmarkFile

try:
    _360seBookmarkFile = _360seBookmarkFile.replace('%APPDATA%', os.environ['APPDATA'])
    FirefoxBookmarkFile = FirefoxBookmarkFile.replace('%APPDATA%', os.environ['APPDATA'])
    ChromeBookmarkFile = ChromeBookmarkFile.replace('%APPDATA%', os.environ['APPDATA'])
except Exception as e:
    pass

class CommonFormat(object):
    def __init__(self):
        self.bms = []
        self.bmJson = []
        self.lastPath = []

    def add(self, id, pid, name, type="url", url=None):
        self.bms.append(
            [id, pid, type, name, url]
        )

    def toJson(self):
        for b in self.bms:
            jBlock = dict(zip(["id", "pid", "type", "name", "url"], b))

            if jBlock["type"] == "folder":
                jBlock["children"] = []
                jBlock.pop("url")

            self.enrich(block=jBlock)

            if jBlock["pid"]:
                self.fillBlock(jBlock, self.bmJson)
            else:
                jBlock.pop("pid")
                self.bmJson.append(jBlock)

        return self.bmJson

    def fillBlock(self, jBlock, bmJson):
        for index, bj in enumerate(bmJson):
            if bj["id"] == jBlock["pid"]:
                jBlock.pop("pid")
                bj["children"].append(jBlock)
                return
            elif bj["type"] == "folder":
                self.fillBlock(jBlock, bj["children"])

    def enrich(self, block):
        pass


class BaseBookmark(object):
    def __init__(self):
        self.bmFile = _360seBookmarkFile
        self.bmJson = {}
        self.bmJsonPath = ['roots', 'bookmark_bar', 'children']
        self.content = ''
        self.commFormat = CommonFormat()
        self.commFormat.enrich = ''

    def read(self):
        with open(self.bmFile, 'r', encoding='utf-8') as f:
            j = json.load(f)
            self.bmJson = copy.deepcopy(j)
        for p in self.bmJsonPath:
            j = j[p]
        return j

    def toList(self, bmJson, pid=""):
        for j in bmJson:
            url = j["url"] if j["type"] == "url" else None
            self.commFormat.add(j["id"], pid, j["name"], j["type"], url)
            if j["type"] == "folder":
                self.toList(j["children"], j["id"])

    def write(self, bmJson):
        j = self.bmJson
        for p in self.bmJsonPath[:-1]:
            j = j[p]

        j["children"] = bmJson

        with open(self.bmFile, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.bmJson, ensure_ascii=False))




class _360seBookmark(BaseBookmark):
    def __init__(self):
        super(_360seBookmark, self).__init__()
        self.bmFile = _360seBookmarkFile
        self.bmJsonPath = ['roots', 'bookmark_bar', 'children']
        self.commFormat.enrich = self.enrichBlock

    def enrichBlock(self, block):
        if block["type"] == "url":
            block["data_ico"] = 0
            block["date_added"] = ""
            block["is_best"] = 0
        else:
            block["date_added"] = ""
            block["date_modified"] = ""
            block["is_best"] = 0


class FirefoxBookmark(BaseBookmark):
    def __init__(self):
        super(FirefoxBookmark, self).__init__()
        self.bmFile = FirefoxBookmarkFile

    def read(self):
        return


    def write(self, bmList):
        mapping = {}
        with sqlite3.connect(self.bmFile) as conn:
            cursor = conn.cursor()
            cursor.execute("""delete from moz_bookmarks where id>33""")
            cursor.execute("""delete from moz_places""")
            for id, pid, type, name, url in bmList:
                if type == "url":
                    cursor.execute("""
                        insert into moz_places (url, title, guid) values (?, ?, ?)
                        """, (url, name, id)
                    )
                    cursor.execute("""select last_insert_rowid()""")
                    newId = cursor.fetchone()[0]
                    mapping[id] = newId

                cursor.execute("""
                    insert into moz_bookmarks (type, fk, parent, title, guid) values (?, ?, ?, ?, ?)
                    """, (1 if type == "url" else 2,
                          mapping.get(id),
                          mapping.get(pid, 3),
                          name, mapping.get(id))
                )
                if type == "folder":
                    cursor.execute("""select last_insert_rowid()""")
                    newId = cursor.fetchone()[0]
                    mapping[id] = newId


class ChromeBookmark(BaseBookmark):
    def __init__(self):
        super(ChromeBookmark, self).__init__()
        self.bmFile = ChromeBookmarkFile
        self.bmJsonPath = ['roots', 'bookmark_bar', 'children']
        self.commFormat.enrich = self.enrichBlock

    def enrichBlock(self, block):
        if block["type"] == "url":
            block["date_added"] = ""
        else:
            block["date_added"] = ""
            block["date_modified"] = ""


if __name__ == '__main__':
    chbm = ChromeBookmark()
    chbm.read()
    bm = _360seBookmark()
    bmJson = bm.read()
    chbm.toList(bmJson)
    bmJson = chbm.commFormat.toJson()

    fbm = FirefoxBookmark()
    fbm.write(chbm.commFormat.bms)
