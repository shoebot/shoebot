tuio = ximport("tuio")

size(640, 480)
speed(30)

def setup():
    global tracking
    tracking = tuio.Tracking()

def draw():
    global tracking
    tracking.update()
    fontsize(10)
    for cur in tracking.cursors():
        x = cur.xpos * WIDTH
        y = cur.ypos * HEIGHT
        oval(x, y, 10, 10)
        text(cur, x, y)

def stop():
    global tracking
    tracking.stop()
