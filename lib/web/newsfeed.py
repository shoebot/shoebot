### NEWSFEED #########################################################################################
# Code for parsing newsfeeds. 
# It wraps the Universal Feedparser by Mark Pilgrim.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import os

from feedparser import feedparser

from url import URLAccumulator
from html import strip_tags
from cache import Cache

def clear_cache():
    Cache("newsfeed").clear()

### FAVORITE NEWSFEED ################################################################################

favorites = {}
try:
    path = os.path.join(os.path.dirname(__file__), "newsfeed.txt")
    for f in open(path).readlines():
        f = f.split(",")
        favorites[f[0].strip()] = f[1].strip()
except:
    pass

def favorite_url(name):

    if favorites.has_key(name):
        return favorites[name]

    for key in favorites:
        if key.lower().find(name.lower()) >= 0:
            return favorites[key]

    return None

favorite = favorite_url

### NEWSFEED #########################################################################################

class Newsfeed:
    
    """ Wrapper for the feedparser.FeedParserDict class.
    
    Ensures that Newsfeed.items redirects to Newsfeed.entries,
    and returns an empty string (by default) instead of raising an error
    when a key could not be found - this way we don't have to check 
    if a key exists before fetching its value.
    
    """
    
    def __init__(self, feed, none=u""):
        self._feed = feed
        self._none = none

    def __call__(self, *args):
        raise TypeError, "Newsfeed object not callable"

    def __repr__(self):
        return strip_tags(self._feed.__repr__())
    
    def __unicode__(self):
        return strip_tags(self._feed)
    
    def __str__(self):
        try: 
            s = self._feed.encode("utf-8")
        except:
            s = self._feed.__str__()
        return strip_tags(s)

    def __getitem__(self, item):
        try: return Newsfeed(self._feed.__getitem__(item))
        except:
            return Newsfeed(self._none)
    
    def has_key(self, key):
        return self._feed.has_key(key)
    
    def __iter__(self):
        return self._feed.__iter__()
    
    def __getattr__(self, a):
        if a == "items": a = "entries"
        try:
            a = self._feed.__getattr__(a)
            if isinstance(a, list): 
                a = [Newsfeed(x, self._none) for x in a]
            return Newsfeed(a)    
        except:
            return Newsfeed(self._none)

### NEWSFEED DOWNLOAD ################################################################################

class NewsfeedDownload(Newsfeed, URLAccumulator):
    
    """ Asynchronous cached Newsfeed.
    """
    
    def __init__(self, url, wait=10, asynchronous=False, cached=True, none=""):
        
        self._feed = None
        self._none = none
        
        if cached: 
            cache = "newsfeed"
        else:
            cache = None
            
        # Refresh cached news results every day.
        if cached and Cache(cache).age(url) > 0:
            Cache(cache).remove(url)
            
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, ".xml")

    def load(self, data):
        
        parsed = feedparser.parse(data)
        Newsfeed.__init__(self, parsed, self._none)
            
def parse(url, wait=10, asynchronous=False, cached=True, none=""):
    
    nf = NewsfeedDownload(url, wait, asynchronous, cached, none)
    try:
        # Some shortcuts:
        nf.title = nf.channel.title
        nf.description = nf.channel.description
        nf.link = nf.channel.link
        nf.date = nf.channel.data
    except:
        pass
    
    return nf

"""
url = favorite_url("white house")
newsfeed = parse(url)

print "Channel:", newsfeed.channel.title
print "Channel description:", newsfeed.channel.description
print "Channel link:", newsfeed.channel.link
print "Channel date:", newsfeed.channel.date
print "Encoding:", newsfeed.encoding

for item in newsfeed.items:
    
    print "Title:", item.title
    print "Link:", item.link
    print "Description", item.description
    
    print "Date:", item.date
    print ">>>", item.date_parsed
    
    print "Author:", item.author
    print ">>", item.author_detail.name
    print ">>", item.author_detail.email
"""