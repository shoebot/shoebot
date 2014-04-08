# Wikipedia articles.

import web

q = "Finland"
article = web.wikipedia.search(q, language="fi")

# Print the article title.
print article.title

# Get a list of all the links to other articles.
# We can supply these to a new search.
print article.links

# The title of each paragraph
for p in article.paragraphs: 
    print p.title
    #print "-"*40
    #print p

print article.paragraphs[0]

print
print article.references[0]
