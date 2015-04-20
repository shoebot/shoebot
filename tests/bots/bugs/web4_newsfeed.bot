# Reading newsfeeds.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

# Get a random URL from our favorites list.
url = choice(web.newsfeed.favorites.values())

# Parse the newsfeed data into a handy object.
feed = web.newsfeed.parse(url)

# Get the title and the description of the feed.
print feed.title, "|", feed.description

for item in feed.items:
    print "-" * 40
    print "- Title       :", item.title
    print "- Link        :", item.link
    print "- Description :", web.html.plain(item.description)
    print "- Date        :", item.date
    print "- Author      :", item.author

fontsize(10)
text(item.description, 20, 20, width=200)