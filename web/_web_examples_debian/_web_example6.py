# Retrieve images from MorgueFile.

import web

q = "cloud"
img = web.morguefile.search(q)[0]

print img

# A morgueFile image in the list has 
# a number of methods and properties.
# The download() method caches the image locally 
# and returns the path to the file.
img = img.download()

