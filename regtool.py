# -*- coding: utf-8 -*-
import winreg


class Reg(object):
	def __init__(self):
		self.software = (
		(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'),
		(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'),
		(winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'))

	def search(self, hkey, path, name):
		values = []
		key = winreg.OpenKey(hkey, path)
		subKeyCnt, attrCnt, unixTime = winreg.QueryInfoKey(key)
		for i in range(subKeyCnt):
			try:
				info = winreg.EnumKey(key, i)
				if info.find(name) >= 0:
					values.append(winreg.OpenKey(key, info))
			except OSError:
				continue

		return values

	def getBrowers(self):
		self.browers = {
			'360se': '',
			'Chrome': '',
			'Firefox': '',
		}
		for hkey, path in self.software:
			for brower in self.browers:
				handles = self.search(hkey, path, brower)
				if handles:
					value = winreg.QueryValueEx(handles[0], 'InstallLocation')
					self.browers[brower] = value[0]

		return {i:self.browers[i] for i in self.browers if self.browers[i] != ''}


if __name__ == '__main__':
	rf =Reg()
	print(rf.getBrowers())