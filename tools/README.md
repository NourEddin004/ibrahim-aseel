# Artwork generators

The ornaments on the invitation are drawn, not downloaded, and two of
them are too dense to author by hand. These scripts emit the SVG that is
pasted into `index.html`. They are **not** used at runtime — the page ships
the finished markup, so it renders with no JavaScript and no layout shift.

| script     | what it emits                              | lands in |
|------------|--------------------------------------------|----------|
| `arch.py`  | the cusped Moorish arch (`<path id="arch">`) | the hero and the cover |
| `tree.py`  | the pomegranate tree, the ground, the birds and the couple | the navy plate |
| `door.py`  | the arched doorway: one leaf, the stone head, and the ivy | the cover |

Both seed a small LCG from the wedding date, so re-running any of
them reproduces exactly the same artwork.

`tree.py` is shaped from a photograph of a real pomegranate rather than from
the weaving: a broad low dome on a short trunk that forks early, wider than
it is tall, with the outer branches arching over and drooping at the tips.
The canopy is a mass — 1371 leaves, small ones, scattered off the stems
rather than lined up along them — because six big leaves a limb reads as a
diagram of a tree, not a tree. The navy field was made near-square to take
it; against the old portrait frame a dome could only ever be width-limited,
and the top third of the plate stayed empty.

The seed is no longer the wedding date. The tree is grown, so how squarely
it comes out is down to the seed, and the date's grew one that reached 150
units further right than left — which the fit then pays for, since it must
scale by the longest arm and the trunk may not leave the centre line.
Twenty were grown; seed 13 comes out 8 units off symmetric and fills the
plate 91% by 98%, where the date's managed 74% by 100%.

It grows rather than draws, so its extent is not known
until it exists — and it never comes out symmetric. The tail of the script
measures what grew and fits it to the plate, scaling about the foot of the
trunk and allowing a small capped sideways shift to balance the two halves.
The ground and the couple are emitted in a `tree-floor` group carrying that
same shift, so the trunk always stands where the grass is.

```bash
python3 tools/tree.py     # writes tree.svgfrag next to the script
```

Then replace the contents of the matching group in `index.html`. Take the
whole group — the fragments contain nested `<g>` elements, so a lazy
regex that stops at the first `</g>` will leave half the old drawing
behind.

`door.py` emits four pieces. The leaf is drawn once with its meeting edge
on the right, which is what the left-hand door needs; the right-hand one is
that same drawing mirrored in CSS, so the ironwork meets itself down the
centre line while the doors are shut.

**A leaf is a rectangle.** It was cut to its own arched silhouette once,
and that was the whole trouble: the shape travelled with the leaf, so
drawing the doors back slid two door-shaped arches out from under the
stone one. A leaf is masked by the doorway it sits in, not by a copy of
the doorway it carries with it — so the arch is a clip on a stationary
wrapper and the leaves underneath are the rectangles doors actually are.
They disappear into the jambs like pocket doors. The arched hairline just
inside the opening moved to the surround for the same reason: a reveal
belongs to the doorway, and it used to slide away with the door. The stone head and the pilasters are
a separate piece because they belong to the frame, not to the leaves — a
doorway does not slide open with its own doorway — The fourth piece is the
opening as a clip path: the leaves are clipped to the arch and cover
nothing above the crown, so something has to keep the card behind them out
of sight. That used to be a wall — a rectangle with the opening cut out of
it — but painting it meant painting flat cream over a page whose parchment
is not flat, and the doorway ended up sitting on a visible panel. Clipping
what is behind is the same result with nothing drawn at all.

The scrolls are logarithmic spirals rather than arcs: a wrought scroll
turns tighter as it goes, and that is the thing that stops it reading as
a coil of wire. They are sampled and joined with Catmull-Rom, since what
the eye reads is the curvature, not the control points.
