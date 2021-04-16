=========
Ball grid
=========

from the Nodebox examples

Use a grid to generate a bubble-like composition.
This example shows that a grid doesn't have to be rigid at all.
It's very easy to breake loose from the coordinates NodeBox
passes you, as is shown here. The trick is to add or subtract
something from the x and y values NodeBox passes on. Here,
we also use random sizes.

.. shoebot::
    :size: 600,600
    :filename: ball_grid.png

    from math import sin, cos

    size(600, 600)

    gridSize = 40

    # Translate a bit to the right and a bit to the bottom to
    # create a margin.
    translate(100, 100)

    startval = random()
    c = random()
    for x, y in grid(10, 10, gridSize, gridSize):
        fill(sin(startval + y * x / 100.0), cos(c), cos(c), random())
        s = random() * gridSize
        oval(x, y, s, s)
        fill(cos(startval + y * x / 100.0), cos(c), cos(c), random())
        deltaX = (random() - 0.5) * 10
        deltaY = (random() - 0.5) * 10
        deltaS = (random() - 0.5) * 200
        oval(x + deltaX, y + deltaY, deltaS, deltaS)
        c += 0.01
