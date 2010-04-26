### GOOGLE ###########################################################################################
# Code for querying Google for search terms, images, news and spelling.
# Also contains the searchenginesort algorithm originally used in Prism for NodeBox.

# Author: Tom De Smedt.
# Copyright (c) 2008 by Tom De Smedt.
# See LICENSE.txt for details.

import urllib
import simplejson

from url import URLAccumulator
from html import replace_entities, strip_tags, collapse_spaces
from cache import Cache

def clear_cache():
    Cache("google").clear()

### GOOGLE SETTINGS ##################################################################################

GOOGLE_ID = "ABQIAAAAsHTxlz1n7jNlYECDj_EF1BT1NOe6bJHqZiq60f1JJ3OzEzDM5BQcAozHwWvFrwx2DDlP6xlTRnS6Cw"

### GOOGLE SERVICES ##################################################################################

GOOGLE_SEARCH     = "search"
GOOGLE_IMAGES     = "images"
GOOGLE_NEWS       = "news"
GOOGLE_BLOGS      = "blogs"

### GOOGLEERROR ######################################################################################

class GoogleError(Exception):
    def __str__(self): return str(self.__class__) 

### GOOGLE LICENSE ###################################################################################

def license_key(id=None):
    
    global GOOGLE_ID
    if id != None:
        GOOGLE_ID = id
    return GOOGLE_ID

### GOOGLE UNICODE ###################################################################################

def format_data(s):
    
    """ Gogole library returns Unicode strings.
    """
    
    return s.encode("utf-8")

### GOOGLE IMAGES ####################################################################################

SIZE_SMALL  = "icon"
SIZE_MEDIUM = "medium"
SIZE_LARGE  = "xxlarge"
SIZE_XLARGE = "huge"

def disambiguate_size(size):
    if size.lower() in ("small", "s", "thumbnail", "thumb", "th", "t", "icon"): 
        return SIZE_SMALL
    if size.lower() in ("medium", "m"): 
        return SIZE_MEDIUM
    if size.lower() in ("large", "l"): 
        return SIZE_LARGE
    if size.lower() in ("xlarge", "xl", "huge", "wallpaper"): 
        return SIZE_XLARGE
    return size

### GOOGLERESULT #####################################################################################
    
class GoogleResult:

    """ Creates an item in a GoogleSearch list object.
    """
    
    def __init__(self):
        
        self.title       = None
        self.url         = None
        self.description = None
        self.date        = None # news, blogs
        self.author      = None # news, blogs
        self.location    = None # news

    def __repr__(self):
        
        s = format_data(self.url)
        return s

### GOOGLERESULTS ####################################################################################


class GoogleResults(list):
    
    """ Creates a list of results from a Google query.
        
    The total number of available results is stored in the results property.
    Each item in the list is a GoogleResult object.
        
    """
    
    def __init__(self, q, data, service=GOOGLE_SEARCH):
        
        self.query = q
        self.total = 0
        if data == "": return

        dict = simplejson.loads(data)
        if dict["responseData"] == None: return
        if service != GOOGLE_BLOGS:
            try: self.total = int(dict["responseData"]["cursor"]["estimatedResultCount"])
            except:
                self.total = 0
            
        for r in dict["responseData"]["results"]:
            
            item = GoogleResult()
            self.append(item)
            item.title = self._parse(r["title"])
            item.description = self._parse(r["content"])

            if service != GOOGLE_BLOGS:
                item.url = r["url"]

            if service == GOOGLE_NEWS:
                item.date = r["publishedDate"]
                item.author = r["publisher"]
                item.location = r["location"]
                
            if service == GOOGLE_BLOGS:
                item.url = r["blogUrl"]
                item.date = r["publishedDate"]
                if r["author"] != "unknown":
                    item.author = r["author"]
            
    def _parse(self, str):
        
        """ Parses the text data from an XML element defined by tag.
        """
        
        str = replace_entities(str)
        str = strip_tags(str)
        str = collapse_spaces(str)
        return str

    def __cmp__(self, other):
        
        """ Compares with another GoogleSearch based on the number of results.
        """
    
        if self.total > other.total:
            return 1
        elif self.total < other.total: 
            return -1
        else:
            return 0

#### GOOGLESEARCH ####################################################################################

class GoogleSearch(GoogleResults, URLAccumulator):
    
    def __init__(self, q, start=0, service=GOOGLE_SEARCH, size="",
                 wait=10, asynchronous=False, cached=True):

        """ Searches Google for the given query.
    
        By default, return cached results whenever possible.
        Otherwise, go online and update the local cache.
        The number of results is limited to 8 and starts at the given index.
        You can only return up to 32 results.
    
        The returned results depend on the service used: 
        web pages, images, news or blogs.
    
        """

        self.query = q
        self.service = service

        if cached:
            cache = "google"
        else:
            cache = None
        url = "http://search.yahooapis.com/"
        url = "http://ajax.googleapis.com/ajax/services/search/"
        if service == GOOGLE_SEARCH : url += "web?"
        if service == GOOGLE_IMAGES : 
            url += "images?"
        if service == GOOGLE_NEWS   : url += "news?"
        if service == GOOGLE_BLOGS  : url += "blogs?"
        arg = urllib.urlencode((("v", 1.0),
                                ("q", q),
                                ("start", start),
                                ("rsz", "large"),
                                ("key", GOOGLE_ID),
                                ("imgsz", disambiguate_size(size))))

        url += arg
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, ".txt")
        
    def load(self, data):
        
        #if str(self.error.__class__) == str(HTTP403Forbidden().__class__):
        #    self.error = GoogleLimitError()
            
        GoogleResults.__init__(self, self.query, data, self.service)

######################################################################################################

def search(q, start=0, wait=10, asynchronous=False, cached=False):
    
    """ Returns a Google web query formatted as a GoogleSearch list object.
    """
    
    service = GOOGLE_SEARCH
    return GoogleSearch(q, start, service, "", wait, asynchronous, cached)  

def search_images(q, start=0, size="", wait=10, asynchronous=False, cached=False):
    
    """ Returns a Google images query formatted as a GoogleSearch list object.
    """
    
    service = GOOGLE_IMAGES
    return GoogleSearch(q, start, service, size, wait, asynchronous, cached)   

def search_news(q, start=0, wait=10, asynchronous=False, cached=False):
    
    """ Returns a Google news query formatted as a GoogleSearch list object.
    """
    
    service = GOOGLE_NEWS
    return GoogleSearch(q, start, service, "", wait, asynchronous, cached)  

def search_blogs(q, start=0, wait=10, asynchronous=False, cached=False):
    
    """ Returns a Google blogs query formatted as a GoogleSearch list object.
    """
    
    service = GOOGLE_BLOGS
    return GoogleSearch(q, start, service, "", wait, asynchronous, cached) 
    
#### GOOGLE SORT #####################################################################################

def sort(words, context="", strict=True, relative=True, service=GOOGLE_SEARCH,
         wait=10, asynchronous=False, cached=False):
    
    """Performs a Google sort on the given list.
    
    Sorts the items in the list according to 
    the result count Google yields on an item.
    
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
        r = GoogleSearch(q, 1, service, "", wait, asynchronous, cached)
        results.append(r)
        
    results.sort(GoogleResults.__cmp__)
    results.reverse()
    
    if relative and len(results) > 0:
        sum = 0.000000000000000001
        for r in results: sum += r.total
        for r in results: r.total /= float(sum)
    
    results = [(r.query, r.total) for r in results]
    return results

######################################################################################################

#r = search("food", cached=True, start=0)
#print r.total
#for item in r:
#    print item

#print sort(["green", "blue", "red"], "apple")



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