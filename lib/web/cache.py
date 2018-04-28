### CACHE ############################################################################################
# Code for caching XML-queries, HTML, images in subfolders in /cache.
# The filenames are unique MD5-hases.

# Authors: Frederik De Bleser, Tom De Smedt.
# Copyright (c) 2007 Tom De Smedt.
# See LICENSE.txt for details.

import os
import datetime
import sys
from glob import glob

try:
    # Python 2.6+
    from hashlib import md5
except:
    # Python 2.5-
    from md5 import new as md5

# For Mac OS X, the cache is stored inside the web library folder.
# For Windows, it is stored in the user's folder (Documents and Settings\UserName\.shoebot-web-cache).
# For Linux, it is stored in $HOME/.shoebot-web-cache/
if sys.platform.startswith("darwin"):
    CACHE_PATH = os.path.join(os.path.dirname(__file__), "cache", "")
elif sys.platform.startswith("win"):
    CACHE_PATH = os.path.join(os.environ["HOMEPATH"], ".shoebot-web-cache", "")
else:
    CACHE_PATH = os.path.join(os.environ["HOME"], ".shoebot-web-cache", "")

class Cache:

    def __init__(self, name, type=".xml"):

        """ The cache can be used to store data downloads.

        All of the data is stored in subfolders of the CACHE_PATH.
        Each filename is hashed to a unique md5 string.

        """

        self.path = os.path.join(CACHE_PATH, name)
        self.type = type

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def hash(self, id):

        """ Creates a unique filename in the cache for the id.
        """

        h = md5(id).hexdigest()
        return os.path.join(self.path, h+self.type)

    def write(self, id, data):

        # Write files using binary mode to avoid extra newlines being inserted.
        f = open(self.hash(id), "wb")
        f.write(data)
        f.close()

    def read(self, id):

        path = self.hash(id)
        if os.path.exists(path):
            f = open(path)
            data = f.read()
            f.close()
            return data
        else:
            return None

    def exists(self, id):

        return os.path.exists(self.hash(id))

    def age(self, id):

        """ Returns the age of the cache entry, in days.
        """

        path = self.hash(id)
        if os.path.exists(path):
            modified = datetime.datetime.fromtimestamp(os.stat(path)[8])
            age = datetime.datetime.today() - modified
            return age.days
        else:
            return 0

    def remove(self, id):

        path = self.hash(id)
        if os.path.exists(path):
            os.unlink(path)

    def clear(self):

        for path in glob(os.path.join(self.path,"*")):
            os.unlink(path)

#c = Cache("kuler")
#print c.age("http://kuler.adobe.com/kuler/services/theme/getList.cfm?listType=popular")
