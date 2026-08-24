/* ═══════════════════════════════════════════════════════════════════
   CONFIG — everything you might need to change lives here, and only
   here.  The wording the guest reads is in index.html.
   ═══════════════════════════════════════════════════════════════════ */
const CONFIG = {
  couple : 'إبراهيم وأسيل',

  /* Pinned to Amman's offset, not the phone's. new Date(2026, 8, 25, 19, 30)
     would mean 7:30pm wherever the guest happens to be standing, so a
     relative abroad would get a countdown to the wrong moment. */
  start  : new Date('2026-09-25T19:30:00+03:00'),

  /* Paste the exact pin from Google Maps here once you have it. Until
     then the button runs a search for the hotel, which still lands the
     guest in the right place. */
  mapsLink : '',
  mapsQuery: 'فندق ماريوت عمان',

  /* ── where the replies go ────────────────────────────────────────
     Fill in ONE of the three. Until you do, the form validates and
     thanks the guest but the reply goes nowhere, so do this before the
     link is sent to anybody.

     supabase : project URL + anon key + table. See README.md for the
                table and the row-level-security policy — the anon key
                is public by design (it ships inside this page), so the
                table must be insert-only for it.
     endpoint : any plain form service — Formspree, Getform, an Apps
                Script web app. Posted as urlencoded form data.
     whatsapp : digits and country code, e.g. '962791234567'. Opens the
                guest's WhatsApp with the reply already written out.
                Worth filling in even alongside the other two: it is
                what catches a reply when the network call fails. */
  supabase : { url: '', key: '', table: 'rsvp' },
  endpoint : '',
  whatsapp : '',
};
const MAX_SEATS = 10;

const $ = (s, c = document) => c.querySelector(s);
const root = document.documentElement;
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* Arabic-Indic numerals: the whole card is set in them, so the live
   numbers have to match the printed ones. */
const ar = (v) => String(v).replace(/[0-9]/g, (d) => '٠١٢٣٤٥٦٧٨٩'[d]);
const pad = (n) => ar(String(n).padStart(2, '0'));

/* ── 0 · the doors ───────────────────────────────────────────────
   The whole doorway is the target — asking someone to find a small
   control on a phone is the wrong way round when the entire screen is
   the door.
   ═════════════════════════════════════════════════════════════════ */
{
  const gate  = $('#gate');
  const cover = $('#cover');

  const open = () => {
    root.classList.remove('is-sealed');
    root.classList.add('is-open');
  };

  if (calm) {
    gate.remove();
    open();
  } else {
    let going = false;

    const run = () => {
      if (going) return;
      going = true;
      cover.disabled = true;

      /* press (.16s) → the pulls let go (.28s) → the leaves slide apart
         (1.6s), with the card coming up behind while they are still
         travelling, so the reveal lands on it rather than on an empty
         opening */
      gate.classList.add('is-pressed');
      setTimeout(() => {
        gate.classList.remove('is-pressed');
        gate.classList.add('is-lifting');
      }, 160);
      setTimeout(() => {
        gate.classList.add('is-opening');
        sky && sky.burst();
      }, 440);
      setTimeout(() => gate.classList.add('is-naming'), 900);
      setTimeout(open, 1900);
      setTimeout(() => gate.classList.add('is-gone'), 2150);

      /* a fixed full-screen layer keeps swallowing taps even at opacity
         0, so it has to leave the DOM either way */
      gate.addEventListener('transitionend', (e) => {
        if (e.target === gate && e.propertyName === 'opacity') gate.remove();
      });
      setTimeout(() => gate.isConnected && gate.remove(), 4200);
    };

    const press   = () => !going && gate.classList.add('is-pressed');
    const release = () => !going && gate.classList.remove('is-pressed');
    cover.addEventListener('pointerdown', press);
    cover.addEventListener('pointerup', release);
    cover.addEventListener('pointercancel', release);
    cover.addEventListener('pointerleave', release);
    cover.addEventListener('click', run);
  }
}

/* ── 1 · the arch draws itself ───────────────────────────────────── */
for (const line of document.querySelectorAll('.arch-line')) {
  /* <use> has no length of its own — measure the path it points at */
  const src = $('#arch');
  if (!src) break;
  const len = Math.ceil(src.getTotalLength());
  line.style.setProperty('--len', len);
}

/* ── 1b · the cue stops asking once they have answered ───────────── */
addEventListener('scroll', function once() {
  if (scrollY < 40) return;
  root.classList.add('has-scrolled');
  removeEventListener('scroll', once);
}, { passive: true });

/* ── 2 · scroll reveal ───────────────────────────────────────────── */
{
  const io = new IntersectionObserver((rows) => {
    for (const r of rows) if (r.isIntersecting) {
      r.target.classList.add('in');
      io.unobserve(r.target);
    }
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
}

/* ── 3 · the countdown ───────────────────────────────────────────── */
{
  const D = $('#cdD'), H = $('#cdH'), M = $('#cdM'), S = $('#cdS');
  const tick = () => {
    let ms = CONFIG.start - Date.now();
    if (ms < 0) ms = 0;
    D.textContent = pad(Math.floor(ms / 864e5));
    H.textContent = pad(Math.floor(ms / 36e5) % 24);
    M.textContent = pad(Math.floor(ms / 6e4) % 60);
    S.textContent = pad(Math.floor(ms / 1e3) % 60);
  };
  tick();
  setInterval(tick, 1000);
}

/* ── 4 · the map ─────────────────────────────────────────────────── */
$('#mapLink').href = CONFIG.mapsLink ||
  'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(CONFIG.mapsQuery);

/* ── 5 · the reply ───────────────────────────────────────────────── */
{
  const form  = $('#rsvpForm');
  const name  = $('#rsvpName');
  const note  = $('#rsvpNote');
  const seats = $('#seatsField');
  const sOut  = $('#sOut'), sVal = $('#sVal');
  const minus = $('#sMinus'), plus = $('#sPlus');
  const errTop = $('#formErr'), errName = $('#nameErr');
  const errGo = $('#goErr');
  const btn = $('#sendBtn'), ctaText = $('#ctaText');
  const done = $('#rsvpDone'), doneSub = $('#doneSub'), waLink = $('#waLink');
  const doneEcho = $('#doneEcho');
  let n = 1, sent = false;

  const setSeats = (v) => {
    n = Math.min(MAX_SEATS, Math.max(1, v));
    sOut.textContent = ar(n);
    sVal.value = n;
    minus.disabled = n === 1;
    plus.disabled  = n === MAX_SEATS;
  };
  name.addEventListener('input', () => name.value.trim() && clear(errName, name));

  minus.addEventListener('click', () => setSeats(n - 1));
  plus .addEventListener('click', () => setSeats(n + 1));
  setSeats(1);

  const coming = () => (form.attending.value || '').startsWith('نعم');

  form.addEventListener('change', (e) => {
    if (e.target.name === 'attending') {
      seats.hidden = !coming();
      clear(errGo);
    }
    if (e.target === name && name.value.trim()) clear(errName, name);
  });

  const flag = (box, msg, field) => {
    box.textContent = msg;
    box.hidden = false;
    if (field) field.setAttribute('aria-invalid', 'true');
  };
  const clear = (box, field) => {
    box.hidden = true;
    if (field) field.removeAttribute('aria-invalid');
  };

  /* the reply, written out the way the couple will want to read it */
  const message = () => [
    `تأكيد حضور — زفاف ${CONFIG.couple}`,
    `الاسم: ${name.value.trim()}`,
    `الحضور: ${form.attending.value}`,
    coming() ? `عدد الأشخاص: ${n}` : '',
    note.value.trim() ? `ملاحظات: ${note.value.trim()}` : '',
  ].filter(Boolean).join('\n');

  const waHref = () => 'https://wa.me/' + CONFIG.whatsapp +
    '?text=' + encodeURIComponent(message());

  const settle = () => {
    form.hidden = true;
    done.hidden = false;
    doneSub.textContent = coming()
      ? 'وجودكم يعني لنا الكثير، وننتظركم على أحرّ من الجمر'
      : 'سنفتقدكم في يومنا، وشكرًا لإخبارنا';
    /* echo the reply back. A thank-you that does not say WHAT was
       received leaves the guest with no way to tell a mistake from a
       success — and no way to know whether to send it again. */
    doneEcho.textContent = coming()
      ? `${name.value.trim()} — ${ar(n)} ${n === 1 ? 'شخص' : n === 2 ? 'شخصان' : 'أشخاص'}`
      : `${name.value.trim()} — لن يتمكن من الحضور`;
    done.focus();
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (sent) return;
    errTop.hidden = true;
    clear(errName, name);
    clear(errGo);

    if (!name.value.trim()) {
      flag(errName, 'يرجى كتابة الاسم الكامل', name);
      name.focus();
      return;
    }
    if (!form.attending.value) {
      flag(errGo, 'يرجى اختيار أحد الخيارين');
      /* without this the message appears and the caret stays where it
         was — announced, but with no way to find what it is about */
      form.attending[0].focus();
      return;
    }

    const sb = CONFIG.supabase;
    const wired = (sb && sb.url && sb.key) || CONFIG.endpoint;

    /* Nothing to POST to: hand the reply straight to WhatsApp. window.open
       has to run inside this handler and before any await, or the tap is
       already spent and the popup blocker takes it. */
    if (!wired && CONFIG.whatsapp) {
      sent = true;
      window.open(waHref(), '_blank', 'noopener');
      settle();
      return;
    }
    if (!wired) { sent = true; settle(); return; }

    sent = true;
    btn.disabled = true;
    ctaText.textContent = 'جارٍ الإرسال…';

    try {
      const res = sb && sb.url && sb.key
        ? await fetch(`${sb.url.replace(/\/$/, '')}/rest/v1/${sb.table}`, {
            method: 'POST',
            headers: {
              'apikey': sb.key,
              'Authorization': `Bearer ${sb.key}`,
              'Content-Type': 'application/json',
              'Prefer': 'return=minimal',
            },
            body: JSON.stringify({
              name: name.value.trim(),
              attending: form.attending.value,
              guests: coming() ? n : 0,
              note: note.value.trim() || null,
            }),
          })
        : await fetch(CONFIG.endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(new FormData(form)).toString(),
          });
      if (!res.ok) throw new Error(res.status);
      settle();
    } catch {
      /* never lose a reply: fall back to a WhatsApp hand-off the guest
         can tap themselves, since the gesture is long gone by now */
      settle();
      if (CONFIG.whatsapp) {
        waLink.href = waHref();
        waLink.hidden = false;
        doneSub.textContent = 'لم يصل الردّ بعد — أرسلوه لنا عبر واتساب من فضلكم';
      }
    } finally {
      btn.disabled = false;
      ctaText.textContent = 'تأكيد الحضور';
    }
  });
}

/* ── 6 · petals on the air ───────────────────────────────────────
   Canvas rather than elements: two dozen drifting shapes as DOM nodes
   would have the compositor re-laying-out the page sixty times a second
   behind a form people are trying to fill in.
   ═════════════════════════════════════════════════════════════════ */
const sky = calm ? null : (() => {
  const cv = $('#motes');
  const ctx = cv.getContext('2d');
  let w, h, dpr;

  const size = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    w = cv.width  = Math.round(innerWidth  * dpr);
    h = cv.height = Math.round(innerHeight * dpr);
  };
  size();
  addEventListener('resize', size, { passive: true });

  /* pomegranate red, a deeper rose, sage, olive, gold and cream — the
     card's own palette, so what falls looks like it came off the page.
     Second value is the shape: 0 petal, 1 leaf, 2 whole flower. */
  const PETAL = 0, LEAF = 1, BLOOM = 2;
  const KIND = [
    ['#9B2E20', PETAL], ['#7C241B', PETAL], ['#B4472F', PETAL],
    ['#DCC197', PETAL], ['#A88755', PETAL],
    ['#7C8467', LEAF],  ['#626455', LEAF],  ['#5C7050', LEAF],
    ['#9B2E20', BLOOM], ['#B4472F', BLOOM], ['#C9A05A', BLOOM],
  ];

  const make = (fromTop) => {
    const [c, shape] = KIND[(Math.random() * KIND.length) | 0];
    return {
      x   : Math.random(),
      y   : fromTop ? -0.08 - Math.random() * 0.3 : Math.random(),
      r   : (shape === BLOOM ? 5 + Math.random() * 4 : 4.5 + Math.random() * 6) * dpr,
      /* roughly a third of what it was: a petal now takes the better part
         of half a minute to cross the screen, which is the difference
         between falling and being blown past */
      vy  : (0.032 + Math.random() * 0.05) / 1000,
      vx  : (Math.random() - 0.5) / 7000,
      rot : Math.random() * Math.PI * 2,
      vr  : (Math.random() - 0.5) * 0.0004,
      p   : Math.random() * Math.PI * 2,
      sway: 0.00006 + Math.random() * 0.00013,
      a   : 0.18 + Math.random() * 0.28,
      c, shape,
    };
  };

  const N = Math.round(Math.min(24, Math.max(10, innerWidth / 30)));
  let flakes = Array.from({ length: N }, () => make(false));

  const petal = (r) => {
    ctx.beginPath();
    ctx.moveTo(0, -r);
    ctx.bezierCurveTo(r * 0.95, -r * 0.45, r * 0.62, r * 0.72, 0, r);
    ctx.bezierCurveTo(-r * 0.62, r * 0.72, -r * 0.95, -r * 0.45, 0, -r);
    ctx.closePath();
  };
  const leafShape = (r) => {
    ctx.beginPath();
    ctx.moveTo(0, -r * 1.2);
    ctx.quadraticCurveTo(r * 0.66, 0, 0, r * 1.2);
    ctx.quadraticCurveTo(-r * 0.66, 0, 0, -r * 1.2);
    ctx.closePath();
  };
  /* a whole five-petal bloom, the same flower that runs through the
     borders — drawn petal by petal so it keeps a soft centre */
  const bloom = (r, colour) => {
    for (let i = 0; i < 5; i++) {
      ctx.save();
      ctx.rotate((i * Math.PI * 2) / 5);
      ctx.beginPath();
      ctx.ellipse(0, -r * 0.66, r * 0.36, r * 0.66, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
    ctx.fillStyle = '#C9A05A';
    ctx.beginPath();
    ctx.arc(0, 0, r * 0.27, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = colour;
  };

  let raf = 0, last = 0;
  const step = (now) => {
    /* Re-check rather than trusting the one measurement taken at load: a
       tab that starts life with a zero-sized viewport (backgrounded, or
       inside some in-app browsers) would otherwise keep a 0x0 canvas for
       the rest of the session and never show a thing. */
    if (cv.width !== Math.round(innerWidth * dpr) ||
        cv.height !== Math.round(innerHeight * dpr)) size();

    const dt = Math.min(64, now - last || 16);
    last = now;
    ctx.clearRect(0, 0, w, h);

    let drop = false;
    for (const f of flakes) {
      if (f.g) f.vy += f.g * dt;               // burst petals fall back
      f.y += f.vy * dt;
      f.p += f.sway * dt;
      f.x += f.vx * dt + Math.sin(f.p) * 0.00026 * dt;
      f.rot += f.vr * dt;

      if (f.y > 1.12) {
        if (f.g) { f.dead = true; drop = true; continue; }
        Object.assign(f, make(true));
      }
      if (f.x < -0.1) f.x += 1.2;
      if (f.x > 1.1)  f.x -= 1.2;

      ctx.save();
      ctx.translate(f.x * w, f.y * h);
      ctx.rotate(f.rot);
      /* the narrow axis is what sells it: a petal turning edge-on is the
         difference between falling and merely sliding down the screen */
      /* a bloom read edge-on looks like a smear, so it keeps more of its
         width than a single petal does */
      const flat = Math.abs(Math.cos(f.p * 1.7));
      ctx.scale(f.shape === BLOOM ? 0.62 + 0.38 * flat : 0.3 + 0.7 * flat, 1);
      ctx.globalAlpha = f.a;
      ctx.fillStyle = f.c;
      if (f.shape === BLOOM) { bloom(f.r, f.c); }
      else { f.shape === LEAF ? leafShape(f.r) : petal(f.r); ctx.fill(); }
      ctx.restore();
    }
    if (drop) flakes = flakes.filter((f) => !f.dead);

    raf = requestAnimationFrame(step);
  };
  raf = requestAnimationFrame(step);

  /* a hidden tab still burns battery on requestAnimationFrame in some
     browsers, and there is nothing to see either way */
  addEventListener('visibilitychange', () => {
    if (document.hidden) { cancelAnimationFrame(raf); raf = 0; }
    else if (!raf) { last = 0; raf = requestAnimationFrame(step); }
  });

  return {
    /* a handful thrown up as the cover opens, then let go of */
    burst() {
      for (let i = 0; i < 20; i++) {
        const f = make(false);
        f.x  = 0.5 + (Math.random() - 0.5) * 0.3;
        f.y  = 0.4 + (Math.random() - 0.5) * 0.16;
        f.vy = -(0.05 + Math.random() * 0.1) / 1000;
        f.vx = (Math.random() - 0.5) / 900;
        f.g  = (0.7 + Math.random() * 0.9) / 1e6;
        f.vr = (Math.random() - 0.5) * 0.0018;
        f.a  = 0.45 + Math.random() * 0.4;
        flakes.push(f);
      }
    },
  };
})();

/* ── 7 · the border bands fit a whole number of motifs ───────────
   A userSpaceOnUse pattern tiles from the origin and stops wherever the
   strip ends, so every band was finishing on a sliced motif — a whole
   star at one end and a shard at the other. This is what CSS gives you
   as `background-repeat: round`, and there is no SVG equivalent, so it
   is done by hand: give each strip its own pattern and stretch the tile
   along the strip by up to a few percent until the count comes out
   whole. Across the strip nothing changes, so the band keeps its exact
   thickness.
   ═════════════════════════════════════════════════════════════════ */
{
  const SVGNS = 'http://www.w3.org/2000/svg';
  const REPEAT = { bandH: 46, bandV: 46, starband: 34 };
  const strips = [...document.querySelectorAll('.fe')];
  const store = $('.plates defs');
  let made = 0;

  const fit = () => {
    for (const svg of strips) {
      const rect = svg.querySelector('rect');
      if (!rect) continue;
      const src = (rect.dataset.pattern ||
                   (rect.getAttribute('fill') || '').replace(/^url\(#|\)$/g, ''));
      const tile = REPEAT[src];
      if (!tile) continue;
      rect.dataset.pattern = src;

      const across = svg.classList.contains('ft') || svg.classList.contains('fb');
      const len = across ? svg.clientWidth : svg.clientHeight;
      if (!len) continue;

      const n = Math.max(1, Math.round(len / tile));
      const k = len / (n * tile);

      let own = rect.dataset.own;
      if (!own) {
        own = rect.dataset.own = `${src}-fit-${made++}`;
        const clone = document.createElementNS(SVGNS, 'pattern');
        clone.setAttribute('id', own);
        clone.setAttribute('href', `#${src}`);
        store.appendChild(clone);
        rect.setAttribute('fill', `url(#${own})`);
      }
      document.getElementById(own).setAttribute(
        'patternTransform', across ? `scale(${k.toFixed(5)},1)` : `scale(1,${k.toFixed(5)})`);
    }
  };

  fit();
  let wait;
  addEventListener('resize', () => { clearTimeout(wait); wait = setTimeout(fit, 120); },
                   { passive: true });
  /* the webfonts can nudge the card's width when they land */
  document.fonts && document.fonts.ready.then(fit);
}

/* ── 8 · the plate drifts as it passes ───────────────────────────── */
{
  const field = $('.np-field'), tree = $('.tree');
  if (field && tree && !calm) {
    let live = false, queued = false;
    new IntersectionObserver((rows) => { live = rows[0].isIntersecting; },
                             { rootMargin: '80px' }).observe(field);
    const move = () => {
      queued = false;
      if (!live) return;
      const r = field.getBoundingClientRect();
      const p = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
      tree.style.transform = `translate3d(0,${(-p * 18).toFixed(1)}px,0)`;
    };
    addEventListener('scroll', () => {
      if (!queued) { queued = true; requestAnimationFrame(move); }
    }, { passive: true });
    move();
  }
}

/* ── 9 · the card tilts to the pointer ───────────────────────────── */
{
  const sec = $('.sec--hero'), sheet = $('.sec--hero .sheet');
  const fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
  if (sec && sheet && fine && !calm) {
    let queued = 0, ry = 0, rx = 0;
    const apply = () => {
      queued = 0;
      sheet.style.transform = `rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
    };
    sec.addEventListener('pointermove', (e) => {
      const r = sec.getBoundingClientRect();
      ry = ((e.clientX - r.left) / r.width - 0.5) * 3;
      rx = -((e.clientY - r.top) / r.height - 0.5) * 2;
      if (!queued) queued = requestAnimationFrame(apply);
    });
    sec.addEventListener('pointerleave', () => {
      ry = rx = 0;
      if (!queued) queued = requestAnimationFrame(apply);
    });
  }
}


/* ── 10 · the tree fills when you reach it ───────────────────────────
   The plate used to be finished before anyone had scrolled to it, and
   the birds and fruit looped whether or not the guest was looking. It
   plays once now, on arrival: fruit to the branches first, then the
   birds in off the frame to land. The observer disconnects on the first
   hit so scrolling back up does not replay it — an entrance that
   happens twice is a loop with extra steps.
   ══════════════════════════════════════════════════════════════════ */
{
  const tree = $('.tree');
  if (tree) {
    /* last bird is down at 2.45 + 7 x .2 + 1.3 = 5.15s */
    const SETTLED = 7200;   /* 2.6 + 7 x .22 + 2.8 = 6.94s */
    /* tree--wait has to come off at the same moment tree--land goes on.
       The entrance animations fill backwards, so they hold everything
       hidden through their own delay anyway — but once tree--rest swaps
       the birds back to perch, which never touches opacity, a lingering
       wait rule would put them out again the instant they landed. */
    const start = () => {
      tree.classList.remove('tree--wait');
      tree.classList.add('tree--land');
      setTimeout(() => tree.classList.add('tree--rest'), SETTLED);
    };
    if (calm) {
      tree.classList.remove('tree--wait');
      tree.classList.add('tree--land', 'tree--rest');
    } else {
      const io = new IntersectionObserver((rows) => {
        if (!rows[0].isIntersecting) return;
        io.disconnect();
        start();
      }, { threshold: 0.25 });
      io.observe(tree);
    }
  }
}
