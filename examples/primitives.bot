'''
Basic primitives example

Taken from the Nodebox test suite.
'''

size(300, 300)
colorrange(255)
background(76,102,51)
fill(186,186,93)

_total_w = 0
def flow(w, h):
    global _total_w
    if _total_w + w*2 >= WIDTH:
        translate(-_total_w, h)
        _total_w = 0 
    else:
        translate(w, 0)
        _total_w += w

x, y = 10, 10
print "drawing first rect"
rect(x, y, 50, 50)
flow(60, 60)
print "drawing round rect"
rect(x, y, 50, 50, 0.6)
flow(60, 60)
print "drawing oval"
oval(x, y, 50, 50)
flow(60, 60)
print "drawing star"
star(x+25, y+25, 20, outer=25, inner=15)
flow(60, 60)
print "drawing arrownormal"
arrow(x+50, y+25, 50)
flow(60, 60)
print "drawing arrowfortyfive"
arrow(x+50, y, 50, type=FORTYFIVE)
flow(60, 60)
print "drawing oval"
oval(x, y, 50, 50)
