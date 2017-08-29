from __future__ import unicode_literals
from lxml import html
from lxml import etree as ET
import re
from bs4 import BeautifulSoup
import json
import lxml.html
import requests
import requests.packages.urllib3 as urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from _elementtree import fromstring
requests.packages.urllib3.disable_warnings()


def getYQLXML(select, url, xpath, spec=False):
    try:
        baseurl = "https://query.yahooapis.com/v1/public/yql"
        query = "select * from htmlstring where url='{0}' and xpath='{1}'"
        query = query.format(url,xpath)
        params = {
                "q":query,
                "env":"store://datatables.org/alltableswithkeys"
            }
        headers = {
                'content-type': "application/x-www-form-urlencoded",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"           
            }
        response = requests.get(baseurl, headers=headers, params=urlencode(params),timeout=(60,60),verify=False)
        body = response.text.encode('utf-8')
        if spec == True:
            return body
        xml = ET.ElementTree(ET.fromstring(body))
        xml = xml.getroot()[0][0]
        if xml.text != None:
            xml = xml.text.replace('\r','').replace('\n','').strip()
            xml = '<results>' + xml + '</results>'
            xml = ET.ElementTree(ET.fromstring(xml))
            return xml.getroot()
    except:
        return None

def GETRequest(url, headers=None, params=None):
    '''
    return a string XML  
    '''
    rq = requests.get(url, data=params, headers=headers)
    body = rq.text.encode("utf8")
    return body
def POSTRequest(url, headers=None, params=None):
    '''
    return a string XML  
    '''
    rq = requests.post(url, data=params, headers=headers, timeout=(60,60))
    body = rq.text.encode('utf8')
    return body

def GetHTMLResponse(url, xpath, headers=None, params=None):
    respone = requests.get(url, data=params, headers=headers)
    content = respone.text
    htmlData = html.fromstring(content)
        
    return htmlData.xpath(xpath)

def getRequestsXML(url,xpath,spec=False,encoding=True):
    try:
        headers = {
            'content-type': "application/x-www-form-urlencoded",   
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        response = requests.request("GET", url, headers=headers,timeout=(60,60),verify=False)        
        htmlDocument = html.fromstring(response.content.decode(response.encoding))
        if encoding == False:
            htmlDocument = html.fromstring(response.content)
        if spec == True:
            return htmlDocument
        else:
            xmlTemp = htmlDocument.xpath(xpath)
            root = ET.Element('results')
            for xml in xmlTemp:
                root.append(xml)
            return root
    except Exception,ex:
        return None 
 
# url = 'https://www.bucmi.com'
# xpath = "//div[@class='dvRecentLocation']/ul/li/span[@class='LocationAddress']"
# http = urllib3.PoolManager()
# rq= requests.get(url)
# soup = BeautifulSoup(rq.content, 'html.parser')
# css_tag = soup.find('span', 'LocationAddress').text.strip().encode('utf8')
# div_tag = soup.select_one("div.dvRecentLocation")
# span_tag = div_tag.select_one("span.LocationAddress")


# _xmlDoc = getRequestsXML(url)

def _ServiceParser():
    print "Getting service" 
    url = "https://www.bucmi.com/rosaserrafashion"
    xpath_addr = "//header/p"
    xmlAddr = getRequestsXML(url,xpath_addr)
    idx = 0
    for i in range(idx,len(xmlAddr)):
        _addr = xmlAddr.findall("a").attrib("title")
        print _addr
    


if __name__ == "__main__" :
    service = _ServiceParser()

#     

# def _locate_():
#     lat_att = []
#     long_att = []
#     
#     lat_attr = soup.findAll("li", {"lat":True})
#     long_attr = soup.findAll("li", {"long":True})
#     for el , ln in lat_attr,long_attr:
#         lat_att.append(el["lat"])
#          print el["lat"], ln["long"]
      
#     return lat_att 

    
    
# def _getCities():
#     cities = []
#     for sp in soup.select("div.dvRecentLocation span"):
#         cities.append(sp.text.strip())
#     return cities
# # 
# if __name__ == "__main__":
#     city = []
#     city = _getCities()
#     len_ = len(city)
#     idx = 0
#     _url = "https://www.bucmi.com/<city>.html?search=<city>,+Espa%C3%B1a"
# 
#     for el in range(idx,len(city)):
# #         print city[el]
#         _new_url = _url.replace("<city>", city[el])
#         _nav = Util.navigate(_new_url)
#         if (_nav) is not None:
#             ''
#             
# #     
#          
            
#             self.__getLinkVenues(opt.find("span").attrib("LocationAddress"))
            
#         print "Getting list of Venues"
#         _urlVenue = 'https://www.bucmi.com/<city>.html?search=<city>,+Espa%C3%B1a'
#         _lstVenue = []
#         _lstVenue = self._getCities()
#         idx = 0 
#         for i in range(idx,len(_lstVenue)):
#              _tempUrl = _urlVenue.replace("<city>", _lstVenue[idx])
#              print _tempUrl
             
  
#         _xmlVenues = Util.getRequestsXML(self._url_venue,self._xpath_lstVenues)
#         _lstVenue = []
#         if _xmlVenues != None and len(_xmlVenues) > 0:
#             for li in _xmlVenues:
# 
#                 ven = Venue()
#                 ven.name = self.__name__
#                 
                
#         print "Getting list of Venues"
#         response = requests.get(self._url_lstVenues)
#         lsturl = html.fromstring(response.content)
#         _lstVenue = lsturl.xpath('//div[@class="dvRecentLocation"]/ul/li/span[@class="LocationAddress"]/text()')
#         _lstVenue = [Util.removeSpecialChar(x) for x in _lstVenue]
#         _lstVenue =[Util.removedoubleSpace(x) for x in _lstVenue]
#         if _lstVenue != None and len(_lstVenue) > 0 :
#                 for item in _lstVenue:   
# #                     _venueXpath = "//ul/li[@location='"+item+"']"
# #                     _xmlvenue = Util.getRequestsXML(self._url_lstVenues,_venueXpath)                       
#                     ven = Venue()
#                     ven.name = self.__name__
#                     ven.scrape_page = self._url_lstVenues 
     

                
                
                