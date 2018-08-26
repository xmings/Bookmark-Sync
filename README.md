# 强大的跨浏览器跨客户端书签同步工具

## 使用方法
1. 克隆项目到本地
```
git clone git@github.com:wmsgood/Bookmark-Sync.git
```
2. 修改config.py中的配置信息
```python
#同步方式，可选QINIU或GITHUB
SYNC_METHOD = 'QINIU'

#七牛信息,请使用自己的七牛账号
_QiNiu = {
    'AK' : 'UhzOHyNt0MeL-5CUe8RQPGoXjHe33u0fpMOhjKqi', 
    'SK' : 'GzTlY7c30WZw-i9MlmTAyp_XXchyxsI9TIZcD5tR', 
    'BUCKET' : 'bmarksync', 
    'BASE_URL' : 'http://p0bld9c0j.bkt.clouddn.com'    
}

#GitHub信息,请使用自己的GitHub账号
#先在GitHub的Settings-->Developer settings-->Personal access tokens界面生成token值
_GitHub = {
    'TOKEN' : '796365420b6bb72eca9d02a292309a8032f0571e', 
    'USER_NAME': 'bmark-sync',
    'REPO_NAME': 'bmarks',
    'BASE_URL' : 'https://api.github.com'
}

```
3. 运行main.py脚本：
```
python main.py
```

## 同步原理：
1. 首先获取服务端库文件Comment中的md5值信息与本地端库文件的md5比较，不同就下载服务端库文件作为本地端库文件;
2. 本地端库文件中的各浏览器书签文件md5值与本地端对应浏览器人书签文件md5值比较，不同就开启合并操作;
3. 根据本地端库文件内容生成各浏览器书签文件和服务端库文件，上传新的服务端库文件;

## 文件种类：
* 服务端库文件：由某一个客户端上传到服务器的本地端库文件，用于同步。
* 本地端库文件：程序目录下用于合并各浏览器的库文件。
* 浏览器书签文件：各浏览器用于管理书签的文件，可能是sqlite或者Json文件。

## 发展历史

### Version 0.4
1. 摒弃之前的书签同步方式，不需要手工导出HTML书签，程序自动搜索书签文件进行整合
2. 约定以第一次第一个同步的浏览器书签为准，后面的同步的书签都在此基础上合并
3. 增加云同步功能，目前支持GitHub和七牛云同步
4. 添加对Firefox书签支持，目前支持Chrome、360se、Firefox三种浏览器

### Vserion:0.3
1. 增加直接读写浏览器的书签库的方式来整理书签，避免书签导出导入的麻烦
整理书签的三种方式：
    * 导到html书签文件-->整理-->生成html格式书签文件
    * 导到html书签文件-->整理-->生成json格式书签文件
    * 获取其它浏览器书签库里面的信息-->去重-->插入目标浏览器的书签库

### Version:0.2
1. 修改之前的级分割符,由于用'-'分割的level在数据库里面排序有问题,如1-10会排在1-2前面,导致目录错乱.
  现调整为000-000-000-000的格式,不足3位的用0填充(使用zfill填充)
2. 增加了生成json格式的书签(原始是html格式的书签)

### Version:0.1
1. 设计思想：把所有浏览器导出HTML书签入库,对库里面的书签去重整合,生成firefox和360的html格式书签
2. 目前只做了360书签与firefox书签以及chrome的整合
