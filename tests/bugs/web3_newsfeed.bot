# Querying Yahoo!

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

# Get a list of links for a search query.
links = web.yahoo.search_images("food")
print links

# Retrieve a random image.
img = web.url.retrieve(choice(links))

# We can't always trust the validity of data from the web,
# the site may be down, the image removed, etc.
# If you're going to do a lot of batch operations and
# you don't want the script to halt on an error,
# put your code inside a try/except statement.
try:
    image(None, 0, 0, data=img.data)
except:
    print str(img.error)
    
# An easier command is web.download():
img = web.download(choice(links))
image(None, 0, 200, data=img)