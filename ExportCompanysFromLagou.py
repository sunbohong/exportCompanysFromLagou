#-*- coding:utf-8 -*-
#!/usr/bin/python
#命令行工具
import click
import json
import urllib
import urllib2
from json2xls import Json2Xls

class exportCompanysFromLagou(object):
	"""exportFromLagou API
	:param string kd:职位名
	:param string city:指定的城市名
	:param bool get_detail_location:是否获取详细地址
	"""
	def __init__(self, kd, city='北京',get_detail_location=True):
		self.kd = kd  
		self.city=city  
		print self.city
		self.get_detail_location=get_detail_location
		#保存公司信息
		self.companys=[]
		self.url = "http://www.lagou.com/jobs/positionAjax.json?"+urllib.urlencode({'city':self.city.encode('utf-8')})

	def saveToFile(self):
		self.filesavepath = '%s-%s.xls' % (self.kd,self.city)
		if len(self.companys)>0:
			obj = Json2Xls(self.filesavepath, json.dumps(self.companys))
			obj.make()
			print u"已保存到%s" % self.filesavepath

	def getJsonData(self,url,parameters):
		req = urllib2.Request(url)
		data = urllib.urlencode(parameters)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
		response = opener.open(req, data)

		# 读取数据
		obj = response.read()

		# 转json
		jsonData=json.loads(obj)
		return jsonData

	def getCompanys(self,url,parameters):
		jsonData=self.getJsonData(url,parameters)
		# 判断返回数据是否正确
		code = jsonData["code"]
		if code == 0 :
			self.companys.extend(jsonData["content"]["result"]) 

	def getLocation(self):
		print "正在获取准确的公司地址"
		for company in self.companys:
			url = "http://www.lagou.com/center/job_%s.html?m=1" % company["positionId"]
			req = urllib2.Request(url)
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
			response = opener.open(req)

			# 读取数据
			obj = response.read()

			s0 = obj.find("global.companyAddress = '")
			s1 = obj.find(" global.imgUrl ")
			company['location']=obj[s0+25:s1-6]


	def getTotalPageNo(self):
		parameters = {'first':'false', 'pn':1, 'kd':self.kd}
		jsonData=self.getJsonData(self.url,parameters)
		# 判断返回数据是否正确
		code = jsonData["code"]
		if code == 0 :
			totalPageCount = jsonData["content"]["totalPageCount"]
			return totalPageCount
		return 0
	def  make(self):
		totalPageCount = self.getTotalPageNo()
		print "一共有%s页数据" % totalPageCount
		for i in xrange(1,totalPageCount+1):
			parameters = {'first':'false', 'pn':i, 'kd':self.kd}
			self.getCompanys(self.url,parameters)
			print "已经获取%d页" % i
		if self.get_detail_location:
			self.getLocation()
		self.saveToFile()

@click.command()
@click.argument('kd')
@click.option('--city', '-c', default='北京')
@click.option('--get_detail_location', '-l',default=True)

def make(kd,city,get_detail_location):
	exportCompanysFromLagou(kd,city=city,get_detail_location=get_detail_location).make()
if __name__ == '__main__':
	make()
