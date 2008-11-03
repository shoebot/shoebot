from url import URLAccumulator
from urllib import quote
from cache import Cache
import simplejson

def clear_cache():
    Cache("colr").clear()

### COLOR MODELS #####################################################################################

def hex_to_rgb(hex):
    
    
    hex = hex.lstrip("#")
    if len(hex) < 6:
        hex += hex[-1] * (6-len(hex))

    r, g, b = hex[0:2], hex[2:4], hex[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    
    return (r/255.0, g/255.0, b/255.0)

### COLR THEME #######################################################################################
        
class ColrTheme(list):
    
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

class Colr(list, URLAccumulator):
    
    def __init__(self, q, page=0, wait=10, asynchronous=False, cached=True):
        
        """ Parses color themes from Adobe Kuler.
        
        Valid queries are "popular", "rating", 
        a theme id as an integer, or a search string.
        
        """
        
        if cached: 
            cache = "colr"
        else:
            cache = None
        
        url  = "http://www.colr.org/json/"
        if isinstance(q, int):
            url += "scheme/" + str(q)  
        elif q in ["latest", "random"]:
            url += "scheme/" + q
        else:
            url += "tag/" + quote(q)
        
        # Refresh cached results every day
        # for latest requests.
        if q == "latest":
            if cached and Cache(cache).age(url) > 0:
                Cache(cache).remove(url)
        if q == "random":
            Cache(cache).remove(url)
            
        URLAccumulator.__init__(self, url, wait, asynchronous, cache, type=".xml", throttle=3)

    def load(self, data):

        data = simplejson.loads(data)
        for theme in data["schemes"]:
            
            ct = ColrTheme()
            ct.id = theme["id"]
            ct.label = theme["id"]
            ct.tags = [x["name"] for x in theme["tags"]]
            
            for clr in theme["colors"]:
                if len(clr) == 3: clr += clr
                ct.append(hex_to_rgb(clr))
                
            self.append(ct)

######################################################################################################
    
def latest(page=0, wait=10, asynchronous=False, cached=True):
    return Colr("latest", page, wait, asynchronous, cached)[0]

def random(page=0, wait=10, asynchronous=False, cached=True):
    return Colr("random", page, wait, asynchronous, cached)[0]
        
def search(q, page=0, wait=10, asynchronous=False, cached=True):
    return Colr(str(q), page, wait, asynchronous, cached)
    
def search_by_id(id, page=0, wait=10, asynchronous=False, cached=True):
    return Colr(int(id), page, wait, asynchronous, cached) 

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

#web = ximport("web")
#size(500, 650)
#themes = search("office")
#theme = themes[0]
#preview(theme)