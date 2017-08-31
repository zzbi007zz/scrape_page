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
    

import json
import datetime
import csv
import time
import sys
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

app_id = "1862061990718335"
app_secret = "61fffa1e165ec2550c4861111f4b7d9c"  # DO NOT SHARE WITH ANYONE!
page_id = sys.argv[1]


# input date formatted as YYYY-MM-DD
since_date = "2017-06-01"
until_date = "2017-07-01"

access_token = app_id + "|" + app_secret


def request_until_succeed(url):
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read()


# Needed to write tricky unicode correctly to csv
def unicode_decode(text):
    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def getFacebookPageFeedUrl(base_url):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    fields = "&fields=message,link,created_time,type,name,id," + \
        "comments.limit(0).summary(true),shares,reactions" + \
        ".limit(0).summary(true)"

    return base_url + fields


def getReactionsForStatuses(base_url):

    reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
    reactions_dict = {}   # dict of {status_id: tuple<6>}

    for reaction_type in reaction_types:
        fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
            reaction_type.upper())

        url = base_url + fields

        data = json.loads(request_until_succeed(url))['data']

        data_processed = set()  # set() removes rare duplicates in statuses
        for status in data:
            id = status['id']
            count = status['reactions']['summary']['total_count']
            data_processed.add((id, count))

        for id, count in data_processed:
            if id in reactions_dict:
                reactions_dict[id] = reactions_dict[id] + (count,)
            else:
                reactions_dict[id] = (count,)

    return reactions_dict


def processFacebookPageFeedStatus(status):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_type = status['type']

    status_message = '' if 'message' not in status else \
        unicode_decode(status['message'])
    link_name = '' if 'name' not in status else \
        unicode_decode(status['name'])
    status_link = '' if 'link' not in status else \
        unicode_decode(status['link'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
        status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + \
        datetime.timedelta(hours=-5)  # EST
    status_published = status_published.strftime(
        '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
        status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
        status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    return (status_id, status_message, link_name, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares)


def scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date):
    with open('{}_facebook_statuses.csv'.format(page_id), 'w') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "link_name", "status_type",
                    "status_link", "status_published", "num_reactions",
                    "num_comments", "num_shares", "num_likes", "num_loves",
                    "num_wows", "num_hahas", "num_sads", "num_angrys",
                    "num_special"])

        has_next_page = True
        num_processed = 0
        scrape_starttime = datetime.datetime.now()
        after = ''
        base = "https://graph.facebook.com/v2.9"
        node = "/{}/posts".format(page_id)
        parameters = "/?limit={}&access_token={}".format(100, access_token)
        since = "&since={}".format(since_date) if since_date \
            is not '' else ''
        until = "&until={}".format(until_date) if until_date \
            is not '' else ''

        print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))

        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = base + node + parameters + after + since + until

            url = getFacebookPageFeedUrl(base_url)
            statuses = json.loads(request_until_succeed(url))
            reactions = getReactionsForStatuses(base_url)

            for status in statuses['data']:

                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    status_data = processFacebookPageFeedStatus(status)
                    reactions_data = reactions[status_data[0]]

                    # calculate thankful/pride through algebra
                    num_special = status_data[6] - sum(reactions_data)
                    w.writerow(status_data + reactions_data + (num_special,))

                num_processed += 1
                if num_processed % 100 == 0:
                    print("{} Statuses Processed: {}".format
                          (num_processed, datetime.datetime.now()))

            # if there is no next page, we're done.
            if 'paging' in statuses:
                after = statuses['paging']['cursors']['after']
            else:
                has_next_page = False

        print("\nDone!\n{} Statuses Processed in {}".format(
              num_processed, datetime.datetime.now() - scrape_starttime))


if __name__ == '__main__':
    scrapeFacebookPageFeedStatus(page_id, access_token, since_date, until_date)
    
    
# if __name__ == "__main__" :
#     service = _ServiceParser()

              