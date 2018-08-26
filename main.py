# -*- coding: utf-8 -*-
import os
from dbutils import BMDao
from config import UserInfo, SYNC_METHOD
from location import getBookmarkFile
from regtool import Reg
from merge import MergeBookmark 
from utils import genEncryptContent, genDecryptContent, fileMD5, getLogger


if SYNC_METHOD == 'QINIU':
    from qiniuapi import Sync
else:
    from githubapi import Sync
    
logger = getLogger(__file__)

    
class Main(object):
    def __init__(self):
        self.bmDao = BMDao()
        self.sync = Sync()
        self.localDBFile = UserInfo.DB_FILE
        self.mergeBookmark = MergeBookmark()
    
        
    def getServFile(self, md5str):
        content = self.sync.getFile(md5str)
        if content:
            content = genDecryptContent(content)
            with open(self.localDBFile, 'wb') as f:
                f.write(content)
            return True
        
    
    def putLocalFile(self):            
        with open(self.localDBFile, 'rb') as f:
            content = f.read()
        message = fileMD5.genStrMD5(content)
        content = genEncryptContent(content)

        self.sync.putFile(content, message)
        
        return message
        
       
    def run(self):
        localMd5 = fileMD5.getMD5()
        logger.info("开始获取远程服务器DB文件md5值")
        servMd5 = self.sync.getServLastMd5
        
        if not os.path.exists(self.localDBFile) and not servMd5:
            raise Exception("The bookmark.db file does not exist")
        
        if localMd5 != servMd5 and not UserInfo.OVERWRITE_SERVER:
            #如果本地和服务端的MD5不一致并且未开启覆盖写SERVER，就下载服务端库覆盖本地库
            logger.info("本地md5值与远程服务器不匹配，开始下载远程服务器库文件")
            self.getServFile(servMd5)
            fileMD5.setMD5(servMd5)
        
        browers = Reg().getBrowers()
        logger.info("检测到本地浏览器：%s" % (str(list(browers))))
        
        
        #合并各浏览器的书签
        hasMerge = False
        for brower in browers:
            logger.info("开始检查 %s 浏览器是否需要合并" % (brower))
            if brower not in UserInfo.Brower:
                continue
            bmDBMd5 = self.bmDao.getLastMergeRec(brower)
            modifyTime, bmFile, bmType= getBookmarkFile(brower)[brower]
            if fileMD5.genFileMD5(bmFile) != bmDBMd5:
                logger.info("检查到 %s 浏览器书签内容发生变化,开始合并" % (brower))
                self.mergeBookmark.mergeFile2DB(brower, bmFile, bmType)
                hasMerge = True
        
        #生成对应浏览器书签文件
        for brower in browers:
            if brower not in UserInfo.Brower:
                continue
            logger.info("开始生成 %s 浏览器书签" % (brower))
            modifyTime, bmFile, bmType= getBookmarkFile(brower)[brower]
            self.mergeBookmark.mergeDB2File(brower, bmFile, bmType)
        
        #上传库文件并保留MD5值，以便后面同步
        if hasMerge:
            logger.info("开始上传书签库文件")
            localMd5 = self.putLocalFile()
        else:
            localMd5 = servMd5
            
        fileMD5.setMD5(localMd5)
            
        logger.info("成功完成书签文件同步")
        
        
                
if __name__ == '__main__':
    m = Main()
    m.run()
    
                