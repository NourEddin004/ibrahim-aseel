# أسيل & إبراهيم — دعوة زفاف

A single-page Arabic wedding invitation for **أسيل هياجنة** and **إبراهيم زريق**,
Friday 25 September 2026, Summer Garden — Marriott Hotel.

Built to look like an antique Moroccan/Arabic wedding card that was printed
on aged paper and then very quietly animated. Mobile first, because the link
goes out over WhatsApp.

```
index.html    the whole page, including every ornament as inline SVG
style.css     the design system
script.js     the cover, the countdown, the calendar link, the RSVP
og-image.png  1200×630 preview card for WhatsApp / Facebook
tools/        the generators for the three dense drawings (see tools/README.md)
```

No build step, no dependencies, no framework. Four webfonts from Google
(Aref Ruqaa Ink, Aref Ruqaa, Amiri, Cormorant Garamond) are the only network
requests the page makes.

---

## Before you send the link — three things

### 1 · Make the replies actually arrive ⚠️

Out of the box the RSVP form validates and thanks the guest, **but nothing is
sent anywhere.** Open `script.js` and fill in *one* of these two:

```js
endpoint : '',   // a Formspree / Getform / Google-Apps-Script URL
whatsapp : '',   // digits + country code, e.g. '962791234567'
```

* **`whatsapp`** is the simplest and needs no account. On submit the guest's
  WhatsApp opens with the reply already written out — name, attending or not,
  how many people, any note — addressed to that number. They press send.
* **`endpoint`** posts the form quietly in the background instead. If the POST
  fails, the thank-you screen falls back to a WhatsApp button, so a reply is
  never silently lost — provided `whatsapp` is filled in too. Fill in both if
  you can.

GitHub Pages has no server, so the Netlify-style markup on the `<form>` does
nothing there; it is left in place only so the same file can be dropped on
Netlify unchanged.

### 2 · Check the details that were assumed

Everything the guest reads lives in two places — `CONFIG` at the top of
`script.js`, and the corresponding text in `index.html`. These were filled in
from the brief; two were inferred and are worth confirming:

| item | current value | note |
|------|---------------|------|
| city | **عمّان — الأردن** | assumed from the couple's names and the venue; change in `index.html` and `CONFIG.city` |
| map  | a Google Maps *search* for "Amman Marriott Hotel" | drop the real pin into `CONFIG.mapsLink` and the button uses it instead |
| RSVP deadline | ١٥ أيلول | in `index.html`, under `.rsvp-sub` |

The event time is pinned to Amman (`+03:00`), so the countdown is correct even
for a guest whose phone is set to another timezone. The `.ics` file is written
as a floating local time on purpose, so every calendar shows 7:30pm.

### 3 · Bump the cache buster

`index.html` links `style.css?v=2` and `script.js?v=2`. **Increment both
numbers whenever you edit either file.** Browsers cache them hard, and a guest
who already opened the invitation will otherwise keep seeing the old one.

---

## The design

Straight off the bride's references:

* **The cusped Moorish arch with a rosette-lattice spandrel** — the printed
  Moroccan invitation. It is the hero, and it is also the cover.
* **The pomegranate tree on midnight navy, red border, eight-point corner
  medallions, birds in the branches** — the woven textile.
* **The pietra-dura star band** framing the details — the inlaid marble frame.
* **The candlelit swag of olive, burgundy roses and pomegranates** — the two
  reception photographs, drawn rather than photographed so that the page stays
  a printed object throughout.

Palette, verbatim from the brief: antique cream `#DCC197`, warm ivory
`#E6DAC1`, deep burgundy `#612618`, pomegranate `#9B2E20`, midnight navy
`#14253A`, muted sage `#626455`, olive `#6B5D3D`, antique gold `#A88755`,
dark walnut `#2D2119`. Two derived leaf tints give the foliage depth.

The couple's names are set in **Aref Ruqaa Ink**, which is a colour font — it
carries its own ink bleed and prints in its own pomegranate red rather than
taking `color`. That is what gives them the letterpress look. Swap the family
to plain `Aref Ruqaa` in `--f-disp` if you ever want them in flat burgundy.

### Motion

Everything is slow on purpose. The boughs breathe (only 15 groups animate; the
other 80 ride along inside them, which keeps a canopy of a thousand leaves off
the phone's main thread), the birds shift their weight, the flames flicker, the
arch draws itself in once when the cover opens, and gold dust drifts. All of it
is turned off under `prefers-reduced-motion` — which also skips the cover
entirely and lands the guest straight on the invitation.

---

## Working on it

```bash
python3 -m http.server 8711
```

Then open <http://localhost:8711>. `.claude/launch.json` has the same thing
wired up as a preview target.

With JavaScript disabled the cover never appears and the invitation is readable
straight away — the cover and the scroll lock are both switched on by a one-line
script in `<head>`, never baked into the markup.
