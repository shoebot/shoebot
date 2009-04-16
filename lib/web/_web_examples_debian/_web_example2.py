# Parsing web pages.

import web

url = "http://nodebox.net"
print web.url.is_webpage(url)

# Retrieve the data from the web page and put it in an easy object.
html = web.page.parse(url)

# The actual URL you are redirected to.
# This will be None when the page is retrieved from cache.
print html.redirect

# Get the web page title.
print html.title

# Get all the links, including internal links in the same site.
print html.links(external=False)

# Browse through the HTML tree, find <div id="content">,
# strip tags from it and print out the contents.
content = html.find(id="content")
web.html.plain(content)
