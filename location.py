# -*- coding: utf-8 -*-
import os, time
from regtool import Reg

'''
360和Chrome使用的是json书签文件，Firefox用的是sqlite书签库
'''
BookmarkFile = {
    '360se': {
        'localJsonFile': '{INSTALL_HOME}\\..\\User Data\\Default\\Bookmarks',
        'localDBFile': '',
        'servJsonFile': '{INSTALL_HOME}\\..\\User Data\\Default\\{USERID32}\\Bookmarks',
        'servDBFile': '{INSTALL_HOME}\\..\\User Data\\Default\\{USERID32}\\360sefav.dat'
        },
    'Chrome': {
        'localJsonFile': '{LOCALAPPDATA}\\Google\\Chrome\\User Data\\Default\\Bookmarks',
        'localDBFile': '',
        'servJsonFile': '',
        'servDBFile': '',        
    },
    'Firefox': {
        'localJsonFile': '',
        'localDBFile': '{APPDATA}\Mozilla\Firefox\Profiles\{DEFAULT}\places.sqlite',
        'servJsonFile': '',
        'servDBFile': '{APPDATA}\Mozilla\Firefox\Profiles\{DEFAULT}\places.sqlite',         
    },
}
usableBookmarkFile = {}

def getBookmarkFile(brower):
    r = Reg()
    browers = r.getBrowers()

    for bm in BookmarkFile[brower]:
        bmFile = BookmarkFile[brower][bm]
        bmType = 'db' if bm.find('DBFile') >= 0 else 'json'
        
        if bmFile == '':
            continue
        
        if bmFile.find('{INSTALL_HOME}') >= 0:
            installHone = browers[brower]
            bmFile = bmFile.replace('{INSTALL_HOME}', installHone)
            
        bmFile = bmFile.replace('{LOCALAPPDATA}', os.getenv('LOCALAPPDATA')).replace('{APPDATA}', os.getenv('APPDATA'))
        
        if bmFile.find('{USERID32}') >= 0:
            userHome = []
            curDir = bmFile.split('{USERID32}')[0]
            for f in os.listdir(curDir):
                fpath = os.path.join(curDir, f)
                if os.path.isdir(fpath) and len(f) == 32:
                    mtime = os.path.getmtime(fpath)
                    if not userHome:
                        userHome = [f, mtime]
                    else:
                        if mtime > userHome[1]:
                            userHome = [f, mtime]
            bmFile = bmFile.replace('{USERID32}', userHome[0])
        
        if bmFile.find('{DEFAULT}') >= 0:
            userHome = []
            curDir = bmFile.split('{DEFAULT}')[0]
            for f in os.listdir(curDir):
                fpath = os.path.join(curDir, f)
                if os.path.isdir(os.path.join(curDir, f)) and f.endswith('.default'):
                    mtime = os.path.getmtime(fpath)
                    if not userHome:
                        userHome = [f, mtime]
                    else:
                        if mtime > userHome[1]:
                            userHome = [f, mtime]                    
            bmFile = bmFile.replace('{DEFAULT}', f)                
                    
        if not os.path.exists(bmFile):
            continue
        modifyTime = os.path.getmtime(bmFile)
        modifyTime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modifyTime))
        if usableBookmarkFile.get(brower):
            if modifyTime > usableBookmarkFile[brower][0]:
                usableBookmarkFile[brower] = [modifyTime, bmFile, bmType]
        else:
            usableBookmarkFile[brower] = [modifyTime, bmFile, bmType]
        
    return usableBookmarkFile        

    
if __name__ == '__main__':
    bookmarkFile = getBookmarkFile('Firefox')
    print(bookmarkFile)






