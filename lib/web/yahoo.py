### YAHOO ############################################################################################
# Code for querying Yahoo! for search terms, images, news and spelling.
# Also contains the searchenginesort algorithm originally used in Prism for NodeBox.

# Authors: Frederik De Bleser, Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import urllib
import xml.dom.minidom

from url import URLAccumulator, HTTP403Forbidden
from html import replace_entities
from cache import Cache

def clear_cache():
    Cache("yahoo").clear()

### YAHOO SETTINGS ###################################################################################

YAHOO_ID         = "Bsx0rSzV34HQ9sXprWCaAWCHCINnLFtRF_4wahO1tiVEPpFSltMdqkM1z6Xubg"

### YAHOO SERVICES ###################################################################################

YAHOO_SEARCH     = "search"
YAHOO_IMAGES     = "images"
YAHOO_NEWS       = "news"
YAHOO_SPELLING   = "spelling"

### YAHOOERROR #######################################################################################

class YahooError(Exception):
    def __str__(self): return str(self.__class__) 
    
class YahooLimitError(YahooError):
    # Daily limit was exceeded.
    def __str__(self): return str(self.__class__) 

### YAHOO LICENSE ####################################################################################

def license_key(id=None):
    
    global YAHOO_ID
    if id != None:
        YAHOO_ID = id
    return YAHOO_ID

### YAHOO UNICODE ####################################################################################

def format_data(s):
    
    """ Yahoo library returns Unicode strings.
    """
    
    return s.encode("utf-8")

### YAHOORESULT ######################################################################################
    
class YahooResult:

    """ Creates an item in a YahooSearch list object.
    """
    
    def __init__(self):
        
        self.title       = None
        self.url         = None
        self.description = None
        self.type        = None
        self.date        = None
        self.width       = None # images
        self.height      = None # images
        self.source      = None # news
        self.language    = None # news

    def __repr__(self):
        
        s = format_data(self.url)
        return s

### YAHOORESULTS #####################################################################################


class YahooResults(list):
    
    """ Creates a list of results from a Yahoo query.
        
    The total number of available results is stored in the results property.
    Each item in the list is a YahooResult object.
        
    """
    
    def __init__(self, q, data, service=YAHOO_SEARCH):
        
        self.query = q
        self.total = 0
        if data == "": return
        dom = xml.dom.minidom.parseString(data)
        doc = dom.childNodes[0]
        self.total = int(doc.attributes["totalResultsAvailable"].value)
        
        for r in doc.getElementsByTagName('Result'):
            
            item = YahooResult()
            item.title        = self._parse(r, 'Title')
            item.url          = self._parse(r, 'Url')
            item.description  = self._parse(r, 'Summary')
            
            if service == YAHOO_SEARCH:
                item.type     = self._parse(r, 'MimeType')
                item.date     = self._parse(r, 'ModificationDate')
            if service == YAHOO_IMAGES:
                item.type     = self._parse(r, 'FileFormat')
                item.width    = int(self._parse(r, 'Width'))
                item.height   = int(self._parse(r, 'Height'))
            if service == YAHOO_NEWS:
                item.date     = self._parse(r, 'ModificationDate')
                item.source   = self._parse(r, 'NewsSourceUrl')
                item.language = self._parse(r, 'Language')
            
            self.append(item)
            
    def _parse(self, e, tag):
        
        """ Parses the text data from an XML element defined by tag.
        """
        
        tags = e.getElementsByTagName(tag)
        children = tags[0].childNodes
        if len(children) != 1: return None
        assert children[0].nodeType == xml.dom.minidom.Element.TEXT_NODE
        
        s = children[0].nodeValue
        s = format_data(s)
        s = replace_entities(s)
        
        return s
        
    def __cmp__(self, other):
        
        """ Compares with another YahooSearch based on the number of results.
        """
    
        if self.total > other.total:
            return 1
        elif self.total < other.total: 
            return -1
        else:
            return 0

#### YAHOOSEARCH #####################################################################################

class YahooSearch(YahooResults, URLAccumulator):
    
    def __init__(self, q, start=1, count=10, service=YAHOO_SEARCH, context=None, 
                 wait=10, asynchronous=False, cached=True):

        """ Searches Yahoo for the given query.
    
        By default, return cached results whenever possible.
        Otherwise, go online and update the local cache.
        The number of results is limited to count and starts at the given index.
    
        The returned results depend on the service used: 
        web pages, images, news, spelling suggestion or contextual links.
    
        """
        
        self.query = q
        self.service = service
        
        if cached:
            cache = "yahoo"
        else:
            cache = None

        url = "http://search.yahooapis.com/"
        if service == YAHOO_SEARCH and context == None : url += "WebSearchService/V1/webSearch?"
        if service == YAHOO_SEARCH and context != None : url += "WebSearchService/V1/contextSearch?"
        if service == YAHOO_IMAGES   :  url += "ImageSearchService/V1/imageSearch?"
        if service == YAHOO_NEWS     :  url += "NewsSearchService/V1/newsSearch?"
        if service == YAHOO_SPELLING :  url += "WebSearchService/V1/spellingSuggestion?"
        arg = urllib.urlencode((("appid", YAHOO_ID), 
                                ("query", q),
                                ("start", start),
                                ("results", count),
                                ("context", unicode(context))))
        
        url += arg
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, ".xml")
        
    def load(self, data):
        
        if str(self.error.__class__) == str(HTTP403Forbidden().__class__):
            self.error = YahooLimitError()
            
        YahooResults.__init__(self, self.query, data, self.service)

######################################################################################################

def search(q, start=1, count=10, context=None, wait=10, asynchronous=False, cached=False):
    
    """ Returns a Yahoo web query formatted as a YahooSearch list object.
    """
    
    service = YAHOO_SEARCH
    return YahooSearch(q, start, count, service, context, wait, asynchronous, cached)  

def search_images(q, start=1, count=10, wait=10, asynchronous=False, cached=False):
    
    """ Returns a Yahoo images query formatted as a YahooSearch list object.
    """
    
    service = YAHOO_IMAGES
    return YahooSearch(q, start, count, service, None, wait, asynchronous, cached)   

def search_news(q, start=1, count=10, wait=10, asynchronous=False, cached=False):
    
    """ Returns a Yahoo news query formatted as a YahooSearch list object.
    """
    
    service = YAHOO_NEWS
    return YahooSearch(q, start, count, service, None, wait, asynchronous, cached)  

#### YAHOOSPELLING ###################################################################################

class YahooSpelling(YahooSearch):
    
    def __init__(self, q, wait, asynchronous, cached):
        
        service = YAHOO_SPELLING
        YahooSearch.__init__(self, q, 1, 1, service, None, wait, asynchronous, cached)
        
    def load(self, data):
        
        dom = xml.dom.minidom.parseString(data)
        doc = dom.childNodes[0]
        r = doc.getElementsByTagName('Result')
        if len(r) > 0:
            r = r[0].childNodes[0].nodeValue
            r = format_data(r)
        else:
            r = q
        
        self.append(r)

def suggest_spelling(q, wait=10, asynchronous=False, cached=False):
    
    """ Returns list of suggested spelling corrections for the given query.
    """
    
    return YahooSpelling(q, wait, asynchronous, cached)

#### YAHOO SORT ######################################################################################

def sort(words, context="", strict=True, relative=True, service=YAHOO_SEARCH,
         wait=10, asynchronous=False, cached=False):
    
    """Performs a Yahoo sort on the given list.
    
    Sorts the items in the list according to 
    the result count Yahoo yields on an item.
    
    Setting a context sorts the items according
    to their relation to this context;
    for example sorting [red, green, blue] by "love"
    yields red as the highest results,
    likely because red is the color commonly associated with love.
    
    """
    
    results = []
    for word in words:
        q = word + " " + context
        q.strip()
        if strict: q = "\""+q+"\""
        r = YahooSearch(q, 1, 1, service, context, wait, asynchronous, cached)
        results.append(r)
        
    results.sort(YahooResults.__cmp__)
    results.reverse()
    
    if relative and len(results) > 0:
        sum = 0.000000000000000001
        for r in results: sum += r.total
        for r in results: r.total /= float(sum)
    
    results = [(r.query, r.total) for r in results]
    return results

######################################################################################################

#r = search("nodebox", cached=False, start=5, count=5)
#print r.total
#for item in r:
#    print item

#r = search_images("nodebox", cached=False, start=1)
#print r.total
#for item in r:
#    print item, item.width, "x", item.height

#r = search_news("apple", cached=False, start=1, asynchronous=True)
#import time
#while not r.done:
#    print "waiting..."
#    time.sleep(0.1)
#print r.total
#for item in r:
#    print item, item.source, item.language

#print suggest_spelling("amazoon")

#results = sort(["green", "blue", "red"], "sky", strict=False, cached=True)
#for word, count in results:
#    print word, count

#ctx = '''
#The apple tree was perhaps the earliest tree to be cultivated, 
#and apples have remained an important food in all cooler climates. 
#To a greater degree than other tree fruit, except possibly citrus, 
#apples store for months while still retaining much of their nutritive value.
#We are not looking for a company named Apple.
#'''
#r = search("apple", cached=False, start=1, context=ctx)
#print r.total
#for item in r:
#    print item.title