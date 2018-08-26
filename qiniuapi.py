# -*- coding: utf-8 -*-
import os, time, uuid, requests
from config import QiNiu, UserInfo
from qiniu import Auth, put_file, BucketManager

class Sync(object):
	def __init__(self):
		self.auth = Auth(QiNiu.AK, QiNiu.SK)
		self.buckName = QiNiu.BUCKET
		self.baseUrl = QiNiu.BASE_URL
		self.dbFile = UserInfo.DB_FILE
		self.userKey = UserInfo.USER_KEY

	@property
	def getServLastMd5(self):
		lastUpload = {}
		bucket = BucketManager(self.auth)
		ret, obj, info = bucket.list(bucket=self.buckName, prefix=self.userKey+'/')
		for info in ret['items']:
			if lastUpload:
				if lastUpload['putTime'] < info['putTime']:
					lastUpload = info
			else:
				lastUpload = info
				
		return lastUpload['key'].split('/')[1] if lastUpload else None

	def putFile(self, content, md5str):
		tmpdb = os.path.abspath('temp.db') 
		with open(tmpdb, 'wb') as f:
			f.write(content)
		fileKey = self.userKey + "/" + md5str
		token = self.auth.upload_token(self.buckName, fileKey, 3600)
		ret, info = put_file(token, fileKey, tmpdb)
		if os.path.exists(tmpdb):
			os.remove(tmpdb)
		return ret


	def getFile(self, md5str):
		fileKey = self.userKey + "/" + md5str
		base_url = '%s/%s' % (self.baseUrl, fileKey)
		private_url = self.auth.private_download_url(base_url)
		resp = requests.get(private_url)
		if not resp.ok:
			return ''
		return resp.content
	
if __name__ == '__main__':
	sb = Sync()

