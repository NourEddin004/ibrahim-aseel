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

# Not the wedding date any more. The tree is grown, so how squarely it
# comes out is down to the seed, and the date's seed grew one that reached
# 150 units further right than left — which the fit then paid for, since it
# has to scale by the longest arm and the trunk may not leave the centre
# line. Twenty seeds were grown; this one comes out 8 units off symmetric
# and fills the plate 91% by 98%. The date's grew to 74% by 100%.
rnd = R(13)
twig_n = [0]
rad = math.radians
out = []
poms = []
perch = []      # branch tips a bird could plausibly sit on
mark = []       # every point that has to end up inside the frame

# Shaped from the photograph rather than from the weaving: a real
# pomegranate is a broad low dome on a short trunk that forks early, not
# a vase. The canopy is wider than it is tall, its widest point sits below
# the middle, and the outer branches arch over and droop at the tips.
DEPTH   = 5
SPREAD  = 32.0      # degrees between the two children
DECAY_L = 0.862
DECAY_W = 0.66
UPRIGHT = 0.18      # near zero: the pull to vertical is what made a column
DROOP   = 13.0      # degrees the outer orders bend back down, per order

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
    # the tips arch over: the further out, the more the branch falls away
    # from where it set off, which is what stops the crown looking blown
    if depth <= 2:
        bend += DROOP * (3 - depth) * (0.55 + 0.45 * rnd.f())
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
    if live:
        cls = 'bough'
    else:
        # only every other twig is animated: half the canopy moving is
        # indistinguishable from all of it, and costs half as much
        twig_n[0] += 1
        cls = 'twig twig--w' if twig_n[0] % 2 else 'twig'
    out.append('<g class="%s" style="--a:%.2fdeg;--b:%d;transform-origin:%.0fpx %.0fpx">'
               % (cls, amp, int(rnd.r(0, 12)), x0, y0))
    out.append('<path class="limb" d="%s"/>' % taper(p0, p1, p2, p3, w, w * DECAY_W))

    # foliage on the outer three orders only — the inner limbs stay bare,
    # exactly as they do in the weaving
    if depth <= 4:
        # small leaves, and many of them. The photograph's canopy is a mass
        # you cannot see the branches through; six big leaves a limb read
        # as a diagram of a tree instead.
        # depth 0 used to get none, which is why the outermost twigs came
        # out as bare stems with a pomegranate on the end. Those are the
        # ones the eye sees against the navy.
        n = (11, 18, 21, 20, 13)[depth]
        for i in range(n):
            t = .12 + .86 * (i / float(n - 1))
            x, y = bez(p0, p1, p2, p3, t)
            a = tanp(p0, p1, p2, p3, t)
            side = 1 if i % 2 == 0 else -1
            # scattered off the stem, not lined up along it: what makes a
            # canopy a mass is leaves filling the space between branches
            lx, ly = x + rnd.r(-19, 19), y + rnd.r(-17, 17)
            mark.append((lx, ly, 30))
            out.append('<use href="#lf" class="lf" transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)"/>'
                       % (lx, ly, a + side * rnd.r(28, 84), rnd.r(1.45, 2.15)))

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

# The plate used to be 900 x 1150 — a portrait frame — and a real
# pomegranate is a broad dome, so the fit was always limited by width and
# left the top third of the navy empty. The field is near-square now,
# which is also the shape the photograph is, and the tree fills it.
VB_H = 980.0
BASE = (450.0, 908.0)
# a short bole that forks low, the way the photograph's does
grow(BASE[0], BASE[1], -90, 225, 44, DEPTH)

# the fruit is drawn after the canopy so nothing is buried behind a leaf
# each one in a wrapper of its own, because the <use> carries a transform
# attribute and a CSS animation on the same element would replace it
for i, (x, y, sc, t) in enumerate(poms):
    out.append('<g class="fruit" style="--i:%d">'
               '<use href="#pg" class="pg" transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)"/>'
               '</g>' % (i, x, y, t, sc))

# ── birds, sat on branches the tree actually grew ─────────────────────
def bird(x, y, sc, face, idx, order, ground=False):
    """--ex/--ey is the offset the bird comes in from: off its own nearest
    edge, and from above, since a bird descends onto a perch. The canopy
    birds live inside .tree-body, which the fit scales down, so theirs
    have to be bigger numbers to clear the same frame."""
    away = -1 if x < BASE[0] else 1
    reach = 330 if ground else 520
    rise = 300 if ground else 215
    ex = away * (reach + rnd.r(-30, 40))
    ey = -(rise + rnd.r(-25, 45))
    er = away * rnd.r(9, 17)
    # the <use> sits inside a group of its own so the wingbeat and the
    # flight path can be two simple animations instead of one keyframe
    # list carrying both
    return ('<g class="bd" style="--b:%d;--ex:%.0fpx;--ey:%.0fpx;--er:%.0fdeg;--o:%d;'
            'transform-origin:%.0fpx %.0fpx">'
            '<g class="wing">'
            '<use href="#bird" transform="translate(%.0f %.0f) scale(%.2f %.2f)"/>'
            '</g></g>'
            % (idx, ex, ey, er, order, x, y + 26, x, y, sc * face, sc))

perch.sort(key=lambda p: p[0])
picks = []
for frac in (0.04, 0.24, 0.44, 0.62, 0.80, 0.96):
    cand = perch[min(int(frac * len(perch)), len(perch) - 1)]
    if all(abs(cand[0] - q[0]) > 110 or abs(cand[1] - q[1]) > 130 for q in picks):
        picks.append(cand)
# the canopy lands first, then the grass — so the eye is taken up into
# the tree and brought back down to the two of them
for i, (x, y) in enumerate(picks):
    out.append(bird(x, y - 12, 1.5, 1 if x < BASE[0] else -1, i, i))
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
# DXMAX is 0 deliberately. Balancing the canopy's bounding box costs the
# trunk its place on the centre line, and the trunk — with the couple
# standing at its foot — is what a viewer reads the plate's axis from.
# A canopy a few units heavier on one side is invisible; a trunk three
# pixels off the middle of a symmetrical frame is not.
TOP, HALF, DXMAX = 62.0, 414.0, 0.0

A = max(1.0, xs1 - BASE[0])          # reach to the right of the trunk
B = max(1.0, BASE[0] - xs0)          # reach to the left
dx = HALF * (B - A) / (A + B)        # the shift that balances the two
dx = max(-DXMAX, min(DXMAX, dx))
k = min((HALF - dx) / A, (HALF + dx) / B, (BASE[1] - TOP) / (BASE[1] - ys0))

# .gust is the one group the whole canopy leans in — the wind is a
# rotation on this, plus a sway on each bough inside it. Animating the
# twigs as well meant forty groups re-rasterising their own subtree every
# frame, which is what made it stutter.
head = ('<g class="gust"><g class="tree-body" transform="translate(%.1f 0) translate(%.1f %.1f) '
        'scale(%.4f) translate(%.1f %.1f)">'
        % (dx, BASE[0], BASE[1], k, -BASE[0], -BASE[1]))

# ── the ground, and who is standing on it ─────────────────────────────
# All of it hangs off BASE, so moving the trunk moves the grass, the
# birds standing in it and the couple with one number.
FOOT, SOIL = 450.0, BASE[1] + 2
G = BASE[1]                       # the line the trunk stands on
floor = ['<g class="tree-floor" transform="translate(%.1f 0)">' % dx,
         '<path class="grd" fill="none" d="M232 %.0fC312 %.0f 382 %.0f 450 %.0fs142 4 222 18"/>'
         % (G + 18, G + 4, G, G),
         '<path class="tuft" fill="none" d="'
         'M338 %(g)sc4-17 2-29-4-40M348 %(g)sc0-19 6-31 16-40M358 %(g)sc6-15 16-23 28-25'
         'M562 %(g)sc-4-17-2-29 4-40M552 %(g)sc0-19-6-31-16-40M542 %(g)sc-6-15-16-23-28-25"/>'
         % {'g': '%.0f' % (G + 2)},
         bird(238, G - 32, 1.45, 1, 7, len(picks), True),
         bird(676, G - 36, 1.4, -1, 8, len(picks) + 1, True),
         bird(752, G - 22, 1.2, -1, 9, len(picks) + 2, True),
         '<use href="#groom" class="fig" transform="translate(%.0f %.0f)"/>' % (FOOT - 34, SOIL),
         '<use href="#bride" class="fig" transform="translate(%.0f %.0f)"/>' % (FOOT + 34, SOIL),
         '</g>']

open('tree.svgfrag', 'w').write(head + "\n" + "\n".join(out) + "\n</g></g>\n" + "\n".join(floor))
print('viewBox 900x%.0f  fit %.3f  raw %.0fx%.0f  filled %.0f%% wide %.0f%% tall'
      % (VB_H, k, xs1 - xs0, BASE[1] - ys0,
         100 * (xs1 - xs0) * k / 900.0, 100 * (BASE[1] - ys0) * k / (BASE[1] - TOP)))
