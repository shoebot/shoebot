# Working with URL's.
size(600,600)
background(1,1,1)
transform(CORNER)
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
print web.is_url("http://www.hv-a.com")

# Does the page exist?
print web.url.not_found("http://www.hv-a.com/niente.html")

# Split the URL into different components.
url = web.url.parse("http://www.hv-a.com/index.html")
print "domain:", url.domain
print "page:", url.page

# Retrieve data from the web.
for i in range(35):
    url = "http://www.hv-a.com/images_hv/rotate/rotate.php"
    print web.url.is_image(url)
    img = web.url.retrieve(url)
    #print "download errors:", img.error
    push()
    translate(random(WIDTH),random(HEIGHT))
    transform(CENTER)
    rotate(random(360))
    image(None, 0, 0, 200,80, data=img.data)
    pop()