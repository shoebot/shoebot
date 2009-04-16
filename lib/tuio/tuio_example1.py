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
    for obj in tracking.objects():
        x = obj.xpos * WIDTH
        y = obj.ypos * HEIGHT
        rotate(obj.angle)
        rect(x, y, 20, 20)
        reset()
        text(obj, x, y)

def stop():
    global tracking
    tracking.stop()
