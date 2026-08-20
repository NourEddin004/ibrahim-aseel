/* ═══════════════════════════════════════════════════════════════════
   CONFIG — everything you might need to change lives here, and only
   here.  ⚠️ months are 0-indexed: 8 = September.
   ═══════════════════════════════════════════════════════════════════ */
const CONFIG = {
  couple : 'أسيل وإبراهيم',

  /* Pinned to Amman's offset, not the phone's. new Date(2026, 8, 25, 19, 30)
     would mean 7:30pm wherever the guest happens to be standing, so a
     relative abroad would get a countdown to the wrong moment. */
  start  : new Date('2026-09-25T19:30:00+03:00'),
  end    : new Date('2026-09-26T00:00:00+03:00'),

  /* …and the calendar entry is written the other way round: as a floating
     local time, with no zone at all, so every guest's calendar simply says
     7:30pm the way the printed card does. */
  icsStart : '20260925T193000',
  icsEnd   : '20260926T000000',

  venue  : 'الحديقة الصيفية — فندق ماريوت',
  city   : 'عمّان، الأردن',

  /* Paste the exact pin from Google Maps here once you have it. Until
     then the button runs a search for the hotel, which still lands the
     guest in the right place. */
  mapsLink : '',
  mapsQuery: 'Amman Marriott Hotel',

  /* ── where the replies go ────────────────────────────────────────
     endpoint : a Formspree / Getform / Apps-Script URL. Leave empty on
                GitHub Pages — there is no server there to POST to.
     whatsapp : the number that should receive replies, digits only and
                with the country code (e.g. '962791234567'). When there
                is no endpoint this is how the reply actually reaches
                the couple, so one of the two must be filled in before
                the link goes out to guests. */
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

/* ── 0 · the folded card ─────────────────────────────────────────── */
{
  const gate = $('#gate');
  const seal = $('#seal');

  const open = () => {
    root.classList.remove('is-sealed');
    root.classList.add('is-open');
  };

  const strike = () => {
    gate.remove();
    open();
  };

  if (calm) {
    strike();
  } else {
    let going = false;
    seal.addEventListener('click', () => {
      if (going) return;
      going = true;
      seal.disabled = true;
      /* the seal lifts (.5s) → the two leaves fold back (1.3s) →
         the whole layer dissolves onto the invitation behind it */
      gate.classList.add('is-lifting');
      setTimeout(() => gate.classList.add('is-unfolding'), 420);
      setTimeout(open, 1250);
      setTimeout(() => gate.classList.add('is-gone'), 1500);
      /* a fixed full-screen layer keeps swallowing taps even at
         opacity 0, so it has to leave the DOM */
      gate.addEventListener('transitionend', () => gate.remove(), { once: true });
      setTimeout(() => gate.isConnected && gate.remove(), 3000);
    });
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

/* ── 4 · map and calendar ────────────────────────────────────────── */
{
  const title = `زفاف ${CONFIG.couple}`;
  const where = `${CONFIG.venue}، ${CONFIG.city}`;

  $('#mapLink').href = CONFIG.mapsLink ||
    'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(CONFIG.mapsQuery);

  /* one .ics as a data URI covers iOS, Android and desktop alike —
     Google Calendar included, and with no third-party redirect */
  const ics = [
    'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//aseel-ibrahim//AR',
    'BEGIN:VEVENT',
    `DTSTART:${CONFIG.icsStart}`, `DTEND:${CONFIG.icsEnd}`,
    `SUMMARY:${title}`, `LOCATION:${where}`,
    'END:VEVENT', 'END:VCALENDAR',
  ].join('\r\n');
  const cal = $('#calLink');
  cal.href = 'data:text/calendar;charset=utf-8,' + encodeURIComponent(ics);
  cal.setAttribute('download', 'aseel-ibrahim.ics');
}

/* ── 5 · the reply ───────────────────────────────────────────────── */
{
  const form  = $('#rsvpForm');
  const name  = $('#rsvpName');
  const note  = $('#rsvpNote');
  const seats = $('#seatsField');
  const sOut  = $('#sOut'), sVal = $('#sVal');
  const minus = $('#sMinus'), plus = $('#sPlus');
  const errTop = $('#formErr'), errName = $('#nameErr'), errGo = $('#goErr');
  const btn = $('#sendBtn'), ctaText = $('#ctaText');
  const done = $('#rsvpDone'), doneSub = $('#doneSub'), waLink = $('#waLink');
  let n = 1, sent = false;

  const setSeats = (v) => {
    n = Math.min(MAX_SEATS, Math.max(1, v));
    sOut.textContent = ar(n);
    sVal.value = n;
    minus.disabled = n === 1;
    plus.disabled  = n === MAX_SEATS;
  };
  minus.addEventListener('click', () => setSeats(n - 1));
  plus .addEventListener('click', () => setSeats(n + 1));
  setSeats(1);

  const coming = () => (form.attending.value || '').startsWith('نعم');

  form.addEventListener('change', (e) => {
    if (e.target.name === 'attending') {
      seats.hidden = !coming();
      errGo.hidden = true;
    }
    if (e.target === name && name.value.trim()) errName.hidden = true;
  });

  const flag = (box, msg) => { box.textContent = msg; box.hidden = false; };

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
    done.focus();
  };

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (sent) return;
    errTop.hidden = errName.hidden = errGo.hidden = true;

    if (!name.value.trim()) {
      flag(errName, 'يرجى كتابة الاسم الكامل');
      name.focus();
      return;
    }
    if (!form.attending.value) {
      flag(errGo, 'يرجى اختيار أحد الخيارين');
      return;
    }

    /* With no endpoint there is nothing on GitHub Pages to POST to, so
       the reply is handed to WhatsApp instead. window.open has to run
       inside this handler, before any await, or the tap is spent and
       the popup blocker takes it. */
    if (!CONFIG.endpoint && CONFIG.whatsapp) {
      sent = true;
      window.open(waHref(), '_blank', 'noopener');
      settle();
      return;
    }
    if (!CONFIG.endpoint) { sent = true; settle(); return; }

    sent = true;
    btn.disabled = true;
    ctaText.textContent = 'جارٍ الإرسال…';

    try {
      const res = await fetch(CONFIG.endpoint, {
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

/* ── 6 · drifting gold dust ──────────────────────────────────────── */
if (!calm) {
  const cv = $('#motes');
  const ctx = cv.getContext('2d');
  let w, h;

  const size = () => {
    w = cv.width  = innerWidth  * devicePixelRatio;
    h = cv.height = innerHeight * devicePixelRatio;
  };
  size();
  addEventListener('resize', size);

  const N = Math.min(22, Math.floor(innerWidth / 46));
  const dust = Array.from({ length: N }, () => ({
    x: Math.random(), y: Math.random(),
    r: (0.9 + Math.random() * 2) * devicePixelRatio,
    vy: (0.005 + Math.random() * 0.012) / 100,
    vx: (Math.random() - 0.5) / 9000,
    p: Math.random() * Math.PI * 2,
  }));

  (function draw() {
    ctx.clearRect(0, 0, w, h);
    for (const m of dust) {
      m.y -= m.vy;
      m.x += m.vx + Math.sin(m.p += 0.0035) / 11000;
      if (m.y < -0.02) { m.y = 1.02; m.x = Math.random(); }
      ctx.beginPath();
      ctx.arc(m.x * w, m.y * h, m.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(168,135,85,${0.26 + Math.sin(m.p * 3) * 0.2})`;
      ctx.fill();
    }
    requestAnimationFrame(draw);
  })();
}
