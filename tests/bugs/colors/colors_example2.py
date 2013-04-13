import sys

# COLOR LIST FROM PIXELS

try:
    colors = ximport("colors")
except ImportError:
    colors = ximport("__init__")
    reload(colors)
    
size(550, 400)

# A list of colors from image pixels.
COLOR_IMAGE = sys.prefix + "/share/shoebot/lib/colors/sea.jpg"
sea = colors.list(COLOR_IMAGE, n=20)
image(COLOR_IMAGE, 0, 0, width=550)


x = 0
for clr in sea:
    fill(clr)
    rect(x, 0, 27.5, 100)
    x += 27.5
