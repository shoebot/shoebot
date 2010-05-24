size(500, 500)

try:
    svg = ximport("svg")
except:
    svg = ximport("__init__")
    reload(svg)

# The parse() command will return
# a list of the shapes in the SVG file.
paths = svg.parse(open("flower.svg").read())

background(color(0.1, 0.1, 0.0))

for i in range(10):
    
    transform(CORNER)
    translate(random(0, 200), random(0, 200))
    scale(random(0.4, 1.6))
    rotate(random(360))

    fill(1, 1, 0.9, 0.1)

    for path in paths:
        # Use copies of the paths
        # that adhere to the transformations 
        # (translate, scale, rotate) we defined.
        drawpath(path.copy())
        
    reset()
