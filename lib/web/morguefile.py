### MORGUEFILE #######################################################################################
# Code for downloading images from MorgueFile.

# Author: Tom De Smedt.
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
        self.category  = ""
        self.author    = ""
        self.name      = ""
        self.url       = ""
        self.date      = ""
        self.views     = 0
        self.downloads = 0
        
        self.path      = ""
        
    def __str__(self):
        
        return self.name.encode("utf-8")
        
    def __cmp__(self, other):
        
        
        """ Images in a MorgueFile list can be sorted according to number of views.
        """
        
        if self.views > other.views: 
            return -1
        else: 
            return 1
        
    def download(self, size=SIZE_LARGE, thumbnail=False, wait=60, asynchronous=False):
        
        """ Downloads this image to cache.
        
        Calling the download() method instantiates an asynchronous URLAccumulator.
        Once it is done downloading, this image will have its path property
        set to an image file in the cache.
        
        """
        
        if thumbnail == True: size = SIZE_THUMBNAIL # backwards compatibility
        self._size = disambiguate_size(size)
        if self._size != SIZE_THUMBNAIL:
            url = self.url.replace("thumbnails", "lowrez")
        else:
            url = self.url
        
        cache = "morguefile"
        extension = os.path.basename(self.url)[-4:]
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, extension, 2)
        
        if not asynchronous:
            return self.path
        
    def load(self, data):
        
        if self._size != SIZE_THUMBNAIL:
            url = self.url.replace("thumbnails", "lowrez")
        else:
            url = self.url
        
        self.path = self._cache.hash(url)

### MORGUEFILE #######################################################################################

class MorgueFile(list):
    
    def __init__(self, xml):
        
        self._parse(xml)

    def _parse_data(self, e, tag):
        
        return e.getElementsByTagName(tag)[0].childNodes[0].data

    def _parse(self, xml):

        if xml == "": return
        xml = xml.replace("& ", "&amp; ")
        dom = parseString(xml)
        for e in dom.getElementsByTagName("image"):
            img = MorgueFileImage()
            img.id        = self._parse_data(e, "unique_id")
            img.category  = self._parse_data(e, "category")
            img.author    = self._parse_data(e, "author")
            img.name      = self._parse_data(e, "title")
            img.url       = self._parse_data(e, "photo_path")
            img.date      = self._parse_data(e, "date_added")
            img.views     = int(self._parse_data(e, "views"))
            img.downloads = int(self._parse_data(e, "downloads"))
            self.append(img)

### MORGUEFILE SEARCH ################################################################################
            
class MorgueFileSearch(MorgueFile, URLAccumulator):
    
    def __init__(self, q, author=False, max=100, wait=10, asynchronous=False, cached=True):
        
        if cached: 
            cache = "morguefile"
        else:
            cache = None
    
        arg = "terms"
        if author == True: arg = "author"
        url = "http://morguefile.com/archive/archivexml.php"
        url += "?" + arg + "=" + quote_plus(q) + "&archive_max_image=" + str(max)
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
#    print img.views, img.name

#img = images[0]
#img.download()
#image(img.path, 0, 0)