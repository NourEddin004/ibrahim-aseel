#!/usr/bin/env python3
"""The arched doorway on the cover.

Emits three pieces of SVG:

  * `leaf`      — one door leaf, meeting edge on the right (x = 150). The
                  other leaf is the same drawing mirrored in CSS, so the
                  scrollwork meets itself down the centre line.
  * `surround`  — the stone head: voussoirs radiating off the arc, a
                  keystone at the crown, and the two pilasters. This sits
                  on the frame, not on the leaves, because a doorway does
                  not slide open with its own doorway.
  * `ivy`       — one climbing stem with its leaves, for the left jamb;
                  the right one is mirrored.

Geometry, in the doorway's own units (300 wide, 420 tall, so one leaf is
150): the head is a true semicircle of radius R about (150, SPRING), which
puts the crown at y = SPRING - R and the springing at the jambs.

Like the other generators here this is not used at runtime — the page
ships the finished markup. Seeded, so re-running reproduces it exactly.
"""

import math

W, H = 300.0, 420.0        # the whole doorway
SPRING = 176.0             # where the arc leaves the jamb
BAND = 24.0                # thickness of the stone head
R = W / 2 - BAND           # inner radius: the outer edge has to fit the box
JAMB = W / 2 - R           # the opening starts here, inside the pilaster


def f(x):
    """Trim a float to the shortest form that still reads the same."""
    s = f'{x:.1f}'
    s = s.rstrip('0').rstrip('.')
    return s or '0'


def pt(x, y):
    return f'{f(x)} {f(y)}'


# ── the spiral ──────────────────────────────────────────────────────
# A wrought scroll is a logarithmic spiral: it turns tighter as it goes,
# which is what stops it reading as a coil of wire. Sampled and joined
# with a smooth polyline, since the eye reads the curvature, not the
# control points.

def spiral(cx, cy, a, b, t0, t1, phase, steps=26):
    """r = a·e^(bθ), swept from t0 to t1 radians."""
    out = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        r = a * math.exp(b * t)
        out.append((cx + r * math.cos(t + phase),
                    cy + r * math.sin(t + phase)))
    return out


def smooth(points):
    """Catmull-Rom through the samples, emitted as cubic Béziers."""
    if len(points) < 2:
        return ''
    d = ['M' + pt(*points[0])]
    n = len(points)
    for i in range(n - 1):
        p0 = points[i - 1] if i else points[0]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < n else points[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{pt(*c1)} {pt(*c2)} {pt(*p2)}')
    return ''.join(d)


def scroll(cx, cy, size, phase, turns=1.45, flip=False):
    """One C-scroll: a straight-ish haunch running into a tight eye."""
    b = 0.22
    t1 = turns * 2 * math.pi
    a = size / math.exp(b * t1)
    pts = spiral(cx, cy, a, b, 0.0, t1, phase)
    if flip:
        pts = [(2 * cx - x, y) for x, y in pts]
    return smooth(pts)


# ── one leaf ────────────────────────────────────────────────────────
# Leaf space is 150 x 420 with the meeting edge at x = 150, which in the
# doorway's own space is the centre line — so the arc's centre sits on
# the leaf's right-hand edge and the head is a quarter circle here.

def leaf():
    out = []
    cx, cy = 150.0, SPRING

    # the silhouette: up the jamb, round the quarter, down the meeting edge
    sil = (f'M{pt(JAMB, H - 6)}L{pt(JAMB, SPRING)}'
           f'A{f(R)} {f(R)} 0 0 1 {pt(cx, SPRING - R)}'
           f'L{pt(150, H - 6)}Z')
    out.append(f'<path id="drLeaf" d="{sil}"/>')

    body = []
    body.append(f'<path class="dr-field" d="{sil}"/>')

    # the stile just inside the silhouette, and the muntin down the middle
    inset = 9.0
    ri = R - inset
    body.append('<path class="dr-stile" fill="none" d="'
                f'M{pt(JAMB + inset, H - 6 - inset)}L{pt(JAMB + inset, SPRING)}'
                f'A{f(ri)} {f(ri)} 0 0 1 {pt(cx, SPRING - ri)}'
                f'L{pt(150, H - 6 - inset)}" />')

    # the lock rail: the line the arch panel sits on
    rail = 236.0
    body.append(f'<path class="dr-rail" fill="none" d="M{pt(JAMB + inset, rail)}'
                f'H150M{pt(JAMB + inset, rail + 13)}H150"/>')

    # ── the ironwork, in the arched head ────────────────────────────
    # It grows off the meeting edge so the two leaves make one figure
    # when they are shut, and every eye turns the same way.
    iron = []

    # the spine, hard against the centre line
    iron.append('<path class="dr-iron" fill="none" d="'
                f'M{pt(146, rail - 8)}C{pt(146, 150)} {pt(146, 96)} {pt(146, SPRING - R + 14)}"/>')

    # three scrolls off the spine, biggest at the bottom
    for cy_s, size, ph in ((rail - 46, 27, -1.15),
                           (152.0, 23, -1.05),
                           (100.0, 19, -0.95)):
        iron.append(f'<path class="dr-iron" fill="none" d="{scroll(112, cy_s, size, ph)}"/>')
        # the tendril that ties it back to the spine
        iron.append('<path class="dr-iron dr-iron--thin" fill="none" d="'
                    f'M{pt(146, cy_s + 6)}C{pt(136, cy_s + 4)} {pt(131, cy_s - 2)} {pt(130, cy_s - 10)}"/>')

    # one counter-scroll low down, turning the other way, so the panel
    # does not read as three of the same thing stacked
    iron.append(f'<path class="dr-iron" fill="none" d="{scroll(72, rail - 74, 20, 2.0, flip=True)}"/>')

    # a small rosette where the spine meets the rail
    iron.append('<use href="#flr" class="dr-fl" transform="'
                f'translate(146 {f(rail - 22)}) scale(1.15)"/>')

    body.append('<g clip-path="url(#drClip)">' + ''.join(iron) + '</g>')

    # ── the panelled foot ───────────────────────────────────────────
    px0, px1 = JAMB + 14, 140.0
    py0, py1 = rail + 30, H - 34
    body.append(f'<path class="dr-pnl" fill="none" d="M{pt(px0, py0)}H{f(px1)}V{f(py1)}H{f(px0)}Z"/>')
    body.append(f'<path class="dr-pnl dr-pnl--in" fill="none" '
                f'd="M{pt(px0 + 7, py0 + 7)}H{f(px1 - 7)}V{f(py1 - 7)}H{f(px0 + 7)}Z"/>')
    # vertical boarding inside it
    n = 4
    for i in range(1, n):
        x = px0 + 7 + (px1 - px0 - 14) * i / n
        body.append(f'<path class="dr-board" fill="none" d="M{pt(x, py0 + 12)}V{f(py1 - 12)}"/>')

    out.append('<clipPath id="drClip"><path d="' + sil + '"/></clipPath>')
    return ('<clipPath id="drClip"><path d="' + sil + '"/></clipPath>\n'
            + '\n'.join(body))


# ── the stone head and the pilasters ────────────────────────────────

def surround():
    cx, cy = W / 2, SPRING
    r0, r1 = R + 1.0, R + BAND
    out = []

    # The wall, with the opening cut out of it. Without this the card
    # waiting behind the doors shows through everywhere the leaves are
    # not — they are clipped to the arch, so above the crown there was
    # nothing between the viewer and the invitation.
    out.append('<path class="dr-wall" fill-rule="evenodd" d="'
               f'M0 0H{f(W)}V{f(H)}H0Z'
               f'M{pt(JAMB, H)}L{pt(JAMB, cy)}'
               f'A{f(R)} {f(R)} 0 0 1 {pt(W - JAMB, cy)}'
               f'L{pt(W - JAMB, H)}Z"/>')

    # the band itself
    out.append('<path class="dr-arch" d="'
               f'M{pt(cx - r1, cy)}A{f(r1)} {f(r1)} 0 0 1 {pt(cx + r1, cy)}'
               f'L{pt(cx + r0, cy)}A{f(r0)} {f(r0)} 0 0 0 {pt(cx - r0, cy)}Z"/>')

    # the joints between the voussoirs. An odd count puts a stone, not a
    # joint, on the crown — the keystone needs something to be.
    n = 15
    for i in range(1, n):
        t = math.pi * i / n
        # the keystone is wider than its neighbours, so its two joints
        # are pushed out to make room for it
        if i in (n // 2, n // 2 + 1):
            t += (0.055 if i > n // 2 else -0.055)
        a = math.pi + t
        out.append('<path class="dr-joint" fill="none" d="'
                   f'M{pt(cx + r0 * math.cos(a), cy + r0 * math.sin(a))}'
                   f'L{pt(cx + r1 * math.cos(a), cy + r1 * math.sin(a))}"/>')

    # the keystone, standing a little proud of the band
    kw, kr = 0.055, r1 + 9
    a0, a1 = math.pi + math.pi / 2 - kw, math.pi + math.pi / 2 + kw
    out.append('<path class="dr-key" d="'
               f'M{pt(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0))}'
               f'A{f(r0)} {f(r0)} 0 0 1 {pt(cx + r0 * math.cos(a1), cy + r0 * math.sin(a1))}'
               f'L{pt(cx + kr * math.cos(a1 + .012), cy + kr * math.sin(a1 + .012))}'
               f'L{pt(cx + kr * math.cos(a0 - .012), cy + kr * math.sin(a0 - .012))}Z"/>')
    out.append(f'<use href="#star8" class="dr-keymark" transform="translate({f(cx)} {f(cy - r1 + 6)}) scale(.62)"/>')

    # the pilasters, from the springing to the floor, exactly as wide as
    # the stone head so the two read as one piece of masonry
    for x in (0.0, W - BAND):
        out.append(f'<path class="dr-pier" d="M{pt(x, cy - 6)}h{f(BAND)}v{f(H - cy + 6)}h-{f(BAND)}Z"/>')
        out.append('<path class="dr-joint" fill="none" d="'
                   f'M{pt(x + 5, cy + 4)}v{f(H - cy - 10)}"/>')

    # the threshold
    out.append(f'<path class="dr-sill" d="M0 {f(H - 14)}h{f(W)}v14H0Z"/>')
    return '\n'.join(out)


# ── the ivy at the jamb ─────────────────────────────────────────────

def ivy(seed=925):
    """One stem, drawn in a 70 x 300 box, rooted at the bottom."""
    st = seed
    def rnd():
        nonlocal st
        st = (st * 1103515245 + 12345) & 0x7FFFFFFF
        return st / 0x7FFFFFFF

    out = []
    # the main stem: a slow S up the box
    out.append('<path class="iv-stem" fill="none" d="'
               'M40 300C30 262 46 236 38 202C31 172 44 146 36 116C30 92 40 68 34 40"/>')
    # side shoots
    shoots = ((262, 1), (214, -1), (170, 1), (128, -1), (86, 1), (52, -1))
    for y, side in shoots:
        x0 = 38
        dx = 26 * side
        out.append('<path class="iv-stem iv-stem--thin" fill="none" d="'
                   f'M{f(x0)} {f(y)}C{f(x0 + dx * .5)} {f(y - 4)} '
                   f'{f(x0 + dx * .85)} {f(y - 12)} {f(x0 + dx)} {f(y - 20)}"/>')
        for k in range(3):
            t = (k + 1) / 3.4
            lx = x0 + dx * t
            ly = y - 20 * t * t
            rot = -140 * side + (rnd() * 40 - 20)
            sc = 0.72 + rnd() * 0.34
            out.append(f'<use href="#lf" class="iv-lf" transform="translate({f(lx)} {f(ly)}) '
                       f'rotate({f(rot)}) scale({f(sc)})"/>')
    # a few leaves straight off the stem
    for y in (240, 190, 148, 100, 62):
        rot = 200 + rnd() * 60
        out.append(f'<use href="#lf" class="iv-lf" transform="translate(37 {f(y)}) '
                   f'rotate({f(rot)}) scale({f(.7 + rnd() * .3)})"/>')
    return '\n'.join(out)


if __name__ == '__main__':
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('leaf', 'all'):
        print('<!-- LEAF -->')
        print(leaf())
    if which in ('surround', 'all'):
        print('<!-- SURROUND -->')
        print(surround())
    if which in ('ivy', 'all'):
        print('<!-- IVY -->')
        print(ivy())
