
from __future__ import unicode_literals
import requests
import codecs
import io
from lxml import etree as ET
from lxml import html
from urllib import urlencode
from urllib import quote_plus
from HTMLParser import HTMLParser
import os
import csv
import unicodecsv
import json
import datetime
from collections import OrderedDict
import csv
import urllib2
import urllib3
import urllib
from bs4 import BeautifulSoup
def getYQLXML2(select, url, xpath, spec=False):
    baseurl = u"https://query.yahooapis.com/v1/public/yql?"
    yql_query = u"select {0} from htmlstring where url='{1}' and xpath='{2}'"
    yql_query = yql_query.format(select,url,xpath)
    yql_url = baseurl + urllib.urlencode({'q':yql_query}) + u"&env=store://datatables.org/alltableswithkeys"
    result = urllib2.urlopen(yql_url).read()
    if spec == True:
        return result
    else:
        xml = ET.ElementTree(ET.fromstring(result))
        xml = xml.getroot()[0][0]
        if xml.text != None:
            xml = xml.text.replace('\r','').replace('\n','').strip()
            xml = '<results>' + xml + '</results>'
            xml = ET.ElementTree(ET.fromstring(xml))
            return xml.getroot()

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


if __name__ == "__main__":
    url = "https://www.bucmi.com/hair-and-beauty"
    xpath_service = "//ul[@class='bcmContentServiceListFront ClassAccordion']"
    xml = getYQLXML2("*",url,xpath_service)
