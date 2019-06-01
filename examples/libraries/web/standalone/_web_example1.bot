# Working with URL's.

import web

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
