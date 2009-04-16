# Reading newsfeeds.

import web

# Get the first URL from our favorites list.
url = web.newsfeed.favorites.values()[0]

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

print item.description
