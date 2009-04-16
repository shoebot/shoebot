# Definitions from the Urban Dictionary.

import web

definitions = web.urbandictionary.search("human")
for i, d in enumerate(definitions):
    print "%d: %s" % (i, d)
