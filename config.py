# -*- coding: utf-8 -*-
import os, socket
from utils import ClassDict

#同步方式，可选QINIU或GITHUB
SYNC_METHOD = 'GITHUB'

#七牛信息,请使用自己的七牛账号
_QiNiu = {
    'AK' : '',
    'SK' : '',
    'BUCKET' : 'bmarksync',
    'BASE_URL' : 'http://xxxxxx.bkt.clouddn.com'
}
QiNiu = ClassDict(_QiNiu)

#GitHub信息,请使用自己的GitHub账号
#需要先在GitHub的Settings-->Developer settings-->Personal access tokens界面生成token值
_GitHub = {
    'TOKEN' : '',
    'USER_NAME': '',
    'REPO_NAME': '',
    'BASE_URL' : 'https://api.github.com'
}
GitHub = ClassDict(_GitHub)


#书签同步用户信息
_UserInfo = {
    'USER_KEY' : socket.gethostname(),
    'DB_FILE': os.path.abspath('bookmark.db'),  # 请勿修改
    'Brower': ['Firefox', 'Chrome', '360se'],  #目前支持'Firefox', 'Chrome', '360'
    'OVERWRITE_SERVER': False,
}

UserInfo = ClassDict(_UserInfo)