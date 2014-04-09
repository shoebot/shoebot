# Retrieve images from MorgueFile.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

q = "cloud"
img = choice(web.morguefile.search(q))

print img

# A morgueFile image in the list has 
# a number of methods and properties.
# The download() method caches the image locally 
# and returns the path to the file.
img = img.download()
image(img, 0, 0)