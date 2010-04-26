### CREDITS ##########################################################################################

# Copyright (c) 2008 Tom De Smedt.
# See LICENSE.txt for details.

__author__    = "Tom De Smedt"
__version__   = "1.9.4.6"
__copyright__ = "Copyright (c) 2008 Tom De Smedt"
__license__   = "GPL"

### NODEBOX WEB LIBRARY #############################################################################

# The NodeBox Web library offers a collection of services to retrieve content from the internet. 
# You can use the library to query Yahoo! for links, images, news and spelling suggestions, 
# to read RSS and Atom newsfeeds, to retrieve articles from Wikipedia, to collect quality images 
# from morgueFile, to get color themes from kuler , to browse through HTML documents, to clean up HTML, 
# to validate URL's, to create GIF images from math equations using mimeTeX, to get ironic word 
# definitions from Urban Dictionary.

# The NodeBox Web library works with a caching mechanism that stores things you download from the web, 
# so they can be retrieved faster the next time. Many of the services also work asynchronously. 
# This means you can use the library in an animation that keeps on running while new content is downloaded 
# in the background.

# The library bundles Leonard Richardson's BeautifulSoup to parse HTM, 
# Mark Pilgrim's Universal Feed Parser for newsfeeds, a connection to John Forkosh's mimeTeX server, 
# Leif K-Brooks entity replace algorithm, Bob Ippolito's simplejson.

# Thanks to Serafeim Zanikolas for maintaining Debian compatibility, Stuart Axon for various patches.

######################################################################################################

import os
import cache
import url
import html
import page
import simplejson
import json # wrapper for simplejson, backward compatibility.

packages = [
    "yahoo", "google", 
    "newsfeed", 
    "wikipedia", 
    "morguefile", "flickr", 
    "kuler", "colr",
    "mimetex", #deprecated
    "mathtex",
    "urbandictionary",
]
for p in packages:
    try: exec("import %s" % p)
    except ImportError:
        pass

def set_proxy(host, type="https"):
    url.set_proxy(host, type)
set_proxy(None)

def is_url(url_, wait=10):
    return url.is_url(url_, wait)

def download(url_, wait=60, cache=None, type=".html"):
    return url.retrieve(url_, wait, False, cache, type).data

def save(url_, path="", wait=60):
    if hasattr(url_, "url"): 
        url_ = url_.url
    if len(path) < 5 or "." not in path[-5:-3]:
        file = url.parse(str(url_)).filename
        path = os.path.join(path, file)
    open(path, "w").write(download(url_, wait))
    return path

def clear_cache():
    page.clear_cache()
    for p in packages:
        try: exec("%s.clear_cache()" % p)
        except NameError:
            pass    

# 1.9.4.6
# cache.py uses hashlib instead of md5 on Python 2.6+
# On Windows, cached files are stored under Documents and Settings\UserName\.nodebox-web-cache.
# Cache files are stored in binary mode to avoid newline issues.
# Fixed support for Morguefile.

# 1.9.4.5
# cache.py closes files after reading and writing.
# This is necessary in Jython.

# 1.9.4.4
# mathTeX deprecates mimeTeX.

# 1.9.4.3
# Flickr accepts Unicode queries.

# 1.9.4.1
# Added set_proxy() command.
# Added Serafeim Zanikolas' patches & examples for Debian.
# Added Serafeim Zanikolas' html=False attribute to WikipediaPage.
    
# 1.9.4
# Added simplejson for improved unicode support.
# Added google.py module.
# Improvements to html.py.
# Morguefile images can be filtered by size.
# Flickr images can be filtered by size.
# Flickr images can be filtered by interestingness/relevance/date/tags.
# Fixed Flickr unicode bug.
# Wikipedia unicode improvements.
# url.URLAccumulator._done() will only load data if no URLError was raised.
# url.parse() has a new .filename attribute (equals .page).
# Handy web.save() command downloads data and saves it to a given path.
# hex_to_rgb() improvement for hex strings shorter than 6 characters.
# Upgraded to BeautifulSoup 3.0.7a