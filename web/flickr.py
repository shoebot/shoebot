from urllib import quote_plus
from url import URLAccumulator
from xml.dom.minidom import parseString
import os
from cache import Cache

API_KEY = "787081027f43b0412ba41142d4540480"

def clear_cache():
    Cache("flickr").clear()

### FLICKR IMAGE #####################################################################################

SIZE_SQUARE    = "Square"
SIZE_SMALL     = "Thumbnail"
SIZE_MEDIUM    = "Small"
SIZE_LARGE     = "Medium"
SIZE_XLARGE    = "Original"

def disambiguate_size(size):
    if size == True  : return SIZE_THUMBNAIL
    if size == False : return SIZE_XLARGE
    if size.lower() in ("square", "sq"): 
        return SIZE_SQUARE
    if size.lower() in ("small", "s", "thumbnail", "thumb", "t", "th", "icon"):
        return SIZE_SMALL
    if size.lower() in ("medium", "m"): 
        return SIZE_MEDIUM
    if size.lower() in ("large", "l"): 
        return SIZE_LARGE
    if size.lower() in ("original", "o", "xlarge", "xl", "huge", "wallpaper"): 
        return SIZE_XLARGE
    return size

class FlickrImage(URLAccumulator):
    
    def __init__(self):
        
        self.id        = 0
        self.name      = ""
        self.author    = ""
        self.url       = ""
        self.path      = ""

        # These are just here for consistency
        # with MorgueFileImage objects.
        self.category  = ""
        self.date      = ""
        self.views     = 0
        self.downloads = 0
        
        self._download = None
        
    def __str__(self):
        
        return self.name.encode("utf-8")
        
    def __cmp__(self, other):
        
        return 1
        
    def download(self, size=SIZE_XLARGE, thumbnail=False, wait=60, asynchronous=False):
        
        """ Downloads this image to cache.
        
        Calling the download() method instantiates an asynchronous URLAccumulator
        that will fetch the image's URL from Flickr.
        A second process then downloads the file at the retrieved URL.
        
        Once it is done downloading, this image will have its path property
        set to an image file in the cache.
        
        """
        
        if thumbnail == True: size = SIZE_THUMBNAIL # backwards compatibility
        self._size = disambiguate_size(size)
        self._wait = wait
        self._asynchronous = asynchronous

        url  = "http://api.flickr.com/services/rest/?method=flickr.photos.getSizes"
        url += "&photo_id=" + self.id
        url += "&api_key=" + API_KEY
        URLAccumulator.__init__(self, url, wait, asynchronous, "flickr", ".xml", 2)

        if not asynchronous:
            return self.path
        
    def load(self, data):
        
        # Step one: fetch the image location from the Flickr API.
        if self.url.startswith("http://api.flickr.com"):
            dom = parseString(data)
            for e in dom.getElementsByTagName("size"):
                self.url = e.getAttribute("source")
                label = e.getAttribute("label")
                # We pick the requested size.
                if label == self._size: break
            
            # Step two: we know where the image is located,
            # now start downloading it.
            extension = os.path.basename(self.url)[-4:]
            self._download = URLAccumulator(self.url, self._wait, self._asynchronous, "flickr", extension, 2)
            
    def _done(self):
        
        done = URLAccumulator._done(self)
        if self._download:
            if self._download.done: 
                # Step three: set the path to the cached image.
                self.path = self._download._cache.hash(self._download.url)
            return done and self._download.done
        else:
            return done

    done = property(_done)

### FLICKR SEARCH ####################################################################################

SORT_INTERESTINGNESS = "interestingness-desc"
SORT_RELEVANCE = "relevance"
SORT_DATE = "date-posted-desc"

MATCH_ANY = "any" # any of the supplied keywords
MATCH_ALL = "all" # all of the supplied keywords

def disambiguate_sort(sort):
    if sort.lower().startswith("interest"): 
        return SORT_INTERESTINGNESS
    if sort.lower().startswith("relevan"): 
        return SORT_RELEVANCE
    if sort.lower().startswith("date"): 
        return SORT_DATE
    return sort

class FlickrSearch(list, URLAccumulator):
    
    def __init__(self, q, start=1, count=100, wait=10, asynchronous=False, cached=True, 
                 sort=SORT_RELEVANCE, match=MATCH_ANY):

        try: q = q.encode("utf-8")
        except:
            pass

        if cached: 
            cache = "flickr"
        else:
            cache = None
        
        url  = "http://api.flickr.com/services/rest/?method="
        if q == "recent":
            url += "flickr.photos.getRecent"
        else:
            url += "flickr.photos.search"
        if isinstance(q, (list, tuple)):
            q = [quote_plus(q) for q in q]
            q = ",".join(q)
            url += "&tags=" + quote_plus(q)
            url += "&tag_mode=" + match
        else:
            url += "&text=" + quote_plus(q)
        url += "&page=" + str(start)
        url += "&per_page=" + str(count)
        url += "&sort=" + disambiguate_sort(sort)
        url += "&api_key=" + API_KEY
        
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, ".xml", 1)

    def load(self, data):
        
        if data == "": return
        dom = parseString(data)
        for img in dom.getElementsByTagName("photo"):
            self.append(self._parse_image(img))
            
    def _parse_image(self, xml):
        
        fi = FlickrImage()
        fi.id     = xml.getAttribute("id")
        fi.name   = xml.getAttribute("title")
        fi.author = xml.getAttribute("owner")
        
        return fi

######################################################################################################
 
def recent(start=1, count=100, wait=10, asynchronous=False, cached=True):
    
    return FlickrSearch("recent", start, count, wait, asynchronous, cached)

def search(q, start=1, count=100, wait=10, asynchronous=False, cached=True, 
           sort=SORT_RELEVANCE, match=MATCH_ANY):
    
    return FlickrSearch(q, start, count, wait, asynchronous, cached, sort, match)

#images = search("glacier")
#img = images[0]
#img.download(asynchronous=True)
#while not img.done:
#    sleep(0.1)
#    print "zzz..."
#image(img.path, 0, 0)

