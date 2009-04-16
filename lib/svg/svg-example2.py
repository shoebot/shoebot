# SVG as layers in Core Image.

size(500, 500)

try:
    svg = ximport("svg")
except:
    svg = ximport("__init__")
    reload(svg)

# We'll need the Core Image library.
coreimage = ximport("coreimage")

canvas = coreimage.canvas(WIDTH, HEIGHT)
canvas.append(color(0.1, 0, 0.1))

paths = svg.parse(open("flower.svg").read(), cached=True)
for path in paths:    
    l = canvas.append(
        path, 
        fill=color(0,0), 
        stroke=color(0.5, random(0.5), random()), 
        strokewidth=0.5
    )
    
    # The only hassle is placing the individual paths
    # on top of each other like they appeared in the SVG.
    # By default, Core Image places each new layer in the center of the canvas.
    # We'll use a combination of corner-mode transformation
    # and the x, y position in the source vector path 
    # to determine the position of the image layer.
    (x, y), (w, h) = path.bounds
    l.origin_top_left()
    l.x += x
    l.y += y

    l.brightness = 0.5
    l.filter("zoomblur", amount=40)
    l.filter("twirl", angle=360)

# Move the layers around as a group.
# We exclude the bottom layer in the canvas, which is the fill background.
for layer in canvas:
    if layer.index > 0:
        layer.x -= 100
        layer.y -= 110

canvas.draw()
