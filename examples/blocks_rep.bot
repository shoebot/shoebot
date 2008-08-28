from random import randint

size(600,400)

colormode(HSB)
colorrange(255)

rows = 9
cols = 9

count = 100

def block(x,y,z,hue=0): 
    '''
    draw an isometric square prism; x,y are the coordinates of 
    the BOTTOM-CENTER corner, z is the height
    '''
    #TODO : variables for width+depth instead of fixed value
    
    # no strokes in the inside
    nostroke()
    
    # LEFT FACE
    # first, set the color
    c = color(hue,40,120)
    fill(c)
    # and draw the path
    beginpath(x,y)
    lineto(x-20,y-10)
    lineto(x-20,y-10-z)
    lineto(x,y-z)
    endpath()

    # RIGHT FACE
    c = color(hue,40,80)
    fill(c)
    beginpath(x,y)
    lineto(x+20,y-10)
    lineto(x+20,y-10-z)
    lineto(x,y-z)
    endpath()

    # TOP FACE
    c = color(hue,40,40)
    fill(c)
    beginpath(x,y-z)
    lineto(x+20,y-10-z)
    lineto(x,y-20-z)
    lineto(x-20,y-10-z)
    endpath()

    # CONTOUR
    # now, we'll make a stroke around the faces
    # set the color
    c = color(hue,40,20)
    # set the stroke
    stroke(c)
    # and unset fill
    nofill()
    # draw the path
    beginpath(x,y)
    lineto(x-20,y-10)
    lineto(x-20,y-10-z)
    lineto(x,y-20-z)
    lineto(x+20,y-10-z)
    lineto(x+20,y-10)
    endpath()

def setup():
    # white background
    background(1,1,1)

def draw():
    global count
    background(1,1,1)

    # and draw the blocks
    for x,y in grid(rows,cols,100,100):
        # height of each block is determined by x,y coordinates
        z = (x+y)/25 + randint(-10,10)
        # draw it
        block(x,y,z,hue=randint(0,255))
    
    snapshot("snap" + str(count) + ".png")
    count +=1

#translate(100,100)
for i in range(1,101):
    print 'Outputting snapshot ' + str(i) + '....'
    draw()

print "Done!"
