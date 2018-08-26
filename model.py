from utils import getClientId

class Bookmark(object):
	def __init__(self, **kwargs):		
		attrs = {'bid': 'bid', 'pid': 'pid', 'plevel': 'plevel', 'pos': 'pos', \
		         'btype': 'btype', 'title': 'name', 'url': 'url', 'enjoy': 'enjoy', \
		         'create_time': 'createTime', 'update_time': 'updateTime', 'last_visit_time': 'lastVisitTime',}
		
		for k in kwargs:
			v = kwargs[k]
			attr = attrs.pop(k, k)
			self.__dict__[attr] = v		
		
		for k in attrs:
			if self.__dict__.get(attrs[k]):
				continue
			self.__dict__[attrs[k]] = 0 if k in ('enjoy', 'pos') else ''
		
	def __str__(self):
		return str(self.bid) + " " + self.title + " " \
		       + str(self.pid) + " " + str(self.pos) + " " + self.createTime
	
	
class MergeRec(object):
	def __init__(self, clientId='', brower='', filePath='', md5Str='', createTime=''):
		self.clientId = getClientId() if not clientId else clientId
		self.brower = brower
		self.filePath = filePath
		self.md5Str = md5Str
		self.createTime = createTime
	
	def __str__(self):
		return self.brower + " " + self.filePath + " " + self.md5Str + " " + self.createTime
	
	

if __name__ == '__main__':
	test = Bookmark(abc=1, bcd=2, cde=3, mnx=4)
	print(test.__dict__)
		