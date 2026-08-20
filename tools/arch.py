# -*- coding: utf-8 -*-
"""The cusped Moorish arch of the reference invitation.

A pointed arch profile, scalloped into foils.  cos^0.7 makes the two halves
arrive at the apex vertically, so they meet in a true point rather than a
dome; the lobes are circular arcs bulging into the opening."""
import math

W, H, N = 300.0, 200.0, 6      # half-width lobes per side
cx = W / 2

def prof(s):
    """s in [-1,1]: -1 left springing, 0 apex, 1 right springing."""
    th = (1 - abs(s)) * math.pi / 2          # 0 at springing, pi/2 at apex
    x = cx * (1 - math.cos(th))
    y = H * math.cos(th) ** 0.7
    return (x if s < 0 else W - x), y

# sample by ARC LENGTH, not by parameter -- otherwise the foils at the
# springing come out as pinpricks and the one at the apex swallows the arch
import bisect
dense = [prof(-1 + i / 4000.0 * 2) for i in range(4001)]
cum, tot = [0.0], 0.0
for i in range(1, len(dense)):
    tot += math.hypot(dense[i][0]-dense[i-1][0], dense[i][1]-dense[i-1][1])
    cum.append(tot)
pts = []
for k in range(2 * N + 1):
    target = tot * k / (2.0 * N)
    j = min(bisect.bisect_left(cum, target), len(dense) - 1)
    pts.append(dense[j])

seg = []
for i in range(1, len(pts)):
    x0, y0 = pts[i - 1]
    x1, y1 = pts[i]
    ch = math.hypot(x1 - x0, y1 - y0)
    r = ch * 0.56                            # <.5 is impossible, .56 = a plump foil
    # sweep 0: each foil bites INTO the opening, which is what makes it a
    # cusped arch rather than a row of bubbles sitting on top of one
    seg.append("A%.1f %.1f 0 0 0 %.1f %.1f" % (r, r, x1, y1))

open_path = "M%.1f %.1f " % pts[0] + " ".join(seg)
print("OPEN  :", open_path)
print()
print("CLOSED:", open_path + " Z")
