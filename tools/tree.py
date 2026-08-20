# -*- coding: utf-8 -*-
"""The pomegranate tree of the bride's first reference.

Grown recursively rather than drawn limb by limb, so the canopy has the
density of the woven original.  The groups nest the way the tree does,
which means one small turn at the trunk carries through every branch and
the whole canopy moves as one piece — with the outer twigs adding a
little of their own on top."""
import math

class R:
    def __init__(s, seed): s.x = seed
    def f(s):
        s.x = (1103515245 * s.x + 12345) % (1 << 31)
        return s.x / (1 << 31)
    def r(s, a, b): return a + (b - a) * s.f()

rnd = R(25092026)
rad = math.radians
out = []
poms = []
perch = []      # branch tips a bird could plausibly sit on
mark = []       # every point that has to end up inside the frame

DEPTH   = 5
SPREAD  = 28.0      # degrees between the two children
DECAY_L = 0.87
DECAY_W = 0.68
UPRIGHT = 0.24      # how strongly each new branch is pulled back to vertical

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
            u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1])

def tanp(p0, p1, p2, p3, t):
    u = 1 - t
    return math.degrees(math.atan2(
        3*u*u*(p1[1]-p0[1]) + 6*u*t*(p2[1]-p1[1]) + 3*t*t*(p3[1]-p2[1]),
        3*u*u*(p1[0]-p0[0]) + 6*u*t*(p2[0]-p1[0]) + 3*t*t*(p3[0]-p2[0])))

def taper(p0, p1, p2, p3, w0, w1, M=16):
    """Outline a limb instead of stroking it, so it narrows from the butt
    to the tip the way a branch does. t**.7 puts the fastest narrowing at
    the base, which is what gives the trunk its flare."""
    lo, hi = [], []
    for i in range(M + 1):
        t = i / float(M)
        x, y = bez(p0, p1, p2, p3, t)
        a = math.radians(tanp(p0, p1, p2, p3, t))
        nx, ny = -math.sin(a), math.cos(a)
        hw = (w0 + (w1 - w0) * (t ** 0.7)) / 2.0
        lo.append((x + nx * hw, y + ny * hw))
        hi.append((x - nx * hw, y - ny * hw))
    return "M" + " L".join("%.0f %.0f" % p for p in lo + hi[::-1]) + " Z"


def grow(x0, y0, ang, ln, w, depth):
    bend = rnd.r(-24, 24) * (0 if depth >= DEPTH - 1 else 1)
    a_end = ang + bend
    ex = x0 + math.cos(rad(a_end)) * ln
    ey = y0 + math.sin(rad(a_end)) * ln
    p0 = (x0, y0)
    p1 = (x0 + math.cos(rad(ang)) * ln * .42, y0 + math.sin(rad(ang)) * ln * .42)
    p2 = (ex - math.cos(rad(a_end + bend * .8)) * ln * .34,
          ey - math.sin(rad(a_end + bend * .8)) * ln * .34)
    p3 = (ex, ey)

    # Only two orders of branch are actually animated -- the major limbs
    # and the outer sprays. Everything else rides along inside them. Sixty
    # simultaneously animating groups would re-rasterise the whole canopy
    # every frame on a phone; twenty reads the same and costs nothing.
    live = depth in (4, 2)
    amp = 0.55 if depth == 4 else 0.8
    out.append('<g class="%s" style="--a:%.2fdeg;--b:%d;transform-origin:%.0fpx %.0fpx">'
               % ('bough' if live else 'twig', amp, int(rnd.r(0, 12)), x0, y0))
    out.append('<path class="limb" d="%s"/>' % taper(p0, p1, p2, p3, w, w * DECAY_W))

    # foliage on the outer three orders only — the inner limbs stay bare,
    # exactly as they do in the weaving
    if depth <= 3:
        n = 9 if depth <= 2 else 6
        for i in range(n):
            t = .18 + .80 * (i / float(n - 1))
            x, y = bez(p0, p1, p2, p3, t)
            a = tanp(p0, p1, p2, p3, t)
            side = 1 if i % 2 == 0 else -1
            lx, ly = x + rnd.r(-7, 7), y + rnd.r(-7, 7)
            mark.append((lx, ly, 46))
            out.append('<use href="#lf" class="lf" transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)"/>'
                       % (lx, ly, a + side * rnd.r(40, 68), rnd.r(2.1, 2.7)))

    if depth <= 0:
        # not every twig fruits, or the canopy turns solid red and the
        # foliage stops reading at all
        if rnd.f() < .72:
            poms.append((ex, ey, rnd.r(1.45, 1.85), rnd.r(-18, 18)))
            mark.append((ex, ey, 34))
    else:
        # a few hung inside the canopy too, so the fruit is not just a
        # rind of red around the outside
        if depth == 1 and rnd.f() < .45:
            mx, my = bez(p0, p1, p2, p3, rnd.r(.45, .8))
            poms.append((mx, my, rnd.r(1.4, 1.7), rnd.r(-18, 18)))
            mark.append((mx, my, 30))
        if depth in (2, 3):
            perch.append((ex, ey))
        s = SPREAD * (1.0 if depth >= DEPTH - 1 else rnd.r(.82, 1.2))
        # the trunk throws three: two shoulders and a leader. Two alone
        # leaves a hollow up the middle of the canopy.
        for way in ((-1, 0, 1) if depth == DEPTH else (-1, 1)):
            a = a_end + way * s
            a += (-90 - a) * UPRIGHT     # without this the limbs splay
            grow(ex, ey, a, ln * DECAY_L * rnd.r(.76, 1.2), w * DECAY_W, depth - 1)
    out.append('</g>')

BASE = (450.0, 1078.0)
grow(BASE[0], BASE[1], -90, 250, 46, DEPTH)

# the fruit is drawn after the canopy so nothing is buried behind a leaf
for (x, y, sc, t) in poms:
    out.append('<use href="#pg" class="pg" transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)"/>'
               % (x, y, t, sc))

# ── birds, sat on branches the tree actually grew ─────────────────────
def bird(x, y, sc, face, idx):
    return ('<g class="bd" style="--b:%d;transform-origin:%.0fpx %.0fpx">'
            '<use href="#bird" transform="translate(%.0f %.0f) scale(%.2f %.2f)"/></g>'
            % (idx, x, y + 26, x, y, sc * face, sc))

perch.sort(key=lambda p: p[0])
picks = []
for frac in (0.04, 0.24, 0.44, 0.62, 0.80, 0.96):
    cand = perch[min(int(frac * len(perch)), len(perch) - 1)]
    if all(abs(cand[0] - q[0]) > 110 or abs(cand[1] - q[1]) > 130 for q in picks):
        picks.append(cand)
for i, (x, y) in enumerate(picks):
    out.append(bird(x, y - 12, 1.5, 1 if x < BASE[0] else -1, i))
    mark.append((x, y - 12, 60))

# ── fit the whole tree inside the plate ───────────────────────────────
# It is grown, not drawn, so its extent is not known until it exists — and
# it never comes out symmetric. Scaling about the trunk alone would then
# size the whole tree by whichever side happened to reach furthest, which
# is what leaves it small and adrift in the middle of the plate. So allow
# a little sideways shift as well, capped, and let the ground move with it
# so the trunk still stands where the grass is.
xs0 = min(x - r for (x, y, r) in mark); xs1 = max(x + r for (x, y, r) in mark)
ys0 = min(y - r for (x, y, r) in mark)
TOP, HALF, DXMAX = 74.0, 412.0, 74.0

A = max(1.0, xs1 - BASE[0])          # reach to the right of the trunk
B = max(1.0, BASE[0] - xs0)          # reach to the left
dx = HALF * (B - A) / (A + B)        # the shift that balances the two
dx = max(-DXMAX, min(DXMAX, dx))
k = min((HALF - dx) / A, (HALF + dx) / B, (BASE[1] - TOP) / (BASE[1] - ys0))

head = ('<g class="tree-body" transform="translate(%.1f 0) translate(%.1f %.1f) '
        'scale(%.4f) translate(%.1f %.1f)">'
        % (dx, BASE[0], BASE[1], k, -BASE[0], -BASE[1]))

# ── the ground, and who is standing on it ─────────────────────────────
FOOT, SOIL = 450.0, 1080.0
floor = ['<g class="tree-floor" transform="translate(%.1f 0)">' % dx,
         '<path class="grd" fill="none" d="M232 1096C312 1082 382 1078 450 1078s142 4 222 18"/>',
         '<path class="tuft" fill="none" d="M338 1080c4-17 2-29-4-40M348 1080c0-19 6-31 16-40'
         'M358 1080c6-15 16-23 28-25M562 1080c-4-17-2-29 4-40M552 1080c0-19-6-31-16-40'
         'M542 1080c-6-15-16-23-28-25"/>',
         bird(238, 1046, 1.45, 1, 7), bird(676, 1042, 1.4, -1, 8), bird(752, 1056, 1.2, -1, 9),
         '<use href="#groom" class="fig" transform="translate(%.0f %.0f)"/>' % (FOOT - 34, SOIL),
         '<use href="#bride" class="fig" transform="translate(%.0f %.0f)"/>' % (FOOT + 34, SOIL),
         '</g>']

open('tree.svgfrag', 'w').write(head + "\n" + "\n".join(out) + "\n</g>\n" + "\n".join(floor))
print('fit %.3f  dx %+.0f  raw %.0fx%.0f  filled %.0f%% wide %.0f%% tall'
      % (k, dx, xs1 - xs0, BASE[1] - ys0,
         100 * (xs1 - xs0) * k / 900.0, 100 * (BASE[1] - ys0) * k / 1078.0))
