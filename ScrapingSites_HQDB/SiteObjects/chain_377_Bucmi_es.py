#coding: utf-8
from __future__ import unicode_literals
import json
import re
import cgi
from bs4 import BeautifulSoup
from lxml import etree as ET
from lxml import html
import requests
import urlparse
import urllib3
from Common import Util,Validation
from BaseSite import BaseSite
from SiteObjects.Objects_HQDB import Venue, Service
import requests.packages.urllib3
from dbfread import __url__
from StringIO import StringIO
from selenium import webdriver
import StringIO
from html5lib.constants import namespaces


requests.packages.urllib3.disable_warnings()

class Bucmi_es(BaseSite):
    __url__ = 'https://www.bucmi.com'
    _chain_ = 'chain_377_'
    __name__ = 'Bucmi '
 
    _url_venue = 'https://www.bucmi.com/'
    _xpath_Venues = "//div[@class='dvRecentLocation']/ul/li/span[@class='LocationAddress']" 
    _xpath_LstVenues = '//ul[@class="bcmPagination""]/li[last()-1]'        
    _url_lstServices = ''
    _xpath_lstServices = '//div[@id="divVenueServiceList"]'
    _xpath_addr = "//div[@class='DireccionWrap']"
    _xpath_lat = '//div[@id="dvMapa"]/input[@id="dnn_ctlVenueContent_ctlVenueMap_hdnLatitude"]'
    _xpath_long = '//div[@id="dvMapa"]/input[@id="dnn_ctlVenueContent_ctlVenueMap_hdnLongitude"]'
    _xpath_img = './/ul[@class="grid"]/li[@class="grid-item"]/a/img'
    services = []
    venues = []
    _lstVenues = []
    venues_csv = []
    services_csv = []
    page = 0  
    outFileVN = ''
    outFileSV = ''
   
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    def doWork(self):
      self.outFileVN = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Venues.csv'
      self.outFileSV = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Services.csv'
      
      print "-----------------------------"
      print self._chain_ + self.__name__
      print "-----------------------------"
      self.__getListVenues()
      self.Write2File()
      if len(self._lstVenues) > 0:
            
            print "Number of venues is : " + str(len(self._lstVenues))
            for i in range(index,len(self._lstVenues)):
                try:
                    ven = self.__VenueParser(self._lstVenues[i])
                   
                except Exception, ex:
                     print "File ",str(index), ":", ex
                     Util.log.error("File " + str(i) + ": " + ex.message)
                     index+=1
                ven.writeToFile(self.folder,index)
                
                    
            if len(self.venues_csv) > 0:
                 self.writelist2File(self.venues_csv,self.outFileVN)
            if len(self.services_csv) > 0:
                 self.writelist2File(self.services_csv,self.outFileSV)

    def Write2File(self):
        if self._lstVenues != None and len(self._lstVenues) > 0:                                    
            print "Number of venues is : " + str(len(self._lstVenues))
            index = 0                          
            for i in range(len(self._lstVenues)):
                try:
                    print ven + "  a"
                    ven = self._lstVenues[i]
                    
                    if ven != None:
                        name = ''
                        if ven.name != None:
                            name += self.__name__ + ' - ' + ven.name                      
                        ven.writeToFile(self.folder,index,name.strip('-'))
                        index+=1
                        self.venues.append(ven.toOrderDict())                                                        
                except Exception,ex:
                   Util.log.error("File " + str(i) + ": " + ex.message)                       
        if len(self.venues) > 0:            
            Util.writelist2File(self.venues,self.outFileVN)    
        if len(self.services) > 0:
            Util.writelist2File(self.services,self.outFileSV)
                                        
            
 
    def __getListVenues(self):
        print "Getting list of Venues"
        print "Number of venues is : " + str(len(self._lstVenues))

        xmlRegions = Util.GetHTMLResponse(self.__url__,self._xpath_Venues)
        idx = 0
        opt = []
        for i in range(idx,len(xmlRegions)):
            opt = xmlRegions[i].text.strip()
            self._getLinkVenue(opt)
         
    
    def _getLinkVenue(self, region,page = 1,totalPage = 1):    
        if page > totalPage: return
        print "Scraping Region: " + region + " at page = " + str(page)
        url = self._url_venue + region +".html" + "?search=" + region 
#       https://www.bucmi.com/Santander.html?search=Santander
        url = url[:url.rfind("?")]
#       https://www.bucmi.com/Santander.html
     

        if page > 1:
            url = url + "?page=" + str(page)
            print url
            
#         https://www.bucmi.com/Madrid.html?page=1
        rq = requests.get(url)
        htmldoc = html.fromstring(rq.content)
        nodes= htmldoc.xpath('//ul[@class="bcmPagination"]/li[last() -1]')
        ttPage = totalPage
        if totalPage == 1:
            tag_a = filter(lambda ele: ele.tag == "a", nodes)
            if len(tag_a) > 0:
                ttPage = int(tag_a[0].text.strip())
        for ele in nodes:
            if ele.tag == "li":

                _sub = ele.getchildren()
                for s in _sub:
                   ttpage = s.text
                   idx = 1 
                   _scrape_page =url + "?page=" 
                   for i in range(idx,int(ttpage)):
                       url =_scrape_page + str(i)
                       self.__VenueParser(url)
            
        page += 1
        
        self._getLinkVenue(region, page, ttPage)
        
    def __VenueParser(self, url):
        vens = Venue()
        xmlVen = Util.getRequestsXML(url, "//section/article")

        print "Scraping page "  + url
        vens.country = 'es'
#   Featured 
        xmlFeatured = xmlVen.xpath('.//div[@class="noved-list recommendedPremium" or @class="noved-list recommended"]')  
        _idx = 0
        for i in range(_idx,len(xmlFeatured)):
            if xmlFeatured != None and len(xmlFeatured) > 0 :
                _featured = "".join(xmlFeatured[i].itertext())
                if _featured == 'RECOMENDADO' :
                        vens.hqdb_featured_ad_type = 'Featured' 


        xpath_detail = '//div[@id="liFoot"]/a'
        _xmldetail = xmlVen.xpath(xpath_detail)
        if len(_xmldetail) > 0:
            
            idx = 0
            for i in range(idx,len(_xmldetail)):
                urlDetail = _xmldetail[i].get('href')
                vens.business_website = urlDetail
                print "Link "+ str(i) + " " + urlDetail 
                vens.scrape_page = urlDetail
                
                vens.services = self.__ServicesParser(urlDetail)

      
                _xpathRate = ".//div/span[@class='RatingCount']"
                _xpathSCore = ".//span[@class='Score']"
                xmlInfo = Util.getRequestsXML(urlDetail,".//div[@class='VenueInfo']")
                xmlLogo =  Util.getRequestsXML(urlDetail, ".//div[@class='VenueLogo']/a[@class='goingToImg']/img")
                for _item in xmlInfo:
                    for score in xmlInfo.xpath(_xpathSCore):
                        vens.hqdb_review_score = score.text
                    for rate in xmlInfo.xpath(_xpathRate):
                        vens.hqdb_nr_reviews = rate.text
                for i in xmlLogo:
                    for img in i.xpath("@src"):
                        vens.venue_images = img
                  
                        
                xmlVenueDetail = Util.getRequestsXML(urlDetail,'//div[@class="contentCenter"]/div')
                xmlBussinessname = Util.getRequestsXML(urlDetail,'//div[@class="OtherVenueData"]')
                for bn in xmlBussinessname.xpath("//h1/text()"):
                     vens.name_of_contact = bn.strip()
                     vens.name = vens.name_of_contact
                      
#               Get city       
                
                xmlCities = Util.getRequestsXML(urlDetail,"//div[@class='OtherVenueData']/a")
                for ct in xmlCities.xpath(".//span"):
                    _ct = ct.text.strip().replace(",","").lstrip()
                    vens.city = _ct
#             
                
                desc = xmlVenueDetail.find(".//div[@class='DescriptionWrap']/p")
                if desc != None and desc.text != None:
                    vens.description=desc.text.strip()
                tel = xmlVenueDetail.find(".//div[@class='DireccionWrap']/a")
                addr = xmlVenueDetail.xpath("//div[@class='DireccionWrap']/node()[3]")
                if tel != None and tel.text != None:
#                     vens.office_number = tel.text.strip()
                    phoneNum = tel.text.strip()
                    telNum = re.search("re(6*|7*)\d+", phoneNum)
                    if telNum:
                        print "----"+ telNum.group()
                        vens.mobile_number = telNum.group()
                    elif phoneNum:
                       vens.office_number = phoneNum
                    
                     
                if addr != None and len(addr) != None:
                    baseAdr= addr[0]
#                     _addr = re.sub('', repl, string)
#                     vens.formatted_address = baseAdr.split(",")[0].strip()
#                     print baseAdr.split(",")[0].strip()
                
                    vens.street = baseAdr.split(",")[0].strip()
                
                    vens.zipcode = baseAdr.split(",")[3].strip()
        
                     
                venueImg = xmlVenueDetail.xpath(self._xpath_img)
                images = []
                for item in venueImg:
                    for img in item.xpath("@src"): 
                        _imgLst = images.append(img)
                
                vens.img_link = images

                xmlLat = xmlVenueDetail.xpath(self._xpath_lat)
                for item in xmlLat:
                    for lat in item.xpath("@value"):
                        vens.latitude = lat.strip()
                xmlLong = xmlVenueDetail.xpath(self._xpath_long)
                for item in xmlLong:
                    for long in item.xpath("@value"):
                        vens.longitude = long.strip()
                 
                    
                if self._lstVenues != None and len(self._lstVenues) > 0:
            
                    self._lstVenues.append(vens)
                    print str(self.page) + ") Scrapping chain 377 page " + vens.scrape_page
                
                vens.writeToFile(self.folder,self.page,vens.name_of_contact)
                self.venues_csv.append(vens)
                self.page+=1    
        return vens
   
    def __ServicesParser(self,url):
        services = []
        sv = Service()
        print 'Getting service page ', url
        xpath_service = "//form[@id='Form']/main"
        _xmlService = Util.getRequestsXML(url,xpath_service)
        
        _service = _xmlService.findall(".//span[@id='lblServiceName']")
        _price = _xmlService.findall(".//span[@class='listPromotionPriceCenter']") + _xmlService.findall(".//span[@id='lblNormalPrice']")
        _dura = _xmlService.findall(".//span[@id='lblTime']")
        _desc = _xmlService.findall(".//p[@id='lblDescriptionService']")
        
        _xpathCate = '//a[re:test(@id,"^Cat_[0-9]")]'  
        _xmlMCate = Util.getRequestsXML(url,"//nav[@class='bcmMenu']")
        
        idx = 0
        for i in range(idx,len(_xmlMCate)):  
                venueCate = []
                for cate in _xmlMCate.xpath(_xpathCate,namespaces={'re': "http://exslt.org/regular-expressions"}):
                        _cate = "".join(cate.itertext()).strip()
                        venueCate.append(_cate)
                        sv.category = venueCate
                              
        for i in range (idx, len(_service)):
                sv.service = "".join(_service[i].itertext()).strip()
                sv.scrape_page = url
                sv.price = "".join(_price[i].itertext()).strip()
                sv.description ="".join(_desc[i].itertext()).strip()
                duration = "".join(_dura[i].itertext()).strip()
                duration = re.search(r'\d+', duration).group()
                intDur= int(duration) * 60
                sv.duration = intDur

                services.append(sv)
        
         
        print 'Scrape service done'
    
        return services
        
    def removeSpecialChar(s, exceptchar=''):
        if s != None:
            firstchar = s[0]
            charlst = ['*','-','/','(',')','.',',',':','+','\r\n','\r','\n']
            for char in charlst:
                if exceptchar == 'pl' and char == '-':
                    continue
                if char != exceptchar:
                    s = s.replace(char,'')
            if exceptchar == 'phone' and firstchar == '+':
                s = firstchar + s
        s = s.replace('#',',,')     
        return s
 
    
        

 
    
 
 

       
       
       
       
       
       
       
       
           