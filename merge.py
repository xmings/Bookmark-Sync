import json
from model import Bookmark, MergeRec
from dbutils import BMDao, _360BMDao, FirefoxBMDao
from utils import fileMD5

class ChromeJsonParser(object):
	def __init__(self):
		self.bmDao = BMDao()
		
	def parser(self, bookmarkBlock, parent = None):
		pos = 1
		for block in bookmarkBlock:
			bid = block.get('id')
			pid = parent.bid if parent else 0
			plevel = parent.plevel + '-' + str(parent.bid).zfill(6) if parent and parent.plevel else '0'.zfill(6)
			btype = block.get('type')
			title = block.get('name')
			url = block.get('url') if btype == 'url' else ''
			createTime = block.get('date_added', '')			
			if btype == 'url':
				try:
					lastVisitTime = block.get('meta_info').get('last_visited_desktop', '')
				except:
					lastVisitTime = ''
				updateTime = ''
			else:
				lastVisitTime = ''
				updateTime = block.get('date_modified', '')

			children = '' if btype == 'url' else block.get('children')

			bookmark = Bookmark(bid=bid, pid=pid, plevel=plevel, pos=pos, btype=btype, \
			                    title=title, url=url, createTime=createTime, \
			                    updateTime=updateTime, lastVisitTime=lastVisitTime)
			
			self.bmDao.insert(bookmark)
			if btype == 'folder':
				self.parser(children, bookmark)

			pos += 1
	
	def run(self, brower, jsonFile):
		self.bmDao.trunMidTable()
		with open(jsonFile, 'r', encoding='utf8') as f:
			content = f.read()
		self.bookmarks = json.loads(content, encoding='utf8')
		self.bookmarkBlock = self.bookmarks['roots']['bookmark_bar']['children']
		
		self.parser(self.bookmarkBlock)

		md5Str = fileMD5.genFileMD5(jsonFile)
		self.mrObj = MergeRec(brower=brower, filePath=jsonFile, md5Str=md5Str)
		self.bmDao.setMergeRec(self.mrObj)


class _360JsonParser(ChromeJsonParser):
	def parser(self, bookmarkBlock, parent=None):
		pos = 1
		for block in bookmarkBlock:
			bid = block.get('id')
			pid = parent.bid if parent else 0
			plevel = parent.plevel + '-' + str(parent.bid).zfill(6) if parent and parent.plevel else '0'.zfill(6)
			btype = block.get('type')
			title = block.get('name')
			url = block.get('url') if btype == 'url' else ''
			enjoy = block.get('is_best', 0) if btype == 'url' else 0
			lastVisitTime = ''
			createTime = block.get('date_added', '')
			updateTime = block.get('date_modified', '') if btype == 'folder' else ''
	
			children = '' if btype == 'url' else block.get('children')
	
			bookmark = Bookmark(bid=bid, pid=pid, plevel=plevel, pos=pos, btype=btype, \
		                    title=title, url=url, createTime=createTime, \
		                    updateTime=updateTime, lastVisitTime=lastVisitTime)
				
			self.bmDao.insert(bookmark)
			if btype == 'folder':
				self.parser(children, bookmark)
	
			pos += 1		
		
class DBParser(object):
	def __init__(self):
		self.bmDao = BMDao()

	def run(self, brower, dbFile):
		if brower == '360se':
			self.srcBMDao = _360BMDao(dbFile)
		elif brower == 'Firefox':
			self.srcBMDao = FirefoxBMDao(dbFile)
		else:
			raise Exception("不支持该浏览器DB解析：%s" % (brower))
		self.bmDao.trunMidTable()
		result = self.srcBMDao.getCurrent()
		for row in result:
			self.bmDao.insert(row)		

class ChromeJsonGenerator(object):
	def __init__(self):
		self.bmDao = BMDao()
			
	def run(self, brower, jsonFile):
		self.bmDict = []
		result = self.bmDao.getCurrent()
		for bm in result:
			block = {}
			block['id'] = bm.bid
			block['name'] = bm.name
			block['type'] = bm.btype
			block['date_added'] = bm.createTime
			if bm.btype == 'url':
				block['meta_info'] = {}
				block['meta_info']['last_visited_desktop'] = bm.lastVisitTime
				block['url'] = bm.url
			else:
				block['children'] = []
				block['date_modified'] = bm.updateTime
			
			if bm.pid > 0:
				parentBlock = self.getParentBlock(bm.plevel, self.bmDict)
				
				parentBlock['children'].append(block)
			else:
				self.bmDict.append(block)
				
		#pprint.pprint(self.bmDict)
		
		with open(jsonFile, 'r', encoding='utf8') as f:
			content = f.read()
		self.bookmarks = json.loads(content, encoding='utf8')
		self.bookmarks['roots']['bookmark_bar']['children'] = self.bmDict
		with open(jsonFile, 'w', encoding='utf-8') as f:
			f.write(json.dumps(self.bookmarks, ensure_ascii=False, indent=2))
			
	def getParentBlock(self, plevel, currBlock):
		i = 0
		for block in currBlock:
			level = plevel.split('-')
			if level[0] and block['id'] == int(level[0]):
				if len(level) == 1:
					return currBlock[i]
				subBlock = self.getParentBlock('-'.join(level[1:]), currBlock[i]['children'])
				if subBlock:
					return subBlock
			i += 1


class _360JsonGenerator(ChromeJsonGenerator):
	def run(self, brower, jsonFile):
		self.bmDict = []
		result = self.bmDao.getCurrent()
		for bm in result:
			block = {}
			block['id'] = bm.bid
			block['name'] = bm.name
			block['type'] = bm.btype
			block['date_added'] = bm.createTime
			if bm.btype == 'url':
				block['url'] = bm.url
				block['is_best'] = bm.enjoy
				block['data_ico'] = '0'
			else:
				block['children'] = []
				block['date_modified'] = bm.updateTime
	
			if bm.pid > 0:
				parentBlock = self.getParentBlock(bm.plevel, self.bmDict)
	
				parentBlock['children'].append(block)
			else:
				self.bmDict.append(block)
	
		#pprint.pprint(self.bmDict)
	
		with open(jsonFile, 'r', encoding='utf8') as f:
			content = f.read()
		self.bookmarks = json.loads(content, encoding='utf8')
		self.bookmarks['roots']['bookmark_bar']['children'] = self.bmDict
		with open(jsonFile, 'w', encoding='utf-8') as f:
			f.write(json.dumps(self.bookmarks, ensure_ascii=False, indent=2))
		
class DBGenerator(object):
	def __init__(self):
		self.bmDao = BMDao()
		
	def run(self, brower, dbFile):
		if brower == '360':
			self.tarBMDao = _360BMDao(dbFile)
		elif brower == 'Firefox':
			self.tarBMDao = FirefoxBMDao(dbFile)
		else:
			return		
			
		self.tarBMDao.truncBookmark()
			
		for bm in self.bmDao.getCurrent():
			self.tarBMDao.insert(bm)


class MergeBookmark(object):
	def __init__(self):
		self.bmDao = BMDao()
		
	
	def mergeFile2DB(self, brower, bmFile, bmType):
		if bmType == 'json':
			if brower == '360se':
				bjParser = _360JsonParser()
			else:
				bjParser = ChromeJsonParser()
			bjParser.run(brower, bmFile)
		elif bmType == 'db':
			dbParser = DBParser()
			dbParser.run(brower, bmFile)
		
		self.bmDao.bulkMerge()
		
			
	def mergeDB2File(self, brower, bmFile, bmType):
		if bmType == 'json':
			if brower == '360se':
				gener = _360JsonGenerator()
			elif brower == 'Firefox':
				raise Exception('Firefox不存在json书签文件')
			else:
				gener = ChromeJsonGenerator()
		else:
			gener = DBGenerator()
		
		gener.run(brower, bmFile)
		
				
			
if __name__ == '__main__':
	bj = DBGenerator()
	bj.run('Firefox', 'F:\\Users\Administrator\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\0lj68xdb.default\\places.sqlite')
	
	
	
	