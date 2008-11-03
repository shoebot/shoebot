from url import URLAccumulator
from urllib import quote
from cache import Cache
from xml.dom import minidom
import colorsys

def clear_cache():
    Cache("kuler").clear()

### COLOR MODELS #####################################################################################

def cmyk_to_rgb(c, m, y, k):

    r = 1.0 - (c+k)
    g = 1.0 - (m+k)
    b = 1.0 - (y+k)
    
    return r, g, b
    
def hex_to_rgb(hex):
    
    hex = hex.lstrip("#")
    if len(hex) < 6:
        hex += hex[-1] * (6-len(hex))
        
    r, g, b = hex[0:2], hex[2:4], hex[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    
    return (r/255.0, g/255.0, b/255.0)
    
def lab_to_rgb(l, a, b):
    
    """ Converts CIE Lab to RGB components.
    
    First we have to convert to XYZ color space.
    Conversion involves using a white point,
    in this case D65 which represents daylight illumination.
    
    Algorithms adopted from:
    http://www.easyrgb.com/math.php
    
    """
    
    y = (l+16) / 116.0
    x = a/500.0 + y
    z = y - b/200.0
    v = [x,y,z]
    for i in range(3):
        if pow(v[i],3) > 0.008856: 
            v[i] = pow(v[i],3)
        else: 
            v[i] = (v[i]-16/116.0) / 7.787

    # Observer = 2, Illuminant = D65
    x = v[0] * 95.047/100
    y = v[1] * 100.0/100
    z = v[2] * 108.883/100

    r = x * 3.2406 + y *-1.5372 + z *-0.4986
    g = x *-0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y *-0.2040 + z * 1.0570
    v = [r,g,b]
    for i in range(3):
        if v[i] > 0.0031308:
            v[i] = 1.055 * pow(v[i], 1/2.4) - 0.055
        else:
            v[i] = 12.92 * v[i]

    #r, g, b = v[0]*255, v[1]*255, v[2]*255
    r, g, b = v[0], v[1], v[2]
    return r, g, b

### KULER THEME ######################################################################################
        
class KulerTheme(list):
    
    def __init__(self):
        
        self.id = 0
        self.author = u""
        self.label = u""
        self.tags = []
    
    def _darkest(self):
        
        """ Returns the darkest swatch.
        
        Knowing the contract between a light and a dark swatch
        can help us decide how to display readable typography.
        
        """
        
        rgb, n = (1.0, 1.0, 1.0), 3.0
        for r,g,b in self:
            if r+g+b < n:
                rgb, n = (r,g,b), r+g+b
        
        return rgb
    
    darkest = property(_darkest)
        
    def _lightest(self):
        
        """ Returns the lightest swatch.
        """
        
        rgb, n = (0.0, 0.0, 0.0), 0.0
        for r,g,b in self:
            if r+g+b > n:
                rgb, n = (r,g,b), r+g+b
        
        return rgb
    
    lightest = property(_lightest)

    def draw(self, x, y, w=40, h=40):
        
        try: from web import _ctx
        except: pass
        
        from nodebox.graphics import RGB
        for r,g,b in self:
            _ctx.colormode(RGB)
            _ctx.fill(r,g,b)
            _ctx.rect(x, y, w, h)
            x += w
            
### KULER ############################################################################################

class Kuler(list, URLAccumulator):
    
    def __init__(self, q, page=0, wait=10, asynchronous=False, cached=True):
        
        """ Parses color themes from Adobe Kuler.
        
        Valid queries are "popular", "rating", 
        a theme id as an integer, or a search string.
        
        """
        
        if cached: 
            cache = "kuler"
        else:
            cache = None
        
        # Requests for search, popular, rating and id have different url.
        url  = "http://kuler.adobe.com/kuler/services/"
        self.id_string = url + "theme/get.cfm?themeId="
        if isinstance(q, int):
            url  = self.id_string + str(q)  
        elif q in ["popular", "rating"]:
            url += "theme/getList.cfm?listType="+q
            url += "&startIndex="+str(page*30)+"&itemsPerPage=30"
        else:
            url += "search/get.cfm?searchQuery="+quote(q)
            url += "&startIndex="+str(page*30)+"&itemsPerPage=30"
        
        # Refresh cached results every day
        # for highest rating or popular requests.
        if q in ["popular", "rating"]:
            if cached and Cache(cache).age(url) > 0:
                Cache(cache).remove(url)
            
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, type=".xml", throttle=3)

    def load(self, data):
        
        if data == "": return
        if data.find("<recordCount>0</recordCount>") > 0: return
        dom = minidom.parseString(data)
        for theme in dom.getElementsByTagName("theme"):
            try:
                self.append(self.parse_theme(theme))
            except:
                pass
                
    def parse_tag(self, xml, tag):
    
        return xml.getElementsByTagName(tag)[0].childNodes[0].nodeValue

    def parse_theme(self, xml):
        
        """ Parses a theme from XML returned by Kuler.
        
        Gets the theme's id, label and swatches.
        All of the swatches are converted to RGB.
        If we have a full description for a theme id in cache,
        parse that to get tags associated with the theme.
        
        """

        kt = KulerTheme()        
        kt.author = xml.getElementsByTagName("author")[0]
        kt.author = kt.author.childNodes[1].childNodes[0].nodeValue
        kt.id = int(self.parse_tag(xml, "id"))
        kt.label = self.parse_tag(xml, "label")
        mode = self.parse_tag(xml, "mode")
        
        for swatch in xml.getElementsByTagName("swatch"):
            
            c1 = float(self.parse_tag(swatch, "c1"))
            c2 = float(self.parse_tag(swatch, "c2"))
            c3 = float(self.parse_tag(swatch, "c3"))
            c4 = float(self.parse_tag(swatch, "c4"))
            
            if mode == "rgb":
                kt.append((c1,c2,c3))
            if mode == "cmyk":   
                kt.append(cmyk_to_rgb(c1,c2,c3,c4))
            if mode == "hsv":
                kt.append(colorsys.hsv_to_rgb(c1,c2,c3))
            if mode == "hex":
                kt.append(hex_to_rgb(c1))
            if mode == "lab":
                kt.append(lab_to_rgb(c1,c2,c3))
        
        # If we have the full theme in cache,
        # parse tags from it.
        if self._cache.exists(self.id_string + str(kt.id)):
            xml = self._cache.read(self.id_string + str(kt.id))
            xml = minidom.parseString(xml)
        for tags in xml.getElementsByTagName("tag"):
            tags = self.parse_tag(tags, "label")
            tags = tags.split(" ")
            kt.tags.extend(tags)
        
        return kt

######################################################################################################
    
def search_by_popularity(page=0, wait=10, asynchronous=False, cached=True):
    return Kuler("popular", page, wait, asynchronous, cached)

def search_by_rating(page=0, wait=10, asynchronous=False, cached=True):
    return Kuler("rating", page, wait, asynchronous, cached)
        
def search(q, page=0, wait=10, asynchronous=False, cached=True):
    return Kuler(str(q), page, wait, asynchronous, cached)
    
def search_by_id(id, page=0, wait=10, asynchronous=False, cached=True):
    return Kuler(int(id), page, wait, asynchronous, cached) 

######################################################################################################

def preview(theme):
    
    try: from web import _ctx
    except: pass
    
    # Use the darkest swatch as background.
    r,g,b = theme.darkest
    c = _ctx.color(r, g, b)
    c.brightness *= 0.5
    c.brightness = max(0.1, c.brightness)
    c.brightness = 0.15
    _ctx.background(c)
    #_ctx.background(0.1)
    
    from random import random, choice
    for i in range(100):
        r,g,b = choice(theme)
        _ctx.fill(r,g,b)
        r,g,b = choice(theme)
        _ctx.stroke(r,g,b)
        _ctx.strokewidth(random()*30)
        r = random()*100
        _ctx.oval(random()*400, random()*400, r, r)

    # Draw swatches.
    _ctx.nostroke()
    theme.draw(20, 480)    

    # Theme info colored in the lightest swatch.
    r,g,b = theme.lightest
    _ctx.fontsize(18)
    _ctx.fill(r,g,b)
    _ctx.text(theme.label + u" | " + str(theme.id), 20, 540)
    _ctx.fontsize(_ctx.fontsize()/2)
    _ctx.text(", ".join(theme.tags), 20, 555, width=400)

#size(500, 650)
#themes = search("rating")
##for theme in themes[:10]: Kuler(theme.id)
#theme = themes[0]
#preview(theme)