import sqlite3, os, datetime, re, uuid
from model import Bookmark, MergeRec
from location import getBookmarkFile
from config import UserInfo


BookmarkDB = UserInfo.DB_FILE


def dict_factory(cursor, row): 
	d = {} 
	for idx, col in enumerate(cursor.description): 
		d[col[0]] = row[idx] 
	return d

class BMDao(object):
	def __init__(self, dbFile=BookmarkDB):
		self.dbFile = dbFile
	
	def insert(self, bmObj):
		createTime = self.parseTimestamp(bmObj.createTime) \
		    if re.fullmatch('\d+', str(bmObj.createTime)) else bmObj.createTime
		updateTime = self.parseTimestamp(bmObj.updateTime) \
		    if re.fullmatch('\d+', str(bmObj.updateTime)) else bmObj.updateTime
		lastVisitTime = self.parseTimestamp(bmObj.lastVisitTime) \
		    if re.fullmatch('\d+', str(bmObj.lastVisitTime)) else bmObj.lastVisitTime
		
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "insert into bookmarks_current "\
					+ "(bid,pid,plevel,pos,btype,title,url,enjoy,create_time,update_time,last_visit_time) "\
					+ "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"			
			conn.execute(sqlStr % (bmObj.bid, bmObj.pid, bmObj.plevel, bmObj.pos, bmObj.btype,
			                       self.format(bmObj.name),bmObj.url, bmObj.enjoy, createTime, updateTime, lastVisitTime))
			conn.commit()
	
	def bulkMerge(self):
		with sqlite3.connect(self.dbFile) as conn:
			#清空ID映射表
			conn.execute("delete from bid_mapping")
			conn.commit()
			#先更新目录，目录按由上向下的层级关系更新，再更新链接
			#如果插入的是目录：
			#  如果存在相同目录名就更新其它信息为最新信息(包括PID)，并向映射表插入ID的映射关系;
			#  如果不存在相同目录名就直接插入，但ID需要使用当前最大ID，且把PID更新为映射表中获取新ID，并向映射表插入ID的映射关系;
			#如果插入的是链接，删除已存在的链接，并插入新的链接，但ID需要使用当前最大ID，且把PID更新为映射表中获取新ID；
			
			#已经把BID列设为自动增长列
			sqlStr = "select bid,pid,pos,enjoy,plevel,create_time,update_time,"\
			    + "last_visit_time,title from bookmarks_current where btype='folder' order by plevel,pos"
			result = conn.execute(sqlStr)
			for row in result:
				#获取最新PID
				result2 = conn.execute("select new_bid,level from bid_mapping where bid='%s'" % (row[1])).fetchone()
				pid = result2[0] if result2	else row[1]
				plevel = result2[1] if result2 else ''
				
				#尝试更新
				sqlStr2 = "update bookmarks_history "\
			        + "set pid='%s', pos='%s', enjoy='%s', plevel='%s',"\
			        + "create_time='%s',update_time='%s',last_visit_time='%s' "\
			        + "where btype='folder' and title='%s'"
				result2 = conn.execute(sqlStr2 % (pid, row[2], row[3], plevel, row[5], row[6], row[7], row[8]))
				conn.commit()
				
				status = False if result2.rowcount == 0 else True
				if not status:
					#如果没有更新，说明不存在相同title的记录，就直接插入，并获取该记录的ID
					sqlStr2 = "insert into bookmarks_history "\
					    + "(pid,btype,pos,enjoy,plevel,create_time,update_time,last_visit_time,title) "\
					    + "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
					result2 = conn.execute(sqlStr2 % (pid, 'folder', row[2], row[3], plevel, row[5], row[6], row[7], row[8]))
					lastrowid = result2.lastrowid
					conn.commit()
				else:
					#如果更新成功，获取该记录的ID
					sqlStr2 = "select bid from bookmarks_history where title='%s' and btype='folder'"
					result2 = conn.execute(sqlStr2 % (row[8]))
					lastrowid = result2.fetchone()[0]
					
					
					
				
				level = plevel + '-' + str(lastrowid).zfill(6) if plevel else str(lastrowid).zfill(6)
				if status:
					#并把该目录下的已存在的url的plevel更新为最新，解决不同浏览器相同目录问题
					sqlStr2 = "update bookmarks_history set plevel='%s' where pid='%s'"
					conn.execute(sqlStr2 % (level, lastrowid))
					conn.commit()					
					#把bid_mapping中之前存在的相同的pid的level更新为最新,解决同一浏览器存在相同的目录问题
					sqlStr2 = "update bid_mapping set level='%s' where new_bid='%s'"
					conn.execute(sqlStr2 % (level, lastrowid))
					conn.commit()
					
		
				conn.execute("insert into bid_mapping (bid,new_bid,level) values('%s', '%s', '%s')" % (row[0], lastrowid, level))
				conn.commit()
				
			
			
			sqlStr = "delete from bookmarks_history "\
			    + "where exists (select 1 from bookmarks_current a where bookmarks_history.url=a.url and a.btype='url')"
			result = conn.execute(sqlStr)
			conn.commit()
			
			sqlStr = "insert into bookmarks_history "\
			    + "(pid,plevel,btype,title,url,pos,enjoy,create_time,update_time,last_visit_time) " \
			    + "select (case when b.new_bid is null then 0 else b.new_bid end) as pid,"\
			    + "(case when b.level is null then '' else b.level end) as plevel,"\
			    + "a.btype,a.title,a.url,a.pos,a.enjoy,a.create_time,a.update_time,a.last_visit_time "\
			    + "from bookmarks_current a left join bid_mapping b on a.pid=b.bid where a.btype='url'"
			result = conn.execute(sqlStr)
			conn.commit()

	
	def getCurrent(self):
		'''返回当前有效记录'''
		with sqlite3.connect(self.dbFile) as conn:
			conn.row_factory = dict_factory
			sqlStr = "select bid,pid,plevel,title,btype,url,pos,enjoy,create_time," \
			    +"update_time,last_visit_time from bookmarks_history order by plevel,pos"
			result = conn.execute(sqlStr).fetchall()
			
			if not result:
				return list()
		return (Bookmark(**r) for r in result)
	
	def getLevel(self, bid):
		level = ''
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "with recursive tree(x) as "\
			    + "(values('%s') union all select pid from tb_fav a,tree where a.bid=tree.x) "\
			    + "select count(1) from tree"
			result = conn.execute(sqlStr % (bid, ))
			for r in result:
				level = str(r) + '-' + level			
		return level
	
	
	def getAll(self):
		with sqlite3.connect(self.dbFile) as conn:
			conn.row_factory = dict_factory
			sqlStr = "select bid,pid,title,btype,url,pos,enjoy,create_time," \
				    +"update_time,last_visit_time from bookmarks_history order by plevel,pos"
			result = conn.execute(sqlStr).fetchall()
			if not result:
				return list()	
		return (Bookmark(**r) for r in result)		
		
			
	
	def setMergeRec(self, mrObj):
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "insert into merge_rec (client_id, brower, file, md5)"\
			    + " values ('%s', '%s', '%s', '%s')" % (mrObj.clientId, mrObj.brower, mrObj.filePath, mrObj.md5Str)
			conn.execute(sqlStr)
	
	def getLastMergeRec(self, brower):
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "select * from merge_rec where brower='%s' order by create_time desc" % (brower)
			result = conn.execute(sqlStr)
			result = result.fetchone()
			if not result:
				return MergeRec()
		return MergeRec(*result)
	
	
	def trunMidTable(self):
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "delete from bookmarks_current"
			result = conn.execute(sqlStr)
			
		
	@staticmethod
	def genTimestamp(dateTime):
		if not dateTime:
			return
		dateTime = datetime.datetime.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
		beginDateTime = datetime.datetime.strptime('160101010800', '%Y%m%d%H%M')
		timedelta = dateTime - beginDateTime
		return int(timedelta.total_seconds() * 1000000)


	@staticmethod
	def parseTimestamp(timeNumber):
		if not timeNumber:
			return 
		timeNumber = int(str(timeNumber).ljust(18, '0')[:-7])
		dateTime = datetime.datetime.strptime('160101010800', '%Y%m%d%H%M')
		dateTime = dateTime + datetime.timedelta(seconds= timeNumber)
		return dateTime.strftime('%Y-%m-%d %H:%M:%S')
	
	@staticmethod
	def format(text):
		text = str(text).replace('\'', '')
		return text
	
	
class _360BMDao(BMDao):
	def __init__(self, dbFile):
		super(_360BMDao, self).__init__(dbFile)
		
	def getCurrent(self):
		if not os.path.exists(self.dbFile):
			raise Exception("360BookmarkDB does not exist")
	
		with sqlite3.connect(self.dbFile) as conn:
			conn.row_factory = dict_factory
			sqlStr = "select id as bid, parent_id as pid, null as plevel, pos, "\
			    + "case when is_folder=0 then 'url' else 'folder' end as btype,"\
			    + "title, url, is_best as enjoy, create_time, "\
			    + "last_modify_time as update_time, null as last_visit_time from tb_fav"
			result = conn.execute(sqlStr)
		
		if not result:
			return list()
		result = [Bookmark(**r) for r in result]
		
		for r in result:
			r.level = self.getLevel(r.bid)
		return result
	
	def getLevel(self, bid):
		level = ''
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "with recursive tree(x) as "\
			    + "(values('%s') union all select parent_id from tb_fav a,tree where a.id=tree.x) "\
			    + "select x from tree"
			result = conn.execute(sqlStr % (bid, ))
			for r in result:
				level = str(r[0]) + '-' + level
		return level	
	
	def truncBookmark(self):
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "delete from tb_fav"
			result = conn.execute(sqlStr)
			
	def insert(self, bmObj):
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "insert into tb_fav (id,parent_id,is_folder,title," \
			    + "url,pos,create_time,last_modify_time,is_best,reserved) "\
			    + "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 0)"
			result = conn.execute(sqlStr % (bmObj.bid,
			                                bmObj.pid,
			                                0 if bmObj.btype=='url' else 1, 
			                                bmObj.title,
			                                bmObj.url,
			                                bmObj.pos,
			                                self.genTimestamp(bmObj.createTime),
			                                self.genTimestamp(bmObj.updateTime),
			                                bmObj.enjoy))
			conn.commit()
			
class FirefoxBMDao(BMDao):
	def __init__(self, dbFile):
		super(FirefoxBMDao, self).__init__(dbFile)
		self.rootId = self.getRootId()
		
	def getRootId(self):
		with sqlite3.connect(self.dbFile) as conn:
			result = conn.execute("select id from moz_bookmarks where title='书签工具栏'")
			rootId = result.fetchone()[0]
		return rootId
	
	def getCurrent(self):
		sqlStr = "with recursive tree(x,y) as "\
		    + "(values({rootid},'') union all select id,printf(y||'-'||printf('%06d',x)) "\
		    + "from moz_bookmarks a,tree where a.parent=tree.x) "\
		    + "select a.id as bid,type as btype, parent as pid,"\
		    + "trim(c.y,'-') as plevel, position as pos, a.title as name, url,"\
		    + "a.dateAdded as createTime,a.lastModified as updateTime, b.last_visit_date as lastVisitTime "\
		    + "from moz_bookmarks a "\
		    + "inner join tree c on c.x=a.id and c.x<>{rootid} "\
		    + "left join moz_places b on ifnull(a.fk,100000)=b.id"
		sqlStr = sqlStr.format(rootid=self.rootId)
		with sqlite3.connect(self.dbFile) as conn:
			conn.row_factory = dict_factory
			result = conn.execute(sqlStr).fetchall()
		
			if not result:
				return list()
			bmObjList = []
			for r in result:
				model = self.modelConvert(Bookmark(**r), 'out')
				bmObjList.append(model)
		return bmObjList
	
	def insert(self, bmObj):
		'''先插入moz_places表，再插入moz_bookmarks表'''
		guid = uuid.uuid1().hex[:12]
		bmObj = self.modelConvert(bmObj, 'in')
		with sqlite3.connect(self.dbFile) as conn:
			if bmObj.btype == 1:
				sqlStr = "insert into moz_places "\
							+ "(id,url,title,visit_count,hidden,typed,last_visit_date,guid) "\
							+ "values (%d, '%s', '%s', 0, 0, 0, '%s', '%s')" 		
				conn.execute(sqlStr % (bmObj.bid, bmObj.url, bmObj.name, bmObj.lastVisitTime, guid))
				conn.commit()				

			sqlStr = "insert into moz_bookmarks "\
			    + "(id,type,fk,parent,position,title,dateAdded,lastModified,guid)"\
			    + "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"
			conn.execute(sqlStr % (bmObj.bid, bmObj.btype, bmObj.fk, bmObj.pid, bmObj.pos, \
			                       bmObj.name, bmObj.createTime, bmObj.lastVisitTime, guid))
			conn.commit()
			
		
	
	def truncBookmark(self):
		with sqlite3.connect(self.dbFile) as conn:
			sqlStr = "with recursive tree(x,y) as "\
			    + "(values(%d,0) union all select id,fk from moz_bookmarks a,tree where a.parent=tree.x)"\
			    + "delete from moz_places where id in (select y from tree)"
			conn.execute(sqlStr % (self.rootId))
			conn.commit()
			sqlStr = "with recursive tree(x) as "\
			    + "(values(%d) union all select id from moz_bookmarks a,tree where a.parent=tree.x) "\
			    + "delete from moz_bookmarks where id in (select x from tree) and id <>%d"
			conn.execute(sqlStr % (self.rootId, self.rootId))
			conn.commit()

	def modelConvert(self, bmObj, direct):
		if direct == 'in':
			bmObj.pid = self.rootId if bmObj.pid == 0 else bmObj.pid
			bmObj.pos -= 1
			if bmObj.btype == 'url':
				bmObj.btype = 1
				bmObj.fk = bmObj.bid
			else:
				bmObj.btype = 2
				bmObj.fk = None
		elif direct == 'out':
			bmObj.pid = 0 if bmObj.pid == self.rootId else bmObj.pid
			bmObj.pos += 1
			bmObj.btype = 'url' if bmObj.btype == 1 else 'folder'
		else:
			raise Exception("Invalid direct value: %s" % (direct))
		
		return bmObj
		

if __name__ == '__main__':
	bmdao = FirefoxBMDao('F:\\Users\Administrator\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\0lj68xdb.default\\places.sqlite')
	bmdao.truncBookmark()
