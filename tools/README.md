# Artwork generators

The ornaments on the invitation are drawn, not downloaded, and two of
them are too dense to author by hand. These scripts emit the SVG that is
pasted into `index.html`. They are **not** used at runtime — the page ships
the finished markup, so it renders with no JavaScript and no layout shift.

| script     | what it emits                              | lands in |
|------------|--------------------------------------------|----------|
| `arch.py`  | the cusped Moorish arch (`<path id="arch">`) | the hero and the cover |
| `tree.py`  | the pomegranate tree, the ground, and the couple standing on it | the navy plate |

Both seed a small LCG from the wedding date, so re-running any of
them reproduces exactly the same artwork.

`tree.py` grows the tree rather than drawing it, so its extent is not known
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
