# Cornu - last updated for NodeBox 1.9.3
# Cornu curves from Raph Levien.
# Cornu-to-Bezier code by Mark Meyer.
# The code is from http://casper.ghostscript.com/~raph/
# You can download Raph's curve editor from http://www.levien.com/spiro/.

from math import *

### CORNU ############################################################################################

# fit arc to pts (0, 0), (x, y), and (1, 0), return th tangent to
# arc at (x, y)
def fit_arc(x, y):
    th = atan2(y - 2 * x * y, y * y + x - x * x)
    return th

# find thetas tangent to path using local cspline logic
def local_ths(path, closed):
    if closed:
        result = []
    else:
        result = [0]
    for i in range(1 - closed, len(path) - 1 + closed):
        x0, y0 = path[(i + len(path) - 1) % len(path)]
        x1, y1 = path[i]
        x2, y2 = path[(i + 1) % len(path)]
        dx = x2 - x0
        dy = y2 - y0
        ir2 = dx * dx + dy * dy
        x = ((x1 - x0) * dx + (y1 - y0) * dy) / ir2
        y = ((y1 - y0) * dx - (x1 - x0) * dy) / ir2
        th = fit_arc(x, y) + atan2(dy, dx)
        result.append(th)
    if not closed:
        result.append(0)
    boundary_ths(path, result, closed)
    return result

# set the endpoint thetas so endpoint curves are circular arcs
def boundary_ths(path, ths, closed):
    if not closed:
        first_th = 2 * atan2(path[1][1] - path[0][1], path[1][0] - path[0][0]) - ths[1]
        ths[0] = first_th
        last_th = 2 * atan2(path[-1][1] - path[-2][1], path[-1][0] - path[-2][0]) - ths[-2]
        ths[-1] = last_th
   
# implementation adapted from cephes
def polevl(x, coef):
    ans = coef[-1]
    for i in range(len(coef) - 2, -1, -1):
        ans = ans * x + coef[i]
    return ans

sn = [
-2.99181919401019853726E3,
 7.08840045257738576863E5,
-6.29741486205862506537E7,
 2.54890880573376359104E9,
-4.42979518059697779103E10,
 3.18016297876567817986E11
]
sn.reverse()
sd = [
 1.00000000000000000000E0,
 2.81376268889994315696E2,
 4.55847810806532581675E4,
 5.17343888770096400730E6,
 4.19320245898111231129E8,
 2.24411795645340920940E10,
 6.07366389490084639049E11
]
sd.reverse()
cn = [
-4.98843114573573548651E-8,
 9.50428062829859605134E-6,
-6.45191435683965050962E-4,
 1.88843319396703850064E-2,
-2.05525900955013891793E-1,
 9.99999999999999998822E-1
]
cn.reverse()
cd = [
 3.99982968972495980367E-12,
 9.15439215774657478799E-10,
 1.25001862479598821474E-7,
 1.22262789024179030997E-5,
 8.68029542941784300606E-4,
 4.12142090722199792936E-2,
 1.00000000000000000118E0
]
cd.reverse()

fn = [
  4.21543555043677546506E-1,
  1.43407919780758885261E-1,
  1.15220955073585758835E-2,
  3.45017939782574027900E-4,
  4.63613749287867322088E-6,
  3.05568983790257605827E-8,
  1.02304514164907233465E-10,
  1.72010743268161828879E-13,
  1.34283276233062758925E-16,
  3.76329711269987889006E-20
]
fn.reverse()
fd = [
  1.00000000000000000000E0,
  7.51586398353378947175E-1,
  1.16888925859191382142E-1,
  6.44051526508858611005E-3,
  1.55934409164153020873E-4,
  1.84627567348930545870E-6,
  1.12699224763999035261E-8,
  3.60140029589371370404E-11,
  5.88754533621578410010E-14,
  4.52001434074129701496E-17,
  1.25443237090011264384E-20
]
fd.reverse()
gn = [
  5.04442073643383265887E-1,
  1.97102833525523411709E-1,
  1.87648584092575249293E-2,
  6.84079380915393090172E-4,
  1.15138826111884280931E-5,
  9.82852443688422223854E-8,
  4.45344415861750144738E-10,
  1.08268041139020870318E-12,
  1.37555460633261799868E-15,
  8.36354435630677421531E-19,
  1.86958710162783235106E-22
]
gn.reverse()
gd = [
  1.00000000000000000000E0,
  1.47495759925128324529E0,
  3.37748989120019970451E-1,
  2.53603741420338795122E-2,
  8.14679107184306179049E-4,
  1.27545075667729118702E-5,
  1.04314589657571990585E-7,
  4.60680728146520428211E-10,
  1.10273215066240270757E-12,
  1.38796531259578871258E-15,
  8.39158816283118707363E-19,
  1.86958710162783236342E-22
]
gd.reverse()


def fresnel(xxa):
    x = abs(xxa)
    x2 = x * x
    if x2 < 2.5625:
        t = x2 * x2
        ss = x * x2 * polevl(t, sn) / polevl(t, sd)
        cc = x * polevl(t, cn) / polevl(t, cd)
    elif x > 36974.0:
        ss = 0.5
        cc = 0.5
    else:
        t = pi * x2
        u = 1.0 / (t * t)
        t = 1.0 / t
        f = 1.0 - u * polevl(u, fn) / polevl(u, fd)
        g = t * polevl(u, gn) / polevl(u, gd)
        t = pi * .5 * x2
        c = cos(t)
        s = sin(t)
        t = pi * x
        cc = 0.5 + (f * s - g * c) / t
        ss = 0.5 - (f * c + g * s) / t
    if xxa < 0:
        cc = -cc
        ss = -ss
    return ss, cc

def eval_cornu(t):
    spio2 = sqrt(pi * .5)
    s, c = fresnel(t / spio2)
    s *= spio2
    c *= spio2
    return s, c

def mod_2pi(th):
    u = th / (2 * pi)
    return 2 * pi * (u - floor(u + 0.5))

def fit_cornu_half(th0, th1):
    if th0 + th1 < 1e-6:
        epsilon = 1e-6
        th0 += epsilon
        th1 += epsilon
    n_iter = 0
    n_iter_max = 21
    est_tm = 0.29112 * (th1 + th0) / sqrt(th1 - th0)
    l = est_tm * .9
    r = est_tm * 2
    while 1:
        t_m = .5 * (l + r)
        dt = (th0 + th1) / (4 * t_m)
        t0 = t_m - dt
        t1 = t_m + dt
        # invariant: t1^2 - t0^2 = th0 + th1
        s0, c0 = eval_cornu(t0)
        s1, c1 = eval_cornu(t1)
        chord_th = atan2(s1 - s0, c1 - c0)
        n_iter += 1
        if n_iter == n_iter_max:
            break
        if mod_2pi(chord_th - t0 * t0 - th0) < 0:
            l = t_m
        else:
            r = t_m
    chordlen = hypot(s1 - s0, c1 - c0)
    k0 = t0 * chordlen
    k1 = t1 * chordlen
    return t0, t1, k0, k1

def fit_cornu(th0, th1):
    if th1 > th0:
        return fit_cornu_half(th0, th1)
    elif th0 > th1:
        t0, t1, k0, k1 = fit_cornu_half(th1, th0)
        # ?
        return (-t1, -t0, -k1, -k0)
    else:
        # it's a circle
        return None

def draw_tan(x, y, th):
    dx = .2 * cos(th)
    dy = .2 * sin(th)
    print_pt(x - dx, y - dy, 'moveto')
    print_pt(x + dx, y + dy, 'lineto')

def draw_cornu(path, ths, closed, flat=False):
    cmd = 'moveto'
    for i in range(len(path) - 1 + closed):
        x0, y0 = path[i]
        x1, y1 = path[(i + 1) % len(path)]
        th = atan2(y1 - y0, x1 - x0)
        th0 = mod_2pi(ths[i] - th)
        th1 = mod_2pi(th - ths[(i + 1) % len(path)])
        flip = -1
        th1 += 1e-6
        if th1 < th0:
            th0, th1 = th1, th0
            flip = 1
        t0, t1, k0, k1 = fit_cornu_half(th0, th1)
        if flip == 1:
            t0, t1 = t1, t0
            k0, k1 = k1, k0
        s0, c0 = eval_cornu(t0)
        s0 *= flip
        s1, c1 = eval_cornu(t1)
        s1 *= flip
        chord_th = atan2(s1 - s0, c1 - c0)
        chordlen = hypot(s1 - s0, c1 - c0)
        rot = th - chord_th
        scale = hypot(y1 - y0, x1 - x0) / chordlen
        cs = scale * cos(rot)
        ss = scale * sin(rot)
        if flat:
            cmd = draw_cornu_flat(x0, y0, t0, t1, s0, c0, flip, cs, ss, cmd)
        else:
            cmd = draw_cornu_bezier(x0, y0, t0, t1, s0, c0, flip, cs, ss, cmd, scale, rot)
    if closed:
        pass # print 'closepath'
    #print 'stroke'

def draw_cornu_flat(x0, y0, t0, t1, s0, c0, flip, cs, ss, cmd):
    
    """ Raph Levien's code draws fast LINETO segments.
    """
    
    for j in range(0, 100):
        t = j * .01
        s, c = eval_cornu(t0 + t * (t1 - t0))
        s *= flip
        s -= s0
        c -= c0
        #print '%', c, s
        x = c * cs - s * ss
        y = s * cs + c * ss
        print_pt(x0 + x, y0 + y, cmd)
        cmd = 'lineto'
    return cmd
    
def draw_cornu_bezier(x0, y0, t0, t1, s0, c0, flip, cs, ss, cmd, scale, rot):

    """ Mark Meyer's code draws elegant CURVETO segments.
    """

    s = None
    for j in range(0, 5):
        # travel along the function two points at a time (at time t and t2)
        # the first time through we'll need to get both points
        # after that we only need the second point because the old second point
        # becomes the new first point
        t = j * .2
        t2 = t+ .2
        
        curvetime = t0 + t * (t1 - t0)
        curvetime2 = t0 + t2 * (t1 - t0)
        Dt = (curvetime2 - curvetime) * scale
        
        if not s:
            # get first point
            # avoid calling this again: the next time though x,y will equal x3, y3
            s, c = eval_cornu(curvetime)
            s *= flip
            s -= s0
            c -= c0
            # calculate derivative of fresnel function at point to get tangent slope
            # just take the integrand of the fresnel function
            dx1 =  cos(pow(curvetime, 2) + (flip * rot))  
            dy1 =  flip * sin(pow(curvetime, 2) + (flip *rot))
            # x,y = first point on function
            x = ((c * cs - s * ss) +x0)
            y = ((s * cs + c * ss) + y0)

        #evaluate the fresnel further along the function to look ahead to the next point
        s2,c2 = eval_cornu(curvetime2) 
        s2 *= flip
        s2 -= s0
        c2 -= c0

        dx2 = cos(pow(curvetime2, 2) + (flip * rot)) 
        dy2 = flip * sin(pow(curvetime2, 2) + (flip * rot))
        # x3, y3 = second point on function
        x3 = ((c2 * cs - s2 * ss)+x0)
        y3 = ((s2 * cs + c2 * ss)+y0)

        # calculate control points
        x1 = (x + ((Dt/3.0) * dx1))
        y1 = (y + ((Dt/3.0) * dy1))   
        x2 = (x3 - ((Dt/3.0) * dx2))
        y2 = (y3 - ((Dt/3.0) * dy2))

        if cmd == 'moveto':
            print_pt(x, y, cmd)
            cmd = 'curveto'
        print_crv(x1, y1, x2, y2, x3, y3)
                    
        dx1, dy1 = dx2, dy2
        x,y = x3, y3
        
    return cmd
    
# update thetas based on cornu splines
def tweak_ths(path, ths, closed):
    dks = []
    for i in range(len(path) - 1 + closed):
        x0, y0 = path[i]
        x1, y1 = path[(i + 1) % len(path)]
        th = atan2(y1 - y0, x1 - x0)
        th0 = mod_2pi(ths[i] - th)
        th1 = mod_2pi(th - ths[(i + 1) % len(path)])
        flip = -1
        th1 += 1e-6
        if th1 < th0:
            th0, th1 = th1, th0
            flip = 1
        t0, t1, k0, k1 = fit_cornu_half(th0, th1)
        if flip == 1:
            t0, t1 = t1, t0
            k0, k1 = k1, k0
        s0, c0 = eval_cornu(t0)
        s1, c1 = eval_cornu(t1)
        chordlen = hypot(s1 - s0, c1 - c0)
        scale = 1 / hypot(y1 - y0, x1 - x0)
        k0 *= scale
        k1 *= scale
        if i > 0:
            dk = k0 - last_k1
            dks.append(dk)
        else:
            first_k0 = k0
        last_k1 = k1
    if closed:
        dks.append(first_k0 - last_k1)
    for i in range(len(dks)):
        x0, y0 = path[i]
        x1, y1 = path[(i + 1) % len(path)]
        x2, y2 = path[(i + 2) % len(path)]
        chord1 = hypot(x1 - x0, y1 - y0)
        chord2 = hypot(x2 - x1, y2 - y1)
        ths[(i + 1) % len(path)] -= .5 * (dks[i] / (chord1 + chord2))

def csinterp(t0, t1, u):
    if u == 0: return (0, 0)
    elif u == 1: return (1, 0)
    c = cos(u * pi * 0.5)
    s = sin(u * pi * 0.5)

    #sigmoid interpolant:
    tau = t0 * c * c + t1 * s * s

    #linear interpolant:
    #tau = t0 * (1 - u) + t1 * u + 1e-9

    f = sin(u * tau) / sin(tau)
    ph = (1 - u) * tau
    return (f * cos(ph), f * sin(ph))

def draw_cspline(path, ths):
    cmd = 'moveto'
    for i in range(len(path) - 1):
        x0, y0 = path[i]
        x1, y1 = path[i + 1]
        th = atan2(y1 - y0, x1 - x0)
        th0 = mod_2pi(ths[i] - th)
        th1 = mod_2pi(th - ths[i + 1])
        scale = hypot(y1 - y0, x1 - x0)
        rot = th
        cs = scale * cos(rot)
        ss = scale * sin(rot)
        for j in range(0, 100):
            t = j * .01
            c, s = csinterp(th0, th1, t)
            x = c * cs - s * ss
            y = s * cs + c * ss
            print_pt(x0 + x, y0 + y, cmd)
            cmd = 'lineto'

### NODEBOX BINDINGS #################################################################################

def print_pt(x, y, cmd):
    x = 100 * x
    y = 100 * y
    if (cmd == 'moveto'):        
        _ctx.moveto(x, y)
    elif (cmd == 'lineto'):
        _ctx.lineto(x, y)
    else:
        print cmd, x, y

def print_crv(x1, y1, x2, y2, x3, y3):
    x1 *= 100
    y1 *= 100
    x2 *= 100
    y2 *= 100
    x3 *= 100
    y3 *= 100
    _ctx.curveto(x1, y1, x2, y2, x3, y3)

def dot_pt(x, y):
    _ctx.oval(x-3,y-3, 6, 6) 

def relativise(path):

    for i in range(len(path)):
        x, y = path[i]
        x *= 0.01 * _ctx.WIDTH
        y *= 0.01 * _ctx.HEIGHT
        
        #Points on the path that have identical coordinates
        #generate a ZeroDivisionError
        for point in path:
            if (x,y) == point:
                x += 0.0000000001
                y += 0.0000000001
        
        path[i] = (x,y)
        
    return path
    
def path(points, close=False, tweaks=20, flat=False, draw=False, helper=False):

    # To make sure we don't change the original, make a copy of the 
    # given points
    points = list(points)

    points = relativise(points)
        
    ths = local_ths(points, close)
    for i in range(tweaks):
        boundary_ths(points, ths, close)
        tweak_ths(points, ths, close)
    boundary_ths(points, ths, close)

    _ctx.autoclosepath(False)
    _ctx.beginpath()
    draw_cornu(points, ths, close, flat)
    p =  _ctx.endpath(draw=draw)

    #beginpath()
    #draw_cspline(path, ths)
    #endpath()

    if helper:
        _ctx.beginpath()
        for i in range(len(points)):
            x, y = points[i]
            draw_tan(x, y, ths[i])
        _ctx.endpath()
        for x,y in points:
            dot_pt(x*100,y*100)
    
    return p
            
def drawpath(p, close=False, tweaks=20, points=False, flat=False):
    
    path(p, close, tweaks, flat, draw=True, helper=points)

### PSYCO SPECIALIZATION #############################################################################

try:
    import psyco
    for f in [
        fit_arc, local_ths, boundary_ths, polevl, fresnel, eval_cornu, 
        mod_2pi, fit_cornu_half, fit_cornu, draw_tan, draw_cornu, 
        draw_cornu_flat, draw_cornu_bezier,
        tweak_ths, csinterp, draw_cspline, print_pt, relativise
        ]:
        psyco.bind(f)
    #print "using psyco"
except:
    pass
