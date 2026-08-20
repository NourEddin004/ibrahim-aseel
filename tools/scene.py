# -*- coding: utf-8 -*-
"""The evening plate.

Not a photograph of a table and not a drawing pretending to be one — a
printed vignette, symmetrical the way the rest of the card is: a swag of
olive, roses and pomegranates dipping between two tapers, under a string
of lights.  The left half is drawn and then mirrored, which is both how
the engraver would have done it and why it comes out exactly even."""
import math

class R:
    def __init__(s, seed): s.x = seed
    def f(s):
        s.x = (1103515245 * s.x + 12345) % (1 << 31)
        return s.x / (1 << 31)
    def r(s, a, b): return a + (b - a) * s.f()

rnd = R(9252026)
W, H, CX = 900.0, 560.0, 450.0

# ── the string of bulbs, hung right across ───────────────────────────
bok = []
for (x0, y0, x1, y1, sag) in [(-60, 74, 470, 52, 62), (430, 52, 960, 78, 58),
                              (-50, 138, 480, 120, 48), (420, 120, 950, 146, 44)]:
    n = 13
    pts = [(x0 + (x1 - x0) * (i / float(n)),
            y0 + (y1 - y0) * (i / float(n)) + math.sin(math.pi * i / float(n)) * sag)
           for i in range(n + 1)]
    bok.append('<path class="wire" d="M%.0f %.0f%s" fill="none"/>'
               % (pts[0][0], pts[0][1], "".join(" L%.0f %.0f" % q for q in pts[1:])))
    for (x, y) in pts:
        if x < -30 or x > W + 30: continue
        r = rnd.r(2.8, 4.6)
        bok.append('<g class="bulb" style="--b:%d">'
                   '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="url(#haloS)" opacity=".45"/>'
                   '<circle cx="%.0f" cy="%.0f" r="%.1f" class="bulb-c"/></g>'
                   % (int(rnd.r(0, 9)), x, y + r, r * 5.2, x, y + r, r))
for i in range(14):
    bok.append('<circle class="blur" cx="%.0f" cy="%.0f" r="%.1f" fill="url(#haloS)" opacity="%.2f"/>'
               % (rnd.r(0, W), rnd.r(30, 250), rnd.r(4, 10), rnd.r(.1, .24)))

# ── one taper, on a turned holder.  Drawn once, mirrored once ────────
def taper(x, h, s):
    w, base = 13 * s, 424.0
    top = base - h
    return ('<g class="cd">'
            '<path class="cd-hold" d="M%.1f %.1f h%.1f l%.1f %.1f h%.1f l%.1f %.1f h-%.1f Z"/>'
            '<ellipse class="cd-foot" cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f"/>'
            '<path class="cd-stick" d="M%.1f %.1f h%.1f v%.1f h-%.1f Z"/>'
            '<path class="cd-drip" fill="none" d="M%.1f %.1f q%.1f %.1f 0 %.1f"/>'
            '<g class="cd-flame" style="--b:%d">'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#haloS)" opacity=".9"/>'
            '<path class="fl-body" d="M%.1f %.1f c%.1f %.1f %.1f %.1f 0 %.1f c%.1f %.1f %.1f %.1f 0 -%.1f Z"/>'
            '</g></g>'
            % (x - w * .9, base - 34 * s, w * 1.8, -w * .35, 16 * s, w * .1, -w * .35, 18 * s, w * .5,
               x, base, 30 * s, 9 * s,
               x - w / 2, top, w, h - 32 * s, w,
               x - w / 2 + 2.5, top + 18, -4, 15, 34,
               int(x) % 5,
               x, top - 15 * s, 38 * s,
               x, top - 30 * s, 10.4 * s, 10.4 * s, 10.4 * s, 19 * s, 30 * s,
               -10.4 * s, -10.4 * s, -10.4 * s, -19 * s, 30 * s))

# ── the swag: leaves along a dipping curve, fruit gathered at the dip ─
p0, p1, p2 = (24, 300), (238, 424), (450, 430)          # left half only
def q(t):
    u = 1 - t
    return (u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0], u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1])
def qt(t):
    u = 1 - t
    return math.degrees(math.atan2(2*u*(p1[1]-p0[1]) + 2*t*(p2[1]-p1[1]),
                                   2*u*(p1[0]-p0[0]) + 2*t*(p2[0]-p1[0])))

half = ['<path class="vine" fill="none" d="M%d %d Q%d %d %d %d"/>'
        % (p0[0], p0[1], p1[0], p1[1], p2[0], p2[1])]
N = 62
for i in range(N):
    t = i / float(N - 1)
    x, y = q(t); a = qt(t)
    grow = .75 + .85 * t                      # fuller as it nears the centre
    for side in (1, -1):
        half.append('<use href="#olv" class="lf" transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)"/>'
                    % (x + rnd.r(-9, 9), y + rnd.r(-12, 12),
                       a + side * rnd.r(30, 80), rnd.r(1.8, 2.6) * grow))
for (t, s, k, dy) in [(.30, 1.5, 'flr', -10), (.46, 1.9, 'pg', 8), (.58, 2.3, 'rose', -14),
                      (.70, 1.7, 'pg', 16), (.80, 2.5, 'rose', -6), (.90, 1.9, 'pgc', 14),
                      (.66, 1.3, 'flr', 22), (.86, 1.4, 'flr', -24)]:
    x, y = q(t)
    cls = {'pg': 'pg', 'pgc': 'pg', 'rose': 'rs', 'flr': 'fl'}[k]
    half.append('<use href="#%s" class="%s" transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)"/>'
                % (k, cls, x, y + dy, rnd.r(-16, 16), s))
half.append(taper(188, 258, 1.05))
# no votive glasses: a beige rectangle in front of the flowers was the one
# thing in the plate that looked like a UI element rather than an engraving.
# What they were really for was the low pool of light, so keep just that.
half.insert(1, '<circle cx="326" cy="446" r="74" fill="url(#halo)" opacity=".8" class="hl"/>')
half.insert(1, '<circle cx="120" cy="410" r="58" fill="url(#halo)" opacity=".6" class="hl"/>')

HALF = "\n".join(half)
# the middle of the swag: two sprigs rising, the cut fruit, one full rose
CENTRE = ('<use href="#olv" class="lf" transform="translate(450 396) rotate(-104) scale(3)"/>'
          '<use href="#olv" class="lf" transform="translate(450 396) rotate(-76) scale(3)"/>'
          '<use href="#olv" class="lf" transform="translate(422 370) rotate(-122) scale(2.5)"/>'
          '<use href="#olv" class="lf" transform="translate(478 370) rotate(-58) scale(2.5)"/>'
          '<use href="#rose" class="rs" transform="translate(450 428) scale(2.6)"/>'
          '<use href="#pgc" class="pg" transform="translate(450 372) rotate(-6) scale(1.9)"/>'
          '<use href="#flr" class="fl" transform="translate(450 466) scale(1.6)"/>')

open('frag.bokeh', 'w').write("\n".join(bok))
open('frag.half',  'w').write(HALF)
open('frag.centre','w').write(CENTRE)
print("bokeh %d   half-swag %d nodes" % (len(bok), len(half)))
