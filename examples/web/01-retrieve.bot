# Working with URL's.

try:
    # This is the statement you normally use.
    # You can also do "import web" outside of NodeBox.
    web = ximport("web")
except:
    # But since these examples are "inside" the library
    # we may need to try something different when
    # the library is not located in /Application Support
    web = ximport("__init__")
    reload(web)

# Is this a valid URL?
print web.is_url("http://nodebox.net")

# Does the page exist?
print web.url.not_found("http://nodebox.net/nothing")

# Split the URL into different components.
url = web.url.parse("http://nodebox.net/code/index.php/Home")
print "domain:", url.domain
print "page:", url.page

# Retrieve data from the web.
url = "http://nodebox.net/code/data/media/header.jpg"
print web.url.is_image(url)
img = web.url.retrieve(url)
print "download errors:", img.error
image(None, 0, 0, data=img.data)