# إبراهيم & أسيل — دعوة زفاف

A single-page Arabic wedding invitation for **إبراهيم زريق** and **أسيل هياجنة**,
Friday 25 September 2026, Summer Garden — Marriott Hotel.

Built to look like an antique Moroccan/Arabic wedding card that was printed
on aged paper and then very quietly animated. Mobile first, because the link
goes out over WhatsApp.

```
index.html    the whole page, including every ornament as inline SVG
style.css     the design system
script.js     the cover, the countdown, the map link, the RSVP
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
sent anywhere.** Fill in one of the three blocks in `script.js`:

```js
supabase : { url: '', key: '', table: 'rsvp' },
endpoint : '',
whatsapp : '',
```

## Where the replies go

`config.js` is the only file with your Supabase details in it. Both pages
read it: the invitation writes replies, `guests.html` reads them back.

**1. Make the table.** Supabase dashboard → SQL Editor → New query, paste
`sql/setup.sql`, run it. It creates `rsvp` and turns on row-level security
with two policies: the public key may INSERT and nothing else; SELECT
requires a signed-in user.

**2. Make the couple's account.** Authentication → Users → Add user. Give
it an email and password and tick *Auto Confirm User*, or Supabase will
send a confirmation mail that has to be clicked before sign-in works.

**3. Fill in `config.js`.** Project Settings → Data API gives you the
Project URL; the API keys section on the same page gives you the
**anon / public** key. Those two go in `config.js`.

The anon key is meant to be public — it ships inside the page and anyone
can read it. What it is *allowed to do* is decided by the policies, not by
hiding it. The key that must never go in this repo is `service_role` on
that same page: it ignores every policy.

**4. Open `guests.html`.** Sign in with the account from step 2. It shows
the tally (confirmed / total heads / apologies), the full list newest
first, and a CSV button. The session is kept in `sessionStorage`, so
closing the tab signs out.

Until `config.js` is filled in, the form still validates and thanks the
guest but the reply goes nowhere — so do this before the link is sent to
anybody. `CONFIG.whatsapp` in `script.js` is worth filling in as well: it
is what catches a reply when the network call fails.

#### Or a plain form service

`endpoint` takes any Formspree / Getform / Apps Script URL and posts the form
urlencoded instead.

#### Either way, set `whatsapp` too

Digits and country code, e.g. `'962791234567'`. It is the safety net: if the
network call fails, the thank-you screen turns into a WhatsApp button with the
reply already written out, so nobody's answer is silently lost. With *nothing*
else configured it becomes the primary path — the guest's WhatsApp opens on
submit and they press send.

The Netlify-style markup on the `<form>` does nothing on GitHub Pages; it is
left in place only so the same file can be dropped on Netlify unchanged.

### 2 · Check the details that were assumed

Everything the guest reads lives in two places — `CONFIG` at the top of
`script.js`, and the corresponding text in `index.html`. These were filled in
from the brief; two were inferred and are worth confirming:

| item | current value | note |
|------|---------------|------|
| city | **عمّان — الأردن** | assumed from the couple's names and the venue; change in `index.html` and `CONFIG.city` |
| map  | a Google Maps *search* for "Amman Marriott Hotel" | drop the real pin into `CONFIG.mapsLink` and the button uses it instead |
| RSVP deadline | ١٥ أيلول | in `index.html`, under `.rsvp-sub` |
| name order | the groom leads | swap the two `.nm` spans in the hero, and the pairings in the title, the cover, the dedication and the footer |

The event time is pinned to Amman (`+03:00`), so the countdown is correct even
for a guest whose phone is set to another timezone.

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

Palette, verbatim from the brief: antique cream `#DCC197`, warm ivory
`#E6DAC1`, deep burgundy `#612618`, pomegranate `#9B2E20`, midnight navy
`#14253A`, muted sage `#626455`, olive `#6B5D3D`, antique gold `#A88755`,
dark walnut `#2D2119`. Two derived leaf tints give the foliage depth.

The couple's names are set in **Aref Ruqaa Ink**, which is a colour font — it
carries its own ink bleed and prints in its own pomegranate red rather than
taking `color`. That is what gives them the letterpress look. Swap the family
to plain `Aref Ruqaa` in `--f-disp` if you ever want them in flat burgundy.

### Motion

Everything is slow on purpose.

* **The doors.** Two leaves that slide apart in their own plane — the
  right one right, the left one left — under a fixed lintel, with the
  opening's `overflow:hidden` as the thing they disappear into. No hinge
  and no rotation: `translateX` only, which is the one property the
  compositor can move without ever touching layout, and the reason it
  stays smooth on a phone. The slide has weight — the latch lets go and
  each leaf eases back a few pixels before it travels, then runs out and
  settles. Behind them is a card, not a blank panel: the same ornamental
  band frame as the invitation, the names, and the date.
* **The arch draws itself in** once the curtain is up — `stroke-dashoffset`
  on the cusped head, measured from the path at load.
* **Petals** fall the length of the page in the card's own palette, on a
  canvas rather than as elements. A handful is thrown up as the curtain
  opens.
* **The boughs breathe.** Only 15 groups animate; the other 80 ride along
  inside them, which keeps a canopy of a thousand leaves off the phone's
  main thread. The navy plate drifts inside its frame as it scrolls past,
  and the card tilts about a degree and a half to the pointer on desktop.

All of it is off under `prefers-reduced-motion`, which also skips the
curtain and lands the guest straight on the invitation.

### Type

Two Arabic faces, and the split between them is the whole readability story:

* **Aref Ruqaa (and Ruqaa Ink)** is a Ruq'ah hand — beautiful at display
  size, close to illegible at label size. It is used for the couple's
  names, the section titles, the two poetic lines and the big date
  numerals. Nothing under 20px is set in it.
* **Amiri**, a Naskh built to be read, carries everything else: the
  invitation line, the venue, every form label, button, hint and error.

Nothing on the page is under 14px. Arabic loses its meaning in strokes
that fine type drops, so the floor is higher than it would be for Latin.

### Controls

Every control on the page — the map button, the text fields, both answers,
the stepper — is one height, `--ctl`, with one edge treatment, `--edge`. The
two RSVP answers are forced to the same size with `grid-auto-rows:1fr`, since
a pair of controls that differ only by how much text they happen to hold reads
as a mistake. They stay in a single column at every width: side by side they
get about 170px each inside the card, which is not enough for
«للأسف لن أتمكن من الحضور» to sit on one line.

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
