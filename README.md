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

#### Supabase

Paste the project URL and the **anon** key. The form posts straight to
PostgREST — no functions, no server:

```sql
create table public.rsvp (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name       text   not null,
  attending  text   not null,
  guests     int    not null default 1,
  note       text
);

alter table public.rsvp enable row level security;

-- anon may add a reply and nothing else
create policy "anon inserts rsvp"
  on public.rsvp for insert to anon with check (true);
```

**Give it the insert policy and no select policy.** The anon key ships inside
this page — that is what it is for, and it is safe *provided* the table cannot
be read back with it. With only the insert policy above, a guest can leave a
reply and cannot list anyone else's. Read the replies from the Supabase table
editor, or with the service key from somewhere that is not a web page.

Two optional hardening steps, worth it if the link circulates widely:

```sql
-- keep a stray double-tap from making two rows
create unique index rsvp_one_per_name on public.rsvp (lower(trim(name)));

-- and cap the free text
alter table public.rsvp add constraint rsvp_sane
  check (length(name) between 2 and 80 and length(coalesce(note,'')) <= 500);
```

The unique index makes a repeat submission fail, which lands the guest on the
WhatsApp fallback rather than silently duplicating — if you would rather they
just succeed quietly, leave it out.

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

* **The cover** is a real two-sided card hinged on the right, the edge an
  Arabic book opens from, and it opens **towards the reader** — out of the
  screen, not away into it. That is the sign of the rotation: with the hinge
  on the right, a positive `rotateY` brings the free edge forward and a
  negative one sends it back through the glass. Press → the seal lifts away →
  the cover swings out through 162°, passing edge-on and standing open like a
  card on a table → the invitation underneath comes up to full size → the
  layer dissolves. The whole card is the tap target, not just the seal; the
  seal is there to say *touch me*, not to be the only place that works.
* **Petals** fall the length of the page — pomegranate red, rose, sage, olive,
  gold and cream, the card's own palette. Drawn on a canvas rather than as
  elements, and each one narrows as it turns edge-on, which is the difference
  between falling and merely sliding down the screen. A handful is thrown up
  when the cover opens.
* **The boughs breathe.** Only 15 groups animate; the other 80 ride along
  inside them, which keeps a canopy of a thousand leaves off the phone's main
  thread. The birds shift their weight, the arch draws itself in once, and the
  navy plate drifts a little inside its frame as it scrolls past.
* **The card tilts** to the pointer on desktop — about a degree and a half,
  enough to read as a physical thing catching the light. Pointer-only; it is
  never wired to a phone's gyroscope.

All of it is off under `prefers-reduced-motion`, which also skips the cover
entirely and lands the guest straight on the invitation.

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
