### MORGUEFILE #######################################################################################
# Code for downloading images from MorgueFile.

# Author: Tom De Smedt, Stuart Axon.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import os
from urllib import quote_plus
from xml.dom.minidom import parseString

from url import URLAccumulator
from cache import Cache

def clear_cache():
    Cache("morguefile").clear()

### MORGUEFILE IMAGE #################################################################################

SIZE_THUMBNAIL = "thumbnail"
SIZE_LARGE     = "medium"

def disambiguate_size(size):
    if size == True  : return SIZE_THUMBNAIL
    if size == False : return SIZE_LARGE
    if size.lower() in ("thumbnail", "thumb", "t", "th", "small", "s"):
        return SIZE_THUMBNAIL
    if size.lower() in ("medium", "m", "large", "l"): 
        return SIZE_LARGE
    return size

class MorgueFileImage(URLAccumulator):
    
    def __init__(self):
        
        self.id        = 0
        self.author    = ""
        self.name      = ""
        self.url       = ""
        self.date      = ""
        self.hi_res    = None
        self.width     = None
        self.height    = None
        
        # For backwards compatibility (don't exist anymore now).
        self.category  = ""
        self.views     = 0
        self.downloads = 0
        
        self.path      = ""
        
    def __str__(self):
        
        return self.name.encode("utf-8")
        
    def download(self, size=SIZE_LARGE, thumbnail=False, wait=60, asynchronous=False):
        
        """ Downloads this image to cache.
        
        Calling the download() method instantiates an asynchronous URLAccumulator.
        Once it is done downloading, this image will have its path property
        set to an image file in the cache.
        
        """
        
        if thumbnail == True: size = SIZE_THUMBNAIL # backwards compatibility
        self._size = disambiguate_size(size)
        if self._size == SIZE_THUMBNAIL:
            url = self.url.replace("/preview/", "/med/")
        else:
            url = self.url
        
        cache = "morguefile"
        extension = os.path.splitext(url)[1]
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, extension, 2)
        
        if not asynchronous:
            return self.path
        
    def load(self, data):
        
        if self._size == SIZE_THUMBNAIL:
            url = self.url.replace("/preview/", "/med/")
        else:
            url = self.url
        
        self.path = self._cache.hash(url)

### MORGUEFILE #######################################################################################

class MorgueFile(list):
    
    def __init__(self, xml):
        
        self._parse(xml)

    def _parse_data(self, e, tag):
        
        return e.getElementsByTagName(tag)[0].childNodes[0].data
        
    def _parse_attribute(self, e, tag, attr):
        
        return e.getElementsByTagName(tag)[0].attributes[attr].value

    def _parse(self, xml):

        if xml == "": return
        xml = xml.replace("& ", "&amp; ")
        xml = xml.decode("utf-8", "ignore")
        dom = parseString(xml)
        for e in dom.getElementsByTagName("item"):
            img = MorgueFileImage()
            img.id        = self._parse_data(e, "media:guid")
            img.author    = self._parse_data(e, "media:credit")
            img.name      = self._parse_data(e, "media:title")
            img.date      = self._parse_data(e, "pubDate")
            img.url       = self._parse_attribute(e, "media:thumbnail", "url").replace("/med/", "/preview/")
            img.hi_res    = self._parse_attribute(e, "media:content", "url")
            img.width     = float(self._parse_attribute(e, "media:content", "width"))
            img.height    = float(self._parse_attribute(e, "media:content", "height"))
            # The width of /preview/ image is always 620,
            # calculacte the height according to this ratio:
            img.width, img.height = 620.0, img.height / img.width * 620.0 
            self.append(img)

### MORGUEFILE SEARCH ################################################################################
            
class MorgueFileSearch(MorgueFile, URLAccumulator):
    
    def __init__(self, q, author=False, max=100, wait=10, asynchronous=False, cached=True):
        
        if cached: 
            cache = "morguefile"
        else:
            cache = None
    
        arg = "qury"
        if author == True: arg = "author"
        url = "http://morguefile.com/archive/xml/"
        url += "?" + arg + "=" + quote_plus(q) + "&lmt=" + str(max)
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, ".xml", 1)

    def load(self, data):
        
        MorgueFile.__init__(self, data)

######################################################################################################
 
def search(q, max=100, wait=10, asynchronous=False, cached=True):
    
    return MorgueFileSearch(q, False, max, wait, asynchronous, cached)
    
def search_by_author(q, max=100, wait=10, asynchronous=False, cached=True):
    
    return MorgueFileSearch(q, True, max, wait, asynchronous, cached)

#images = search("apple")
#images.sort()
#for img in images:
#    print img.name

#img = images[0]
#img.download()
#image(img.path, 0, 0)