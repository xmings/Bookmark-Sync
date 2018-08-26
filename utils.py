# -*- coding: utf-8 -*-
import hashlib, base64, os, re, logging
from cryptography.fernet import Fernet

fernet = Fernet(b'zDmfPrJnNuKBWmYFe9AjHmM2sHtODHpKV5xVP3EdXpA=')

def genEncryptContent(content):
    content = fernet.encrypt(content)
    #base64.b64encode('test'.encode('utf-8')).decode('utf-8') #字符串
    content = base64.encodebytes(content)
    return content

def genDecryptContent(content):
    content = base64.decodebytes(content)
    content = fernet.decrypt(content)
    
    return content


def getClientId():
    info = os.popen('wmic cpu get ProcessorId')
    info = re.split('[\s\n]+', info.read())
    return info[1]


def getLogger(fileName):
    logger = logging.getLogger(fileName)
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        
        f = logging.Formatter("%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s")
        console.setFormatter(f)
        
        logger.addHandler(console)
    return logger


class FileMD5(object):
    def __init__(self):
        self.syncFile = 'sync.log'

    def getMD5(self):
        with open(self.syncFile, 'r', encoding='utf-8') as f:
            localMd5 = f.read()
        return localMd5

    def setMD5(self, md5):
        with open(self.syncFile, 'w', encoding='utf-8') as f:
            f.write(md5)

    def genFileMD5(self, file):
        if not os.path.exists(file):
            return
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file, 'rb') as f:
                content = f.read()

        return self.genStrMD5(content)

    def genStrMD5(self, content):
        md5 = hashlib.md5()
        if isinstance(content, str):
            content = content.encode('utf-8')
        md5.update(content)
        return md5.hexdigest()


fileMD5 = FileMD5()


class ClassDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
 
    def __getattr__(self, key):
        return self[key]
 
    def __setattr__(self, key, value):
        self[key] = value
 
    def __delattr__(self, key):
        del self[key]

if __name__ == '__main__':
    a = genEncryptContent(bytes("test", 'utf-8'))
    print(a)
    b = genDecryptContent(a)
    print(b)
