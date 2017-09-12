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
import itertools
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

    xpath_normal_price = "//li[not(@category='Preferente')]/ul/li/span[@id='lblNormalPrice']"
    xpath_sv_name = "//li[not(@category='Preferente')]/ul/li/div/span[@id='lblServiceName']"
    xpath_sv_desc = "//li[not(@category='Preferente')]/ul/li/div/p[@id='lblDescriptionService']"
    xpath_sv_dur = "//li[not(@category='Preferente')]/ul/li/div/span[@id='lblTime']"
    xpath_lst = "//ul[@class='bcmContentServiceListFront ClassAccordion']/li[@class='bcmContentServiceListFront']/h3/text()"
    xpath_service = "//ul[@class='bcmContentServiceListFront ClassAccordion']"
    xpath_cates = "//ul[not(@category='Preferente')]/ul"


    services = []
    venues = []
    _lstVenues = []
    venues_csv = []
    services_csv = []
    page = 0  
    outFileVN = ''
    outFileSV = ''
    cate_s = []
    
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
            index = 0
            print "Number of venues is : " + str(len(self._lstVenues))
            for i in range(index,len(self._lstVenues)):
                try:
                    ven = self.__VenueParser(self._lstVenues[i])
                   
                except Exception, ex:
                     print "File ",str(index), ":", ex
                     Util.log.error("File " + str(i) + ": " + ex.message)
                     index+=1
                ven.writeToFile(self.folder,index,self.__name__)
                
                    
            if len(self.venues_csv) > 0:
                 self.writelist2File(self.__name__,self.venues_csv,self.outFileVN)
            if len(self.services_csv) > 0:
                 self.writelist2File(self.__name__,self.services_csv,self.outFileSV)

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
                # urlDetail = "https://www.bucmi.com/Bika Depilacion Hilo Moncloa"
                spaceRegex = re.compile(r"\s+").search(urlDetail)
                if spaceRegex:
                    urlDetail = urlDetail.replace(" ","%20")

                vens.scrape_page = urlDetail
                
                vens.services = self.__ServicesParser(urlDetail)

                _xmlMCate = Util.getRequestsXML(urlDetail,"//nav[@class='bcmMenu']")
                _xpathCate = '//a[re:test(@id,"^Cat_[0-9]")]'  
                _xpathRate = ".//div/span[@class='RatingCount']"
                _xpathSCore = ".//span[@class='Score']"
                xmlInfo = Util.getRequestsXML(urlDetail,".//div[@class='VenueInfo']")
                xmlLogo =  Util.getRequestsXML(urlDetail, ".//div[@class='VenueLogo']/a[@class='goingToImg']/img")
                for _item in xmlInfo:
                    for score in xmlInfo.xpath(_xpathSCore):
                        vens.hqdb_review_score = score.text
                    for rate in xmlInfo.xpath(_xpathRate):
                        rate = rate.text
                        # vens.hqdb_nr_reviews = rate.text
                        rate = [int(s) for s in rate.split() if s.isdigit()]
                        rate = rate[0]
                        vens.hqdb_nr_reviews = str(rate)
                for i in xmlLogo:
                    for img in i.xpath("@src"):
                        vens.venue_images = img
                  
                # idx = 0
                # for i in range(idx,len(_xmlMCate)):
                #         venueCate = []
                #         for cate in _xmlMCate.xpath(_xpathCate,namespaces={'re': "http://exslt.org/regular-expressions"}):
                #
                #                 _cate = cate.text.strip()
                #                 venueCate.append(_cate)
                #
                #         vens.category = ",".join(venueCate)
                        
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
                for t in tel.xpath("@href"):
                        phoneNum = t
                        phoneNum = phoneNum[4:]
                        # vens.office_number = phoneNum
                        phoneRegex = re.compile(r'^6\d+|^7\d+')
                        telNum = phoneRegex.search(phoneNum)
                        if telNum:
                            print telNum.group()
                            telNum = telNum.group()
                            vens.mobile_number = telNum
                            if vens.mobile_number != None:
                                vens.mobile_number = ""
                        else:
                            vens.office_number = phoneNum
                            if vens.mobile_number != None:
                                vens.mobile_number = ""

                addr = xmlVenueDetail.xpath("//div[@class='DireccionWrap']/node()[3]")
                if addr != None and len(addr) != None:
                    baseAdr= addr[0]

                    baseAdr = addr[0]
                    addRegEx = re.compile(r'\w+/\s\w+,\s\d+\s')
                    street = addRegEx.search(baseAdr)
                    zipCodeRegEx = re.compile(r'\d{5}')
                    zipCode = zipCodeRegEx.search(baseAdr)
                    if street:
                        street = street.group()
                        vens.street = street
                    if zipCode:
                        zipCode = zipCode.group()
                        vens.zipcode = zipCode

                     
                venueImg = xmlVenueDetail.xpath(self._xpath_img)
                images = []
                for item in venueImg:
                    for img in item.xpath("@src"): 
                        _imgLst = images.append(img)
                
                vens.img_link = images

                xmlLat = xmlVenueDetail.xpath(self._xpath_lat)
                for item in xmlLat:
                    for lat in item.xpath("@value"):
                        vens.latitude = str(lat)
                        print str(lat)
                xmlLong = xmlVenueDetail.xpath(self._xpath_long)
                for item in xmlLong:
                    for long in item.xpath("@value"):
                        vens.longitude = str(long)
                        print long
 
                if self._lstVenues != None and len(self._lstVenues) > 0:
            
                    self._lstVenues.append(vens)
                    print str(self.page) + ") Scrapping chain 377 page " + vens.scrape_page
                    print len(self._lstVenues)
                vens.writeToFile(self.folder,self.page,vens.name_of_contact)
                self.venues_csv.append(vens)
                
                self.page+=1    
        return vens
   
    def __ServicesParser(self,url):
        services = []
        
        print 'Getting service page ', url
        try :
            sv1 = self._serviceParser1(url)
            services += sv1[:]
            # sv2 = self._serviceParser2(url)
            # services += sv2[:]
            sv3 = self._serviceParse(url)
            services += sv3[:]
        except TypeError, er:
            print "Error" + str(er)

         
        print 'Scrape service done'
      
        return services

    def _serviceParser1(self, url):
        services = []
        xpath_service = "//form[@id='Form']/main"
        xmlService = Util.getRequestsXML(url, xpath_service)
        cates = xmlService.xpath("//li[contains(@class,'Preferente')]")
        lblServiceName = xmlService.findall(".//li[@category='Preferente']/ul/li/div/span[@id='lblServiceName']")
        lblTime = xmlService.findall(".//li[@category='Preferente']/ul/li/div/span[@id='lblTime']")

        lblDescriptionService = xmlService.findall(".//li[@category='Preferente']/ul/li/div/p[@id='lblDescriptionService']")
        lblNormalPrice = xmlService.findall(".//li[@category='Preferente']/ul/li/span[@id='lblNormalPrice']")

        print "Getting service section 1 " + url

        for i in range(len(cates)):
                sv = Service()
                sCate = xmlService.findall(".//li[@category='Preferente']")
                ct = sCate[0].attrib
                for k,v in ct.items():
                    if k=='category':
                        sv.service_category = v

                sName = xmlService.findall(".//span[@id='lblServiceName']")
                sv.service = sName[i].text


                sTime = xmlService.findall(".//span[@id='lblTime']")
                sTime = sTime[i].text
                sTime = re.search(r'\d+', sTime).group()
                dbTime = int(sTime) * 60
                sv.duration = dbTime


                sPrice = xmlService.findall(".//span[@id='lblNormalPrice']")
                sv.price = sPrice[i].text

                sDesc = xmlService.findall(".//p[@id='lblDescriptionService']")

                sv.description = sDesc[i].text
                services.append(sv)
                print "Done section 1"
        return services



    # Count number of category
    def _countCate(self,url):
       xmlService = Util.getRequestsXML(url, self.xpath_service)
       xmlServiceCate = xmlService.xpath(self.xpath_lst)
       for i in range(len(xmlServiceCate)):
            temp_cate = xmlServiceCate[0]
            if temp_cate not in cate_s:
              xpath_count = "count(//li[@category='" + xmlServiceCate[i] + "'])"
            elif temp_cate in cate_s:
                xpath_count = xpath_count = "count(//li[@category='" + xmlServiceCate[i+1] + "'])"
            numbSv = xmlService.xpath(xpath_count)
            countNum = int(numbSv)
            cate_s.append(temp_cate)
            return countNum


    def _serviceParse(self,url):
        print "Service section 2"
        service = []
        xpath_sv= "//form[@id='Form']/main"
        xmlService = Util.getRequestsXML(url, xpath_sv)

        # if xmlService != None:
        #     ul_tag = xmlService.xpath(".//ul[@class='bcmContentServiceListFront ClassAccordion']")
        #     numb = 0
        #     for pos in ul_tag[0].getchildren():
        #         if pos.tag == "li":
        li = xmlService.xpath('//li[@class="bcmContentServiceListFront"]')
        for content in li:
            for child in content.getchildren():
                if child.tag == "h3":
                    print child.text
                    cate = child.text
                else:
                    svName = child.xpath('.//span[@id="lblServiceName"]/text()')
                    duration = child.xpath('.//span[@id="lblTime"]/text()')
                    r = re.compile(r'\s\w+')
                    duration = [r.sub("", item) for item in duration]
                    duration = [int(x) for x in duration]
                    duration = [x * 60 for x in duration]
                    desc = child.xpath('.//p[@id="lblDescriptionService"]')
                    price = child.xpath(".//span[@id='lblNormalPrice']")

                    for i in range(0,len(svName)):
                        sv = Service()
                        sv.service_category = cate
                        sv.duration = duration[i]
                        sv.service = svName[i]
                        sName = svName[i]
                        sv.price = price[i].text
                        sv.description = desc[i].text

                        service.append(sv)



        return service


 
 

       
       
       
       
       
       
       
       
           