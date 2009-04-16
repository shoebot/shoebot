### MIMETEX ##########################################################################################
# Code for connecting to mimeTeX server to convert LaTeX math to images.

# Author: Tom De Smedt.
# Copyright (c) 2007 by Tom De Smedt.
# See LICENSE.txt for details.

from url import URLAccumulator
from urllib import quote
from cache import Cache

def clear_cache():
    Cache("mimetex").clear()

class mimeTeX(URLAccumulator):
    
    """ The mimeTeX server returns a GIF-image for a LaTeX math expression.
    http://www.forkosh.com/mimetex.html
    """
    
    def __init__(self, eq, wait=10, asynchronous=False):
        
        url = "http://www.forkosh.dreamhost.com/mimetex.cgi?"+quote(eq)
        URLAccumulator.__init__(self, url, wait, asynchronous, "mimetex", type=".gif", throttle=1)

    def load(self, data):
        
        # Provide the path to the GIF stored in cache.
        self.image = self._cache.hash(self.url)

def gif(eq):
    
    return mimeTeX(eq).image

#eq = "E = hf = \frac{hc}{\lambda} \,\! "
#image(gif(eq), 10, 10)