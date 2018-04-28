### URL ##############################################################################################
# Code for identifying, parsing and retrieving URL's.
# The asynchronous URLAccumulator is subclassed in all other services.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

import os
import socket, urllib, urllib2, urlparse
import thread, time
from warnings import warn

from cache import Cache

### SETTINGS #########################################################################################

USER_AGENT = "NodeBox/1.9.4 +http://nodebox.net"
REFERER = "http://nodebox.net"

### URLERROR #########################################################################################

class URLError(Exception):
    # A fault in the URL, like a missing t in htp://
    def __str__(self): return str(self.__class__)

class URLTimeout(URLError):
    # URL took to long to load.
    def __str__(self): return str(self.__class__)

class HTTPError(URLError):
    # Error on server.
    def __str__(self): return str(self.__class__)

class HTTP401Authentication(HTTPError):
    # URL requires a login and password.
    def __str__(self): return str(self.__class__)

class HTTP403Forbidden(HTTPError):
    # No access to this URL (user-agent?)
    def __str__(self): return str(self.__class__)

class HTTP404NotFound(HTTPError):
    # URL doesn't exist on the internet.
    def __str__(self): return str(self.__class__)

### URLPARSER ########################################################################################

class URLParser:

    def __init__(self, url="", method="get"):

        """ Splits an url string into different parts.

        The parts are:
        protocol, domain, login, username, password, port, path, page, query, anchor.

        The method defaults to get when the url has a query part.
        Setting it to post will submit the query by POST
        when opening the url.

        """

        # If the url is a URLParser, copy POST parameters correctly.
        is_post_urlparser = False
        if isinstance(url, URLParser) and url.method == "post":
            is_post_urlparser = True
            url.method = "get"

        # If the url is a URLParser, use its string representation.
        # See that the original object's method is correctly reset.
        urlstr = str(url)
        if is_post_urlparser: url.method = "post"
        url = urlstr

        # Consider the following url:
        # http://user:pass@example.com:992/animal/bird?species=seagull#wings
        # protocol: http
        # domain: example.com
        url = urlparse.urlsplit(url)
        self.protocol = url[0]
        self.domain = url[1]

        # username: user
        # password: pass
        self.username = ""
        self.password = ""
        if self.domain.find("@") >= 0:
            login = self.domain.split("@")[0]
            if login.find(":") >= 0:
                self.username = login.split(":")[0]
                self.password = login.split(":")[1]
            self.domain = self.domain.split("@")[1]

        # port: 992
        self.port = ""
        if self.domain.find(":") >= 0:
            p = self.domain.split(":")
            if p[1].isdigit():
                self.port = p[1]
                self.domain = p[0]

        # path: /animal/
        # page: bird
        self.path = url[2]
        self.page = ""
        if not self.path.endswith("/"):
            if self.path.find("/") >= 0:
                self.page = self.path.split("/")[-1]
                self.path = self.path[:-len(self.page)]
            else:
                self.page = self.path
                self.path = ""
        self.filename = self.page

        # query: {"species": "seagull"}
        self.query = {}
        self.method = method
        if url[3] != "":
            self.method = "get"
        if is_post_urlparser:
            self.method = "post"
        for param in url[3].split("&"):
            key, value = "", ""
            if param.find("=") >= 0:
                try: (key, value) = param.split("=")
                except:
                    key = param
            else:
                key = param
            if key != "":
                self.query[key] = value

        # anchor: wings
        self.anchor = url[4]

    def __str__(self):

        """ Reforms a url string from the different parts.
        """

        url = ""
        if self.protocol != ""  : url += self.protocol + "://"
        if self.username != ""  : url += self.username + ":" + self.password + "@"
        if self.domain   != ""  : url += self.domain
        if self.port     != ""  : url += ":" + self.port
        if self.path     != ""  : url += self.path
        if self.page     != ""  : url += self.page
        if self.method == "get" and \
           len(self.query) > 0  : url += "?" + urllib.urlencode(self.query)
        if self.anchor   != ""  : url += "#" + self.anchor

        return url

    def _address(self):
        return str(self)
    address = property(_address)

def parse(url):
    return URLParser(url)

def create(url="", method="get"):
    return URLParser(url, method)

#url = parse("http://user:pass@example.com:992/animal/bird?species=seagull#wings")
#print url.domain
#print url.path
#print url.page
#print url

### URL OPENER #######################################################################################

PROXY = None
def set_proxy(host, type="https"):
    global PROXY
    if host != None:
        PROXY = (host, type)
    else:
        PROXY = None

def open(url, wait=10):

    """ Returns a connection to a url which you can read().

    When the wait amount is exceeded, raises a URLTimeout.
    When an error occurs, raises a URLError.
    404 errors specifically return a HTTP404NotFound.

    """

    # If the url is a URLParser, get any POST parameters.
    post = None
    if isinstance(url, URLParser) and url.method == "post":
        post = urllib.urlencode(url.query)

    # If the url is a URLParser (or a YahooResult or something),
    # use its string representation.
    url = str(url)

    # Use urllib instead of urllib2 for local files.
    if os.path.exists(url):
        return urllib.urlopen(url)

    else:
        socket.setdefaulttimeout(wait)
        try:
            #connection = urllib2.urlopen(url, post)
            request = urllib2.Request(url, post, {"User-Agent": USER_AGENT, "Referer": REFERER})
            if PROXY:
                p = urllib2.ProxyHandler({PROXY[1]: PROXY[0]})
                o = urllib2.build_opener(p, urllib2.HTTPHandler)
                urllib2.install_opener(o)
            connection = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            if e.code == 401: raise HTTP401Authentication
            if e.code == 403: raise HTTP403Forbidden
            if e.code == 404: raise HTTP404NotFound
            raise HTTPError
        except urllib2.URLError, e:
            if e.reason[0] == 36: raise URLTimeout
            raise URLError

    return connection

#print open("http://nodebox.net")
#print open("http:/nodebox.net")
#print open("http://ndoebox.net")
#print open("http://nodebox.net/doink")
#print open("url.py").info()
#print open("boink.py").info()
#print open("file://url.py").info()

### URL VALIDATION ###################################################################################

def is_url(url, wait=10):

    """ Returns False when no connection can be opened to the url.
    """

    try: connection = open(url, wait)
    except:
        return False

    return True

def not_found(url, wait=10):

    """ Returns True when the url generates a "404 Not Found" error.
    """

    try: connection = open(url, wait)
    except HTTP404NotFound:
        return True
    except:
        return False

    return False

#url = "http://ndoebox.net"
#print is_url(url)

#print not_found("http://nodebox.net/nonexistent.html")
#print not_found("http://nodebox.net/")

### URL MIMETYPE ###################################################################################

def is_type(url, types=[], wait=10):

    """ Determine the MIME-type of the document behind the url.

    MIME is more reliable than simply checking the document extension.
    Returns True when the MIME-type starts with anything in the list of types.

    """

    # Types can also be a single string for convenience.
    if isinstance(types, str):
        types = [types]

    try: connection = open(url, wait)
    except:
        return False

    type = connection.info()["Content-Type"]
    for t in types:
        if type.startswith(t): return True

    return False

def is_webpage(url, wait=10):
    return is_type(url, "text/html", wait)
is_page = is_webpage
def is_stylesheet(url, wait=10):
    return is_type(url, "text/css", wait)
def is_plaintext(url, wait=10):
    return is_type(url, "text/plain", wait)
def is_pdf(url, wait=10):
    return is_type(url, "application/pdf", wait)
def is_newsfeed(url, wait=10):
    return is_type(url, ["application/rss+xml", "application/atom+xml"], wait)
def is_image(url, wait=10):
    return is_type(url, ["image/gif", "image/jpeg", "image/x-png"], wait)
def is_audio(url, wait=10):
    return is_type(url, ["audio/mpeg", "audio/x-aiff", "audio/x-wav"], wait)
def is_video(url, wait=10):
    return is_type(url, ["video/mpeg", "video/quicktime"], wait)
def is_archive(url, wait=10):
    return is_type(url, ["application/x-stuffit", "application/x-tar", "application/zip"], wait)

#print is_webpage("http://nodebox.net")
#print is_archive("http://nodebox.net/code/data/media/coreimage.zip")

### URLACCUMULATOR ###################################################################################

urlaccumulator_throttle = {}

class URLAccumulator:

    def __init__(self, url, wait=60, asynchronous=False, cache=None, type=".html", throttle=0):

        """ Creates a threaded connection to a url and reads data.

        URLAccumulator can run asynchronously which is useful for animations.
        The done property is set to True when downloading is complete.
        The error attribute contains a URLError exception when no data is found.

        URLAccumulator data can be cached.
        Downloads that resulted in an error will write an empty file to the cache,
        the data property will be an empty string but no error is logged
        when the data is read from the cache in later calls.

        URLAccumulator can be throttled.
        This ensures only a certain amount of requests to a domain
        will happen in a given period of time.

        URLAccumulator data is loaded.
        It has a load() method that is called once when done.

        """

        self.url = url
        self.data = None
        self.redirect = None
        self.error = None

        if cache != None:
            self.cached = True
            self._cache = Cache(cache, type)
        else:
            self.cached = False
            self._cache = None

        self._domain = URLParser(self.url).domain
        self._throttle = throttle
        global urlaccumulator_throttle
        if not self._domain in urlaccumulator_throttle:
            urlaccumulator_throttle[self._domain] = time.time() - self._throttle

        self._start = time.time()
        self._wait = wait
        self._busy = True
        self._loaded = False

        # Synchronous downloads wait until completed,
        # otherwise check the done property.
        thread.start_new_thread(self._retrieve, (self.url,))
        if not asynchronous:
            while not self._done():
                time.sleep(0.1)

    def _queued(self):

        # Throttles live requests:
        # waits until the current time is greater than
        # the time of the last request plus the throttle amount.
        global urlaccumulator_throttle
        if self.cached and self._cache.exists(str(self.url)):
            return False
        elif time.time() < urlaccumulator_throttle[self._domain] + self._throttle:
            return True
        else:
            urlaccumulator_throttle[self._domain] = time.time()
            return False

    def _retrieve(self, url):

        # When the url data is stored in cache, load that.
        # Otherwise, retrieve it from the web.
        if self.cached and self._cache.exists(str(url)):
            self.data = self._cache.read(str(url))
        else:
            try:
                connection = open(url)
                self.data = connection.read()
                self.redirect = connection.geturl()
                if self.redirect == str(url):
                    self.redirect = None
            except Exception, e:
                self.data = u""
                self.error = e

        self._busy = False

    def _done(self):

        # Will continue downloading asynchronously.
        # 1) When the time limit is exceeded, logs a Timeout error.
        # 2) Once uncached data is ready, stores it in cache.
        # 3) Loads the data.
        # 4) Issues a warning when an error occured.
        if (not self._busy or time.time() >= self._start + self._wait) \
        and not self._queued():                                           # 1
            if self.data == None and \
               self.error == None:
                self.data = u""
                self.error = URLTimeout()
                self.load(self.data)
                self._busy = False
            if self.cached and not self._cache.exists(str(self.url)) \
               and self.data != None and self.data != "":                 # 2
                self._cache.write(str(self.url), str(self.data))
            if not self._loaded and self.error == None:                   # 3
                self.load(self.data)
                self._loaded = True
            if self.error != None:                                        # 4
                warn(str(self.error)+" in "+str(self.__class__)+" for "+str(self.url), Warning)
            return True
        else:
            return False

    done = property(_done)

    def load(self, data):

        """ Override this method in subclasses to process downloaded data.
        """

        pass

def retrieve(url, wait=60, asynchronous=False, cache=None, type=".html"):

    ua = URLAccumulator(url, wait, asynchronous, cache, type)
    return ua

#r = retrieve("http://nodebox.net")
#print r.data
#print r.redirect

#url = create("http://api.search.yahoo.com/ContentAnalysisService/V1/termExtraction", method="post")
#url.query["appid"] = "YahooDemo"
#url.query["context"] = "Italian sculptors and painters of the renaissance favored the Virgin Mary for inspiration"
#url.query["query"] = "madonna"
#r = retrieve(url)
#print r.data

#r = retrieve("http://nodebox.net", asynchronous=True)
#while not r.done:
#    print "wait...",
#    time.sleep(0.1)
#print r.redirect



# XXX - should or should we not do quote_plus() somewhere in here?
