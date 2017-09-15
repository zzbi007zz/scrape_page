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



def _serviceParse(self, url):
    print "Service section 2"
    service = []
    xpath_sv = "//form[@id='Form']/main"
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

                for i in range(0, len(svName)):
                    sv = Service()
                    sv.service_category = cate
                    sv.duration = duration[i]
                    sv.service = svName[i]
                    sName = svName[i]
                    sv.price = price[i].text
                    sv.description = desc[i].text

                    service.append(sv)

    return service

if __name__ == "__main__":
    url = "https://www.bucmi.com/cortoycambio"
    sv = _serviceParse(url)