"""
Shoebot library example, using the Nodebot grammar.

Libraries using ximport get a variable called '_ctx'
which they can use nodebox commands on.


TODO - If we create a 'Shoebot' grammar it should 
provide a better mechanism than '_ctx'
"""

from math import sin

def draw(x, y, color='#fefefe'):
    """
    Draw a daisy at x, y
    """
    # save location, size etc
    _ctx.push()
    
    # save fill and stroke
    _fill =_ctx.fill()
    _stroke = _ctx.stroke()


    # draw stalk
    _ctx.strokewidth(3)
    _ctx.stroke('#3B240B')
    
    _ctx.line(x + (sin(x * 0.1) * 10.0), y + 80, x + sin(_ctx.FRAME * 0.1), y)

    # draw flower
    _ctx.translate(-20, 0)

    # draw petals
    _ctx.fill(color)
    _ctx.nostroke()
    for angle in xrange(0, 360, 45):
        _ctx.rotate(degrees=45)
        _ctx.rect(x, y, 40, 8, 1)

    # draw centre
    _ctx.fill('#F7FE2E')
    _ctx.ellipse(x + 15, y, 10, 10)

    # restore fill and stroke
    _ctx.fill(_fill)
    _ctx.stroke(_stroke)

    # restore location, size etc
    _ctx.pop()


