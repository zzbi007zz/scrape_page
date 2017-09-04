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
import os, json
import pandas as pd
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
    

# path_jdon_dir = "JSON_Results/chain_377_Bucmi/"
# 
# json_files = [pos_json for pos_json in os.listdir(path_jdon_dir) if pos_json.endswith('.json')]
# jsons_data = pd.DataFrame(columns=['name', 'office_number', 'mobile_number','latitude','longtitude'])
# 
# for index, js in enumerate(json_files):
#     with open(os.path.join(path_to_json, js)) as json_file:
#         json_text = json.load(json_file)
#         
#         name = json_text['name']
#         office_number = json_text['office_number']
#         mobile_number = json_text['mobile_number']
#         latitude = json_text['mobile_number']
#         longtitude = json_text['longtitude']
#         
#         jsons_data.loc[index] = [name,office_number,mobile_number,latitude,longtitude]
#         
# print jsons_data

import json
from glob import glob

data = []

pattern = os.path.join('JSON_Results/', '*.json')
for file_name in glob(pattern):
    with open(file_name) as f:
        data.append(json.load(f))
        print data[0]


              