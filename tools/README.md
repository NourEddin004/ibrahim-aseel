# Artwork generators

The ornaments on the invitation are drawn, not downloaded, and two of
them are too dense to author by hand. These scripts emit the SVG that is
pasted into `index.html`. They are **not** used at runtime — the page ships
the finished markup, so it renders with no JavaScript and no layout shift.

| script     | what it emits                              | lands in |
|------------|--------------------------------------------|----------|
| `arch.py`  | the cusped Moorish arch (`<path id="arch">`) | the hero and the cover |
| `tree.py`  | the pomegranate tree — ~1000 leaves, 15 animated boughs | the navy plate |

Both seed a small LCG from the wedding date, so re-running any of
them reproduces exactly the same artwork.

```bash
python3 tools/tree.py     # writes tree.svgfrag next to the script
```

Then replace the contents of the matching group in `index.html`. Take the
whole group — the fragments contain nested `<g>` elements, so a lazy
regex that stops at the first `</g>` will leave half the old drawing
behind.
