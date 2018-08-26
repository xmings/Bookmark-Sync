# -*- coding: utf-8 -*-
import requests, json, os
from config import GitHub, UserInfo

class Sync(object):
	def __init__(self,):
		self.servSha = None
		self.servFileMd5 = None
		self.sess = requests.Session()
		self.gitToken = GitHub.TOKEN
		self.dbFile = UserInfo.DB_FILE
		self.userKey = UserInfo.USER_KEY
		self.baseURL = '%s/repos/%s/%s/' % (GitHub.BASE_URL, GitHub.USER_NAME, GitHub.REPO_NAME)

	def _getLastCommit(self):
		resp = self.sess.get(self.baseURL + 'commits')
		batchSha = ''
		for c in resp.json():
			message = c['commit']['message']
			if message.startswith(self.userKey + ':'):
				user , md5 = message.split(':')
				batchSha = c['sha']
				break

		if batchSha:
			self.servFileMd5 = md5
			resp = self.sess.get(self.baseURL + 'commits/' + batchSha).json()
			for c in resp['files']:
				if c['filename'] == 'bookmark.db':
					self.servSha = c['sha']
					break

		return [self.servSha, self.servFileMd5]


	@property
	def getServLastMd5(self):
		if self.servFileMd5:
			return self.servFileMd5
		return self._getLastCommit()[1] 

	def putFile(self, content, md5str):
		sha, md5 = self._getLastCommit()
		path = os.path.basename(self.dbFile)
		message = self.userKey + ":" + md5str
		url = self.baseURL + 'contents/%s?access_token=%s' % (path, self.gitToken)
		data = {"message": message, "content": content.decode('utf-8')}  #json不支持二进制数据，所以必须转为str
		if sha:
			data['sha'] = sha
		resp = self.sess.put(url=url, data=json.dumps(data))
		return resp.ok

	def getFile(self, md5str):
		path = os.path.basename(self.dbFile)
		url = self.baseURL + 'contents/' + path
		resp = self.sess.get(url)
		if not resp.ok:
			return ''
		resp = json.loads(resp.content.decode('utf-8'))
		content = bytes(resp['content'], 'utf-8')
		return content

if __name__ == '__main__':
	sync = Sync()
	a, b = sync.putFile()
	print(a, b)
