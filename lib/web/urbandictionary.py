import url
import soap
import re
from cache import Cache
import pickle

def clear_cache():
    Cache("urbandictionary").clear()

class UrbanDictionaryDefinition:
    
    def __init__(self, word, url, description, example, author):

        self.word = word
        self.url = url
        self.description = description
        self.example = example
        self.author = author
        self._parse()
    
    def _parse(self):
        
        """ Strips links from the definition and gathers them in a links property.
        """
        
        p1 = "\[.*?\](.*?)\[\/.*?\]"
        p2 = "\[(.*?)\]"
        self.links = []
        for p in (p1,p2):
            for link in re.findall(p, self.description):
                self.links.append(link)
            self.description = re.sub(p, "\\1", self.description)
            
        self.description = self.description.strip()
    
    def __str__(self):
        
        return self.description

class UrbanDictionaryError(Exception):
    pass

class UrbanDictionary(list):
    
    def __init__(self, q, cached=True):
        
        url = "http://api.urbandictionary.com/soap?wsdl"
        key = "91cf66fb7f14bbf7fb59c7cf5e22155f"

        # Live connect for uncached queries 
        # or queries we do not have in cache.
        cache = Cache("urbandictionary", ".pickle")
        if not cached or not cache.exists(q):
            server = soap.SOAPProxy(url)
            try:
                definitions = server.lookup(key, q)
            except Exception, soap.faultType:
                raise UrbanDictionaryError, "the API is no longer supported"
            data = []
            for item in definitions:
                ubd = UrbanDictionaryDefinition(
                    item.word, item.url, item.definition, item.example, item.author
                )
                self.append(ubd)
                data.append( [item.word, item.word, item.definition, item.example, item.author] )
            # Cache a pickled version of the response.
            if cached:
                data = pickle.dumps(data)
                cache.write(q, data)
        
        # For cached queries,
        # unpack the pickled version in the cache.
        else:
            definitions = cache.read(q)
            definitions = pickle.loads(definitions)
            for item in definitions:
                ubd = UrbanDictionaryDefinition(
                    item[0], item[1], item[2], item[3], item[4]
                )
                self.append(ubd)
            
def search(q, cached=True):
    return UrbanDictionary(q, cached)