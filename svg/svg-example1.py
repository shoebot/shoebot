size(500, 500)

svg = ximport("svg")

# The parse() command will return
# a list of the shapes in the SVG file.
paths = svg.parse(open("svg/flower.svg").read())

background(color(0.1, 0.1, 0.0))

for i in range(10):
    
    transform(mode=CORNER)
    
    translate(random(50, 200), random(50, 200))
    scale(random(0.4, 1.5))
    rotate(degrees=random(60))

    fill(1,0.2,0.5,0.1)

    for path in paths:
        # Use copies of the paths
        # that adhere to the transformations 
        # (translate, scale, rotate) we defined.
        path.fill=(1,0.2,0.5,0.1)
        drawpath(path.copy())
    reset()
        
    
