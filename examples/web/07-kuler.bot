# Color themes from Kuler.

try:
    web = ximport("web")
except:
    web = ximport("__init__")
    reload(web)

# Get the current most popular themes.
themes = web.kuler.search_by_popularity()

# Display colors from the first theme.
for i in range(100):
    for r, g, b in themes[0]:
        fill(r, g, b, 0.8)
        rotate(random(360))
        s = random(50) + 10
        oval(random(300), random(300), s, s)