Blines and circloids
====================

by Tom de Smedt <https://www.nodebox.net/code/index.php/Blines_and_Circloids>

.. shoebot::
    :size: 550,550
    :filename: blines.png

    # You'll need the Boids and Cornu libraries.
    boids = ximport("boids")
    cornu = ximport("cornu")

    size(550, 550)
    background(0.1, 0.1, 0.0)
    nofill()

    flock = boids.flock(10, 0, 0, WIDTH, HEIGHT)

    n = 70
    for i in range(n):

        flock.update(shuffled=False)

        # Each flying boid is a point.
        points = []
        for boid in flock:
            points.append((boid.x, boid.y))

        # Relativise points for Cornu.
        for i in range(len(points)):
            x, y = points[i]
            x /= 1.0 * WIDTH
            y /= 1.0 * HEIGHT
            points[i] = (x, y)

        t = float(i) / n
        stroke(0.9, 0.9, 4 * t, 0.6 * t)
        cornu.drawpath(points, tweaks=0)
