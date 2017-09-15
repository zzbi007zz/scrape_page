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
import HTMLParser
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
    _xpath_Venues = "//section/div/ul/li/a"
    _xpath_LstVenues = '//ul[@class="bcmPagination""]/li[last()-1]'        
    _url_lstServices = ''
    _xpath_lstServices = '//div[@id="divVenueServiceList"]'
    _xpath_addr = "//div[@class='DireccionWrap']"
    _xpath_lat = '//div[@id="dvMapa"]/input[@id="dnn_ctlVenueContent_ctlVenueMap_hdnLatitude"]/@value'
    _xpath_long = '//div[@id="dvMapa"]/input[@id="dnn_ctlVenueContent_ctlVenueMap_hdnLongitude"]/@value'
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
      # self.outFileVN = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Venues.csv'
      # self.outFileSV = self.folder + '/' + self._chain_ + '_' + Validation.RevalidName(self.__name__) + '_Services.csv'
      #
      print "-----------------------------"
      print self._chain_ + self.__name__
      print
      self.__getListVenues()
      self.Write2File()
      if len(self.venues) > 0:
            index = 0
            print "Number of venues is : " + str(len(self.venues))
            for i in range(index,len(self.venues)):
                try:
                    ven = self.venues[i]
                    ven = self.__VenueParser(self.venues[i])
                except Exception, ex:
                     print "File ",str(index), ":", ex
                     Util.log.error("File " + str(i) + ": " + ex.message)

    def Write2File(self):
        if self.venues != None and len(self.venues) > 0:
            print "Number of venues is : " + str(len(self.venues))
            index = 0
            for i in range(len(self.venues)):
                try:
                    print ven + "  a"
                    ven = self.venues[i]

                    if ven != None:
                        name = ''
                        if ven.name != None:
                            name += self.__name__ + ' - ' + ven.name
                        ven.writeToFile(self.folder, index, name.strip('-'))
                        index += 1
                        self.venues.append(ven.toOrderDict())
                except Exception, ex:
                    Util.log.error("File " + str(i) + ": " + ex.message)
        if len(self.venues) > 0:
            Util.writelist2File(self.venues, self.outFileVN)
        if len(self.services) > 0:
            Util.writelist2File(self.services, self.outFileSV)

    def __getListVenues(self):
        print "Getting list of Venues"
        xmlRegions = Util.GetHTMLResponse(self.__url__,self._xpath_Venues)
        for i in xmlRegions:
            url = self.__url__ + i.get("href")
            existing = [x for x in self.venues if x in url]
            if len(existing) <= 0:
                self.venues.append(url)
                self._getLinkVenue(url)

    def _getLinkVenue(self, region, page=1, totalPage=1):
        print "Scraping page: " + str(page)
        # url = region + "?page=" + str(page)
        region = "https://www.bucmi.com/peluqueria/madrid"
        nodes = Util.getRequestsXML(region,"//ul[@class='bcmPagination']/li")
        if nodes != None:
            tag_a = nodes.xpath("//a/@href")
            _numb_arr = []
            for a in tag_a:
                url = str(a)
                p = re.findall("page=(\d+)",url)
                _numb_arr.append(p)
            i = iter(_numb_arr)




            # print total
            # i=1
            # if i <= total:
            #     i+=1
            #     url = region + "?page=" + str(i)
            # elif i >= total:
            #     pass


        # rq = requests.get(region)
        # htmldoc = html.fromstring(rq.content)
        # nodes = htmldoc.xpath('//ul[@class="bcmPagination"]/li[last()]')
        # for content in nodes:
        #     for child in content.getchildren():
        #         print child.text
        #
        #     page += 1
        # self._getLinkVenue(region, page, ttPage)


    def __VenueParser(self, url):
        print "Scraping " + url
        xpathz = "//parent::article/div"
        xmlVenue = Util.getRequestsXML(url,xpathz)
        if xmlVenue != None and len(xmlVenue) > 0:
            vens = Venue()
            vens.country = 'es'
            name = xmlVenue.find(".//h1/a")
            name = name.text
            vens.name = name
            vens.name_of_contact = name
            scrape_page = xmlVenue.xpath("//h1/a/@href")[0]
            spaceRegex = re.compile(r"\s+").search(scrape_page)
            if spaceRegex:
                scrape_page = scrape_page.replace(" ","%20")
            else:
                vens.scrape_page = scrape_page
            print "Page " + scrape_page

            vens.business_website = scrape_page

            review = xmlVenue.find(".//header/div/span")
            review= review.text
            review = [int(s) for s in review.split() if s.isdigit()]
            review = review[0]
            review = str(review)
            print "review " + review
            vens.hqdb_nr_reviews = review
            score = xmlVenue.find(".//div[@class='bcmComentRatio']/div/p/span")
            score = score.text
            print "score " + score
            vens.hqdb_review_score = score
            address = xmlVenue.xpath("//header/p/a/@title")[0]
            zipcode = re.search(r"\d{5}",address)
            vens.zipcode = zipcode.group()
            print "zipcode " + zipcode.group()
            street = ",".join(address.split(",", 2)[:2])
            vens.street = street
            city = address.split(",",4)
            city = city[4]
            vens.city = city
            featured = xmlVenue.xpath("//div[@class='noved-list recommendedPremium' or @class='noved-list recommended']")[0]
            if featured.text == "RECOMENDADO":
                vens.hqdb_featured_ad_type = 'Featured'

            service_url = scrape_page
            xmlPhone = Util.GetHTMLResponse(service_url,"//div[@class='DireccionWrap']/a/@href")
            phonenum = xmlPhone[0]
            phonenum = phonenum[4:]
            print "phone: " + phonenum
            if xmlPhone!= None:
                if phonenum.find('06') == 0 or phonenum.find('07') == 0:
                    vens.mobile_number = phonenum
                else:
                    vens.office_number = phonenum

            xmlImg = Util.GetHTMLResponse(service_url,"//div[@class='VenueLogo']/a[@class='goingToImg']/img/@src")
            if xmlImg != None:
                vens.img_link = xmlImg[0]
            vens.services = self.__ServicesParser(service_url)

            venueImgs = self.GetHTMLResponse(service_url,"//ul/li/a/img/@src")
            if venueImgs != None:
                vens.venue_images = venueImgs
            xmlLat = self.GetHTMLResponse(service_url,self._xpath_lat)
            xmlLong = self.GetHTMLResponse(service_url,self._xpath_long)
            if xmlLat != None and xmlLong!= None:
                lat = str(xmlLat)[0]
                long = str(xmlLong)[0]
                vens.latitude = lat
                vens.longitude = long

        if self.venues != None and len(self.venues) > 0:
            self.venues.append(vens)
            print str(self.page) + ") Scrapping chain 377 page " + vens.scrape_page

        self.page += 1

        return vens

    def GetHTMLResponse(url, xpath, headers=None, params=None):
        respone = requests.get(url, data=params, headers=headers)
        content = respone.text
        htmlData = html.fromstring(content)

        return htmlData.xpath(xpath)
#
    def __ServicesParser(self,url):
        services = []
        print 'Getting service page ', url


#         try :
#             sv1 = self._serviceParser1(url)
#             services += sv1[:]
#             # sv2 = self._serviceParser2(url)
#             # services += sv2[:]
#             sv3 = self._serviceParse(url)
#             services += sv3[:]
#         except TypeError, er:
#             print "Error" + str(er)
#
#
#         print 'Scrape service done'
#
#         return services
#
#     def _serviceParser1(self, url):
#         services = []
#         xpath_service = "//form[@id='Form']/main"
#         xmlService = Util.getRequestsXML(url, xpath_service)
#         cates = xmlService.xpath("//li[contains(@class,'Preferente')]")
#         lblServiceName = xmlService.findall(".//li[@category='Preferente']/ul/li/div/span[@id='lblServiceName']")
#         lblTime = xmlService.findall(".//li[@category='Preferente']/ul/li/div/span[@id='lblTime']")
#
#         lblDescriptionService = xmlService.findall(".//li[@category='Preferente']/ul/li/div/p[@id='lblDescriptionService']")
#         lblNormalPrice = xmlService.findall(".//li[@category='Preferente']/ul/li/span[@id='lblNormalPrice']")
#
#         print "Getting service section 1 " + url
#
#         for i in range(len(cates)):
#                 sv = Service()
#                 sCate = xmlService.findall(".//li[@category='Preferente']")
#                 ct = sCate[0].attrib
#                 for k,v in ct.items():
#                     if k=='category':
#                         sv.service_category = v
#
#                 sName = xmlService.findall(".//span[@id='lblServiceName']")
#                 sv.service = sName[i].text
#
#
#                 sTime = xmlService.findall(".//span[@id='lblTime']")
#                 sTime = sTime[i].text
#                 sTime = re.search(r'\d+', sTime).group()
#                 dbTime = int(sTime) * 60
#                 sv.duration = dbTime
#
#
#                 sPrice = xmlService.findall(".//span[@id='lblNormalPrice']")
#                 sv.price = sPrice[i].text
#
#                 sDesc = xmlService.findall(".//p[@id='lblDescriptionService']")
#
#                 sv.description = sDesc[i].text
#                 services.append(sv)
#                 print "Done section 1"
#         return services
#
#
#     def _serviceParse(self,url):
#
#         print "Service section 2"
#         service = []
#         xpath_sv= "//form[@id='Form']/main"
#         xmlService = Util.getRequestsXML(url, xpath_sv)
#
#         # if xmlService != None:
#         #     ul_tag = xmlService.xpath(".//ul[@class='bcmContentServiceListFront ClassAccordion']")
#         #     numb = 0
#         #     for pos in ul_tag[0].getchildren():
#         #         if pos.tag == "li":
#         li = xmlService.xpath('//li[@class="bcmContentServiceListFront"]')
#         for content in li:
#             for child in content.getchildren():
#                 if child.tag == "h3":
#                     print child.text
#                     cate = child.text
#                     if cate == None:
#                         break
#                 else:
#                     svName = child.xpath('.//span[@id="lblServiceName"]/text()')
#                     duration = child.xpath('.//span[@id="lblTime"]/text()')
#                     r = re.compile(r'\s\w+')
#                     duration = [r.sub("", item) for item in duration]
#                     duration = [int(x) for x in duration]
#                     duration = [x * 60 for x in duration]
#                     desc = child.xpath('.//p[@id="lblDescriptionService"]')
#                     price = child.xpath(".//span[@id='lblNormalPrice']")
#
#                     for i in range(0,len(svName)):
#                         sv = Service()
#                         sv.service_category = cate
#                         sv.duration = duration[i]
#                         sv.service = svName[i]
#                         sName = svName[i]
#                         sv.price = price[i].text
#                         sv.description = desc[i].text
#
#                         service.append(sv)
#
#         return service

       # def _serviceParser1(self):


       
       
       
       
       
           