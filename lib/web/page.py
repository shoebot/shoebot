### PAGE #############################################################################################
# Code for querying the HTML DOM.
# It wraps BeautifulSoup by Leonard Richardson.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

from BeautifulSoup import BeautifulSoup, Tag

from url import URLAccumulator, URLParser
from html import replace_entities, plain
from cache import Cache

def clear_cache():
    Cache("html").clear()

### PAGE ERRORS ######################################################################################

class PageUnicodeError(Exception):
    def __str__(self): return str(self.__class__)  

class PageParseError(Exception):
    def __str__(self): return str(self.__class__)  

### PAGE #########@###################################################################################

Tag.find_all = Tag.findAll

class Page(BeautifulSoup, URLAccumulator):
    
    """ DOM tree of a HTML page.
    
    Page is essentially an asynchronous download of a BeautifulSoup page.
    It has the following methods:
    description() - returns meta description
    keywords() - returns meta keywords
    links() - by default, returns external links
    find(tag, attribute=value) - find the first tag with given attributes
    find_all(tag, attribute=value) - find all tags with given attributes
    
    find() and find_all() return objects that have find() and find_all() too.
    They're essentially lists of Tag objects.
    
    Alternatively, get tags directly as properties, e.g.
    page.body.p - returns a list of all p Tag objects (each has find() and find_all() )
    
    To get attributes from a Tag:
    p["id"]
    
    """
    
    def __init__(self, url, wait=10, asynchronous=False, cached=True):
        
        if cached: 
            cache = "html"
        else:
            cache = None
        URLAccumulator.__init__(self, url, wait, asynchronous, cache)

    def load(self, data):
        
        data = replace_entities(data)
        try:
            BeautifulSoup.__init__(self, data)
        except UnicodeEncodeError:
            self.error = PageUnicodeError()
            BeautifulSoup.__init__(self, "")
        except:
            self.error = PageParseError()
            BeautifulSoup.__init__(self, "")            

    def _title(self):
        
        """ Returns the page title.
        """    
        
        return self.find("title").string
        
    title = property(_title)    

    def _description(self):
        
        """ Returns the meta description in the page.
        """        

        meta = self.find("meta", {"name":"description"})
        if isinstance(meta, dict) and \
           meta.has_key("content"):
            return meta["content"]
        else:
            return u""
            
    description = property(_description)

    def _keywords(self):
        
        """ Returns the meta keywords in the page.
        """
        
        meta = self.find("meta", {"name":"keywords"})
        if isinstance(meta, dict) and \
           meta.has_key("content"):
            keywords = [k.strip() for k in meta["content"].split(",")]
        else:
            keywords = []
            
        return keywords
        
    keywords = property(_keywords)

    def links(self, external=True):
        
        """ Retrieves links in the page.
        
        Returns a list of URL's.
        By default, only external URL's are returned.
        External URL's starts with http:// and point to another
        domain than the domain the page is on.
        
        """
        
        domain = URLParser(self.url).domain
        
        links = []
        for a in self("a"):
            for attribute, value in a.attrs:
                if attribute == "href":
                    if not external \
                    or (value.startswith("http://") and value.find("http://"+domain) < 0):
                        links.append(value)
                        
        return links
    
    def find_class(self, classname, tag=""):
        return self( tag, {"class": classname} )
        
def parse(url, wait=10, asynchronous=False, cached=True):
    return Page(url, wait, asynchronous, cached)

"""
import url
url = url.create("http://nodebox.net/code/index.php/Share")
url.query["p"] = 2
print url

page = parse(url)
print page.title
print page.title.string
print page.description()
print page.keywords()

print page.find(id="content")["id"]
# find() returns a list of Tags and has a find() method
for p in page.body.find("div", id="content").find_all("p"):
    print ">>>", plain(p)

print page.links()
print page.find_all("h2")

print page.contents[0].name

# .div returns a list of Tags
print page.body.div(id="content")[0].p
"""