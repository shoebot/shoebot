### CACHE ############################################################################################
# Code for caching XML-queries, HTML, images in subfolders in /cache.
# The filenames are unique MD5-hases.

# Authors: Frederik De Bleser, Tom De Smedt.
# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

import os
import md5
import datetime
import sys
from glob import glob

# For Mac OS X, the cache is stored inside the web library folder.
# For Linux, it is stored in $HOME/.nodebox-web-cache/
if sys.platform.startswith("darwin") \
or sys.platform.startswith("win"):
    CACHE_PATH = os.path.join(os.path.dirname(__file__), "cache", "")
else:
    CACHE_PATH = os.path.join(os.environ['HOME'], ".nodebox-web-cache", "")

class Cache:
    
    def __init__(self, name, type=".xml"):
        
        """ The cache can be used to store data downloads.
        
        All of the data is stored in subfolders of the CACHE_PATH.
        Each filename is hashed to a unique md5 string.
        
        """
        
        self.path = CACHE_PATH+name
        self.type = type
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
    def hash(self, id):
    
        """ Creates a unique filename in the cache for the id.
        """
    
        h = md5.new(id).hexdigest()
        return os.path.join(self.path, h+self.type)

    def write(self, id, data):
    
        f = self.hash(id)
        open(f, "w").write(data)
    
    def read(self, id):
    
        f = self.hash(id)
        if os.path.exists(f):
            return open(f).read()
        else:
            return None

    def exists(self, id):

        f = self.hash(id)
        return os.path.exists(f)
        
    def age(self, id):
        
        """ Returns the age of the cache entry, in days.
        """
        
        f = self.hash(id)
        if os.path.exists(f):
            modified = datetime.datetime.fromtimestamp(os.stat(f)[8])
            age = datetime.datetime.today() - modified
            return age.days
        else:
            return 0
            
    def remove(self, id):
        
        f = self.hash(id)
        if os.path.exists(f):
            os.unlink(f)
            
    def clear(self):
        
        for f in glob(os.path.join(self.path,"*")):
            os.unlink(f)
        
#c = Cache("kuler")
#print c.age("http://kuler.adobe.com/kuler/services/theme/getList.cfm?listType=popular")