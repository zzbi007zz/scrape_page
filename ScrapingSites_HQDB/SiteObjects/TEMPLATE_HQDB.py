#coding: utf-8
from __future__ import unicode_literals
from BaseSite import BaseSite
from Common import Util,Validation
from lxml import etree as ET
from SiteObjects.Objects_HQDB import Venue, Service
import re
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class TEMPLATE_HQDB(BaseSite):
    '''
    Get information from ""
    '''
    phoneCodeList = None
    __url__ = ''
    _language = ''
    _chain_ = ''
    __name__ = ''
    _url_lstVenues = ''    
    _xpath_lstVenues = ''        
    _url_lstServices = ''
    _xpath_lstServices = ''
    services = []
    venues = []
    outFile = ''
    charReplace = []
    
    
    def __init__(self, output="JSON_Results", isWriteList=None):
        BaseSite.__init__(self, output, self._chain_ + self.__name__)
        self._output = output
        self._isWriteList = isWriteList
    
    
    def doWork(self):
        #Set OutFile Values
        self.outFile = self.outFile = self._chain_ + '_' + Validation.RevalidName(self.__name__)        
        self.phoneCodeList = Util.getPhoneCodeList()
        self.charReplace = Util.getCharReplace()
        '''
        Code Here - Write All JSON
        '''
        #Write CSV Files
        ven = Venue()
        self.__ValidationFields(ven)
        Util.ExportCSV(self.folder,outFile)
    
    def __getListVenues(self):
        print "Getting list of Venues"
        

    def __VenueParser(self):        
        print 'Scrapping: '
        ven = Venue()
        return ven

    def __ServicesParser(self,url,xmlServices):        
        ''

    def __ValidationVenueFields(self,ven):
        for property, value in vars(ven).iteritems():
            #value = getattr(ven,property)
            if isinstance(value,list) and property != 'services':
                for val in value:
                    val = val.encode('utf8').encode('string-escape')
                    for x in self.charReplace:                        
                        val = val.replace(x.get('replace_text'),x.get('with_text'))
                    val = val.decode('string-escape').decode('utf8')
            elif isinstance(value,list) == False:
                value = value.encode('utf8').encode('string-escape')
                for x in self.charReplace:
                    value = value.replace(x.get('replace_text'),x.get('with_text'))
                value = value.decode('string-escape').decode('utf8')
            setattr(ven,property,value)
        if ven.services != None:
            ven.services = self.__ValidationServiceFields(ven.services)
        return ven
                
    def __ValidationServiceFields(self,services):
        for service in services:
            for property,value in vars(service).iteritems():
                value = value.encode('utf8').encode('string-escape')
                for x in self.charReplace:
                    value = value.replace(x.get('replace_text'),x.get('with_text'))
                value = value.decode('string-escape').decode('utf8')
                setattr(service,property,value)
        return services
