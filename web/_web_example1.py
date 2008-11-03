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
import Image
import StringIO

url = "http://www.hv-a.com/images_hv/rotate/rotate.php"
print web.url.is_image(url)
img = web.url.retrieve(url)
im = Image.open(StringIO.StringIO(img.data))
im.show(command="eog")
im.save("temp.png")
print "download errors:", img.error
#image(None, 0, 0, data=im)
#image("temp.png",0,0)