const nfCache = {};
const fmt = (n, d = 1) =>
  Number.isFinite(n)
    ? (nfCache[d] ||= new Intl.NumberFormat('uz-UZ', { maximumFractionDigits: d })).format(n)
    : '—';
/* Harakat yoqilganmi? (GSAP bor va "harakatni kamaytirish" o‘chiq.) Har safar tekshiriladi. */
const motionOn = () => !!(window.gsap && window.Motion && window.Motion.ok());
const slider = (name, label, min, max, value, step = 1, unit = '') =>
  `<label class="sim-control"><span>${label}<output data-for="${name}">${value} ${unit}</output></span><input data-v="${name}" type="range" min="${min}" max="${max}" step="${step}" value="${value}" aria-label="${label}" data-unit="${unit}" style="--p:${(value - min) / (max - min)}"></label>`;
const numinput = (name, label, value) =>
  `<label class="sim-number"><span>${label}</span><input type="number" inputmode="numeric" min="1" max="100" step="1" data-v="${name}" value="${value}" aria-label="${label}"></label>`;
const metric = (label, value) =>
  `<div class="sim-metric${String(value).length > 18 ? ' is-long' : ''}"><span>${label}</span><strong>${value}</strong></div>`;
/* Shartli belgilar (HTML): ranglar CSS tokenlaridan — qarang 70-simulations.css */
const legendList = items =>
  items.length
    ? `<ul class="sim-legend" aria-label="Shartli belgilar">${items.map(([k, t]) => `<li><i class="${k}"></i>${t}</li>`).join('')}</ul>`
    : '';
function makeGraph({
  a = 100,
  b = 2,
  c = 20,
  d = 2,
  maxQ,
  maxP,
  areas = [],
  lines = [],
  marks = [],
  social,
  showSupply = true,
  description = 'Talab va taklif',
  axisX = 'Miqdor · birlik',
  axisY = 'Narx · shartli birlik',
  legend = [],
}) {
  maxQ = maxQ || Math.max(40, (a / b) * 1.05);
  maxP = maxP || Math.max(a * 1.1, c + 40);
  const L = 76,
    T = 35,
    W = 570,
    H = 302;
  const X = q => L + (q / maxQ) * W,
    Y = p => T + H - (p / maxP) * H;
  const coords = pts => pts.map(([q, p]) => `${X(q)},${Y(p)}`).join(' ');
  const lineCurve = (fn, cls) => {
    const p0 = fn(0),
      slope = (fn(maxQ) - p0) / maxQ,
      qs = [0, maxQ];
    if (slope !== 0) qs.push(-p0 / slope, (maxP - p0) / slope);
    const pts = qs
      .filter(q => q >= 0 && q <= maxQ && fn(q) >= -1e-7 && fn(q) <= maxP + 1e-7)
      .sort((x, y) => x - y)
      .filter((q, i, list) => i === 0 || Math.abs(q - list[i - 1]) > 1e-8)
      .map(q => [q, Math.max(0, Math.min(maxP, fn(q)))]);
    return `<polyline points="${coords(pts)}" class="cv ${cls}"/>`;
  };
  const grid = Array.from({ length: 5 }, (_, i) => {
    const q = (maxQ * i) / 4,
      p = (maxP * i) / 4;
    return `<path d="M${X(q)} ${T}V${T + H} M${L} ${Y(p)}H${L + W}" class="gr"/><text x="${X(q)}" y="${T + H + 22}" text-anchor="middle" class="tk">${fmt(q, 0)}</text><text x="${L - 13}" y="${Y(p) + 4}" text-anchor="end" class="tk">${fmt(p, 0)}</text>`;
  }).join('');
  const shade = areas.map(z => `<polygon points="${coords(z.points)}" class="ar ar-${z.tone}"/>`).join('');
  const extra = lines
    .map(
      l =>
        `<line x1="${X(l.x1 ?? 0)}" y1="${Y(l.p)}" x2="${X(l.x2 ?? maxQ)}" y2="${Y(l.p)}" class="rf${l.tone ? ` rf-${l.tone}` : ''}"/>${l.label ? `<text x="${L + W - 4}" y="${Y(l.p) - 7}" text-anchor="end" class="lb${l.tone ? ` lb-${l.tone}` : ''}">${esc(l.label)}</text>` : ''}`
    )
    .join('');
  const dots = marks
    .map(
      m =>
        `<path d="M${L} ${Y(m.p)}H${X(m.q)}V${Y(0)}" class="dl"/><circle cx="${X(m.q)}" cy="${Y(m.p)}" r="5" class="sim-dot"/>${m.label ? `<text x="${X(m.q) + (m.dx ?? 9)}" y="${Y(m.p) + (m.dy ?? -10)}" class="lb">${esc(m.label)}</text>` : ''}`
    )
    .join('');
  const keys = [
    ['lg-d', 'Talab'],
    ...(showSupply ? [['lg-s', 'Taklif / xususiy xarajat']] : []),
    ...(social !== undefined ? [['lg-soc', 'Ijtimoiy xarajat']] : []),
    ...legend,
  ];
  return `<svg class="sim-svg" viewBox="0 0 700 420" role="img" aria-label="${esc(description)}"><title>${esc(description)}</title>${grid}${shade}${extra}<path d="M${L} ${T - 7}V${T + H}H${L + W + 6}" class="ax"/>${lineCurve(q => a - b * q, 'cv-d')}${showSupply ? lineCurve(q => c + d * q, 'cv-s') : ''}${social !== undefined ? lineCurve(q => c + social + d * q, 'cv-soc') : ''}${dots}<text x="${L + W / 2}" y="${T + H + 52}" text-anchor="middle" class="at at-x">${esc(axisX)}</text><text x="${L}" y="${T - 12}" class="at">${esc(axisY)}</text></svg>${legendList(keys)}`;
}
function simplePPF({ x = 50, growth = 1, inefficient = false, opportunity = false }) {
  const L = 75,
    T = 35,
    W = 570,
    H = 290;
  const X = v => L + (v / 130) * W,
    Y = v => T + H - (v / 160) * H;
  const yval = v => 120 * growth * (1 - (v / (100 * growth)) ** 2);
  const pts = Array.from({ length: 81 }, (_, i) => {
    const q = (i / 80) * 100 * growth;
    return `${X(q)},${Y(yval(q))}`;
  }).join(' ');
  const oldpts = Array.from({ length: 81 }, (_, i) => {
    const q = (i / 80) * 100;
    return `${X(q)},${Y(120 * (1 - (q / 100) ** 2))}`;
  }).join(' ');
  const selQ = Math.min(x, 100 * growth),
    selY = yval(selQ) * (inefficient ? 0.65 : 1);
  const gridY = [0, 40, 80, 120],
    gridX = [0, 50, 100];
  return `<svg class="sim-svg" viewBox="0 0 700 405" role="img" aria-label="Ishlab chiqarish imkoniyatlari chegarasi va tanlangan nuqta"><title>Ishlab chiqarish imkoniyatlari chegarasi</title>${gridY.map(v => `<path d="M${L} ${Y(v)}H${L + W}" class="gr gx"/>`).join('')}${gridX.map(v => `<path d="M${X(v)} ${T}V${T + H}" class="gr gx"/>`).join('')}<path d="M${L} ${T}V${T + H}H${L + W}" class="ax"/>${gridY.map(v => `<text x="${L - 12}" y="${Y(v) + 4}" text-anchor="end" class="tk">${v}</text>`).join('')}${gridX.map(v => `<text x="${X(v)}" y="${T + H + 23}" text-anchor="middle" class="tk">${v}</text>`).join('')}<polyline points="${oldpts}" class="ol"/><polyline points="${pts}" class="cv cv-acc"/><path d="M${L} ${Y(selY)}H${X(selQ)}V${T + H}" class="dl"/><circle cx="${X(selQ)}" cy="${Y(selY)}" r="6" class="sim-dot${inefficient ? ' is-warn' : ''}"/><text x="${X(selQ) + (selQ > 65 ? -12 : 12)}" y="${Y(selY) - 12}" text-anchor="${selQ > 65 ? 'end' : 'start'}" class="lb">${inefficient ? 'Resurs to‘liq ishlatilmagan' : 'Chegaradagi tanlov'}</text><text x="350" y="372" text-anchor="middle" class="at at-x">Kompyuterlar · dona</text><text x="${L}" y="${T - 12}" class="at">Avtomobillar · dona</text></svg>${legendList(
    [
      ['lg-acc', 'Ishlab chiqarish imkoniyatlari chegarasi'],
      ['lg-ref', 'Dastlabki chegara'],
    ]
  )}`;
}
/* Qatlamlar: [data-for] qiymati, jonli sinov (tween), pulsatsiya. Hisob-kitob (compute) o‘zgarmagan. */
function patchMetrics(el, html) {
  const t = document.createElement('template');
  t.innerHTML = html;
  const next = t.content.children,
    cur = el.children;
  if (cur.length !== next.length) {
    el.innerHTML = html;
    return;
  }
  for (let i = 0; i < next.length; i++) {
    const a = cur[i],
      b = next[i];
    if (a.className !== b.className) a.className = b.className;
    const al = a.firstElementChild,
      bl = b.firstElementChild,
      av = a.lastElementChild,
      bv = b.lastElementChild;
    if (al.textContent !== bl.textContent) al.textContent = bl.textContent;
    if (av.textContent !== bv.textContent) av.textContent = bv.textContent;
  }
}
function simShell(host, title, controls, compute) {
  const intro = host.innerHTML;
  host.innerHTML = `<div class="sim-heading"><span>Interaktiv model</span><h3>${title}</h3></div><div class="sim-intro">${intro}</div><div class="sim-controls">${controls}</div><div class="sim-chart"></div><div class="sim-metrics" aria-live="polite"></div><p class="sim-reading" aria-live="polite"></p><p class="sim-note">O‘quv uchun tuzilgan soddalashtirilgan misol. Chizmadagi raqamlar haqiqiy bozor prognozi emas.</p>`;
  const live = [host.querySelector('.sim-metrics'), host.querySelector('.sim-reading')],
    rangeKeys = Array.from(host.querySelectorAll('input[type="range"][data-v]')).map(el => el.dataset.v),
    disp = {}; /* ekranda ko‘rinayotgan (tweenlanayotgan) slayder qiymatlari */
  let lastKey, target, tween;
  const busy = on =>
    live.forEach(el => (on ? el.setAttribute('aria-busy', 'true') : el.removeAttribute('aria-busy')));
  /* mid=true: tween o‘rtasida faqat chizma va raqamlar yangilanadi, izoh matni oxirida. */
  const paint = (v, mid) => {
    host._mid = mid;
    compute(v, host);
    host._mid = false;
  };
  const halt = () => {
    if (tween) {
      tween.kill();
      tween = null;
    }
    busy(false);
  };
  const pulse = () => {
    if (!motionOn()) return;
    host.querySelectorAll('.sim-chart .sim-dot').forEach(dot => {
      /* SVG ichida aniq markaz (cx, cy) atrofida kattalashadi. */
      window.gsap.set(dot, { svgOrigin: `${dot.getAttribute('cx')} ${dot.getAttribute('cy')}` });
      window.gsap.fromTo(
        dot,
        { scale: 1.65 },
        { scale: 1, duration: 0.55, ease: 'back.out(2.4)', clearProps: 'transform', overwrite: 'auto' }
      );
    });
  };
  const finish = () => {
    tween = null;
    rangeKeys.forEach(k => (disp[k] = target[k]));
    paint(target, false);
    busy(false);
    pulse();
  };
  /* Tashqaridan (Motion 'settle', bobdan chiqish): tweenni darhol aniq qiymatga keltiradi. */
  host.__sim = {
    settle() {
      if (!tween) return;
      tween.kill();
      finish();
    },
  };
  const update = () => {
    const v = {};
    let invalid = false;
    host.querySelectorAll('[data-v]').forEach(el => {
      if (el.type === 'number') {
        const n = Number(el.value);
        const bad = el.value === '' || !Number.isInteger(n) || n < 1 || n > 100;
        invalid = invalid || bad;
        el.setAttribute('aria-invalid', String(bad));
      }
      v[el.dataset.v] =
        el.type === 'checkbox' ? el.checked : el.tagName === 'SELECT' ? el.value : Number(el.value);
      if (el.type === 'range') {
        v[el.dataset.v] = Number(el.value);
        const o = host.querySelector(`[data-for="${el.dataset.v}"]`);
        if (o) o.textContent = fmt(v[el.dataset.v], 2) + ' ' + (el.dataset.unit || '');
        el.style.setProperty('--p', String((el.value - el.min) / (el.max - el.min)));
      }
    });
    if (invalid) {
      halt();
      lastKey = host._chart = host._reading = undefined;
      host.querySelector('.sim-chart').innerHTML =
        '<p class="sim-note">Hisoblash uchun barcha ishlab chiqarish tezliklarini kiriting.</p>';
      host.querySelector('.sim-metrics').innerHTML = '';
      host.querySelector('.sim-reading').textContent =
        'Har bir tezlik 1 dan 100 gacha bo‘lgan musbat butun son bo‘lsin.';
      return;
    }
    const key = JSON.stringify(v);
    if (key === lastKey) return;
    const first = lastKey === undefined;
    lastKey = key;
    target = v;
    const moved = rangeKeys.some(k => disp[k] !== v[k]);
    if (first || !moved || !motionOn()) {
      halt();
      rangeKeys.forEach(k => (disp[k] = v[k]));
      paint(v, false);
      if (!first) pulse();
      return;
    }
    /* Slayder harakati: ko‘rsatilayotgan holat maqsadga ~0,35 s da silliq yaqinlashadi. */
    busy(true);
    const goal = {};
    rangeKeys.forEach(k => (goal[k] = v[k]));
    tween = window.gsap.to(disp, {
      ...goal,
      duration: 0.35,
      ease: 'power3.out',
      overwrite: true,
      onUpdate: () => paint({ ...target, ...disp }, true),
      onComplete: finish,
    });
  };
  host.addEventListener('input', update);
  host.addEventListener('change', update);
  update();
}
const setSim = (h, chart, metrics, reading) => {
  if (h._chart !== chart) h.querySelector('.sim-chart').innerHTML = h._chart = chart;
  patchMetrics(h.querySelector('.sim-metrics'), metrics);
  if (!h._mid && h._reading !== reading) h.querySelector('.sim-reading').innerHTML = h._reading = reading;
};
function mountSimulations(root) {
  root.querySelectorAll('[data-interactive]').forEach(h => {
    if (h.dataset.mounted === 'true') return;
    h.dataset.mounted = 'true';
    const type = h.dataset.interactive;
    if (type === 'opportunity')
      simShell(
        h,
        'Bir tanlovning muqobil xarajati',
        slider('hours', 'O‘qishga ajratilgan vaqt', 0, 4, 2, 0.5, 'soat'),
        v => {
          const oc = v.hours * 40,
            earn = (4 - v.hours) * 40;
          const gx = [76, 213.5, 351, 488.5, 626],
            sx = 76 + (v.hours / 4) * 550,
            sy = 285 - (earn / 160) * 240;
          const svg = `<svg class="sim-svg" viewBox="0 0 700 365" role="img" aria-label="O‘qish va ish daromadi o‘rtasidagi tanlov"><title>O‘qish va ishlash uchun 4 soat</title>${gx.map(x => `<path d="M${x} 35V285" class="gr gx"/>`).join('')}${[45, 165, 285].map(y => `<path d="M76 ${y}H646" class="gr gx"/>`).join('')}<path d="M76 35V285H646" class="ax"/><path d="M76 45L626 285" class="cv cv-acc"/><path d="M76 ${sy}H${sx}V285" class="dl"/><circle cx="${sx}" cy="${sy}" r="6" class="sim-dot is-warn"/><text x="76" y="315" text-anchor="middle" class="tk">0</text><text x="213.5" y="315" text-anchor="middle" class="tk gx">1</text><text x="351" y="315" text-anchor="middle" class="tk gx">2</text><text x="488.5" y="315" text-anchor="middle" class="tk gx">3</text><text x="626" y="315" text-anchor="middle" class="tk">4</text><text x="63" y="49" text-anchor="end" class="tk">160</text><text x="63" y="169" text-anchor="end" class="tk gx">80</text><text x="63" y="289" text-anchor="end" class="tk gx">0</text><text x="360" y="348" text-anchor="middle" class="at at-x">O‘qish · soat</text><text x="76" y="23" class="at">Ishdan daromad · ming so‘m</text></svg>`;
          setSim(
            h,
            svg,
            metric('O‘qish vaqti', fmt(v.hours) + ' soat') +
              metric('Voz kechilgan ish daromadi', fmt(oc) + ' ming so‘m') +
              metric('Qolgan vaqtdagi daromad', fmt(earn) + ' ming so‘m'),
            `Faraz: bo‘sh vaqtingiz <strong>4 soat</strong>, muqobil ish haqi <strong>40 ming so‘m/soat</strong>. O‘qishga sarflangan ${fmt(v.hours)} soatning muqobil xarajati ${fmt(oc)} ming so‘m. O‘qishning kelajakdagi foydasi bu misolda pulga baholanmagan.`
          );
        }
      );
    else if (type === 'ppf')
      simShell(
        h,
        'Imkoniyat, samaradorlik va o‘sish',
        slider('x', 'Kompyuter ishlab chiqarish', 0, 100, 50, 5, 'dona') +
          slider('growth', 'Resurs / texnologiya indeksi', 1, 1.3, 1, 0.05, 'baravar') +
          '<label class="sim-check"><input type="checkbox" role="switch" data-v="inefficient"> Resurslarning bir qismi bekor tursin</label>',
        v => {
          const ymax = 120 * v.growth * (1 - (v.x / (100 * v.growth)) ** 2),
            y = ymax * (v.inefficient ? 0.65 : 1);
          const extra = Math.min(10, Math.max(0, 100 * v.growth - v.x)),
            next = v.x + extra,
            oc = ymax - 120 * v.growth * (1 - (next / (100 * v.growth)) ** 2);
          setSim(
            h,
            simplePPF(v),
            metric('Kompyuter', fmt(v.x) + ' dona') +
              metric('Avtomobil', fmt(y) + ' dona') +
              metric(
                extra > 0 ? `Chegarada yana ${fmt(extra)} kompyuter` : 'Yana kompyuter ishlab chiqarish',
                extra > 0 ? fmt(oc) + ' avtomobil' : 'Bu chegarada imkonsiz'
              ),
            v.inefficient
              ? 'Nuqta chegara ichida: mavjud imkoniyatdan to‘liq foydalanilmagan. Resursni ishga solib, ikkala mahsulotni ham ko‘paytirish mumkin. Ko‘rsatilgan qo‘shimcha kompyuter xarajati to‘liq foydalanish chegarasiga tegishli.'
              : 'Nuqta chegarada: kompyuter ko‘payishi avtomobilning kamayishini talab qiladi. Kompyuter miqdori katta bo‘lganda yana 10 ta ishlab chiqarishning muqobil xarajati ortadi. Indeks oshishi butun chegarani kengaytiradi.'
          );
        }
      );
    else if (type === 'advantage')
      simShell(
        h,
        'Kim nimada nisbatan ustun?',
        numinput('ab', 'Ali: non / soat', 12) +
          numinput('as', 'Ali: ko‘ylak / soat', 3) +
          numinput('bb', 'Vali: non / soat', 6) +
          numinput('bs', 'Vali: ko‘ylak / soat', 2),
        v => {
          const ac = v.ab / v.as,
            bc = v.bb / v.bs,
            equal = Math.abs(ac - bc) < 1e-8,
            shirt = ac < bc ? 'Ali' : 'Vali',
            bread = ac > bc ? 'Ali' : 'Vali';
          const table = `<div class="table-wrap"><table><thead><tr><th>Imkoniyat xarajati</th><th>Ali</th><th>Vali</th></tr></thead><tbody><tr><td>1 ko‘ylak uchun voz kechiladigan non</td><td>${fmt(ac, 3)}</td><td>${fmt(bc, 3)}</td></tr><tr><td>1 non uchun voz kechiladigan ko‘ylak</td><td>${fmt(1 / ac, 3)}</td><td>${fmt(1 / bc, 3)}</td></tr></tbody></table></div>`;
          setSim(
            h,
            table,
            metric('Ko‘ylakda nisbiy ustun', equal ? 'Hech kim' : shirt) +
              metric('Nonda nisbiy ustun', equal ? 'Hech kim' : bread) +
              metric(
                'Manfaatli savdo narxi',
                equal
                  ? 'Oraliq yo‘q'
                  : `${fmt(Math.min(ac, bc), 3)} < P < ${fmt(Math.max(ac, bc), 3)} non/ko‘ylak`
              ),
            equal
              ? 'Ikkala imkoniyat xarajati teng. Ushbu doimiy unumdorlik modelida nisbiy ustunlikka asoslangan savdo foydasi yo‘q.'
              : 'Ko‘ylakni eng kam nondan voz kechib chiqaradigan tomon ko‘ylakda nisbiy ustun. Mutlaq ustunlik uchun esa soatiga ishlab chiqarilgan miqdorni bevosita taqqoslang. Oraliqning ichidagi narx ikkala tomon uchun ham o‘z ishlab chiqarishidan arzonroq almashuv beradi.'
          );
        }
      );
    else if (type === 'market')
      simShell(
        h,
        'Talab va taklif siljisa nima bo‘ladi?',
        slider('da', 'Talabning siljishi', -30, 40, 0, 5) +
          slider('dc', 'Taklif xarajatining o‘zgarishi', -15, 30, 0, 5) +
          slider('price', 'Tekshiriladigan narx', 10, 130, 60, 5),
        v => {
          const a = 100 + v.da,
            c = 20 + v.dc,
            q = (a - c) / 4,
            p = a - 2 * q,
            qd = Math.max(0, (a - v.price) / 2),
            qs = Math.max(0, (v.price - c) / 2),
            gap = qd - qs;
          setSim(
            h,
            makeGraph({
              a,
              c,
              maxP: 160,
              maxQ: 75,
              marks: [{ q, p, label: 'E' }],
              lines: [{ p: v.price, label: 'Tanlangan narx' }],
            }),
            metric('Muvozanat narxi', fmt(p)) +
              metric('Muvozanat miqdori', fmt(q)) +
              metric(
                gap > 0 ? 'Tanqislik' : gap < 0 ? 'Ortiqcha taklif' : 'Bozor muvozanatda',
                fmt(Math.abs(gap)) + ' birlik'
              ),
            `Talab miqdori: <strong>${fmt(qd)}</strong>; taklif miqdori: <strong>${fmt(qs)}</strong>. ${gap > 0 ? 'Xaridorlar sotuvchilardan ko‘proq mahsulot xohlaydi; narxga yuqoriga bosim paydo bo‘ladi.' : gap < 0 ? 'Sotuvchilar xaridorlardan ko‘proq mahsulot taklif qiladi; narxga pastga bosim paydo bo‘ladi.' : 'Talab va taklif miqdorlari teng.'} Birinchi ikki boshqaruv egri chiziqni siljitadi; oxirgisi mavjud chiziqlar bo‘ylab miqdorni o‘zgartiradi.`
          );
        }
      );
    else if (type === 'elasticity')
      simShell(
        h,
        'Bir chiziq, turli elastiklik',
        slider('p0', 'Boshlang‘ich narx', 5, 95, 60, 5) + slider('p1', 'Yangi narx', 5, 95, 70, 5),
        v => {
          const q0 = (100 - v.p0) / 2,
            q1 = (100 - v.p1) / 2,
            dp = (v.p1 - v.p0) / ((v.p1 + v.p0) / 2),
            dq = (q1 - q0) / ((q1 + q0) / 2),
            ed = dp === 0 ? NaN : Math.abs(dq / dp),
            tr0 = v.p0 * q0,
            tr1 = v.p1 * q1;
          setSim(
            h,
            makeGraph({
              showSupply: false,
              c: 200,
              d: 2,
              maxQ: 55,
              maxP: 110,
              marks: [
                { q: q0, p: v.p0, label: 'A' },
                { q: q1, p: v.p1, label: 'B' },
              ],
              areas: [
                {
                  points: [
                    [0, 0],
                    [q1, 0],
                    [q1, v.p1],
                    [0, v.p1],
                  ],
                  tone: 'c',
                },
              ],
              legend: [['lg-c', 'Yangi tushum']],
            }),
            metric('O‘rta nuqta elastikligi', fmt(ed, 2)) +
              metric('Boshlang‘ich tushum', fmt(tr0)) +
              metric('Yangi tushum', fmt(tr1)),
            dp === 0
              ? 'Narxlar bir xil: ikki nuqta bo‘yicha foiz o‘zgarishlar nisbati 0/0, elastiklikni shu ikkita bir xil nuqtadan hisoblab bo‘lmaydi.'
              : `ΔP = ${fmt(dp * 100, 2)}%; ΔQ = ${fmt(dq * 100, 2)}%; |ΔQ% / ΔP%| = <strong>${fmt(ed, 2)}</strong>. Bu oraliqda talab ${ed > 1.001 ? 'elastik' : ed < 0.999 ? 'noelastik' : 'birlik elastik'}. Tushum ${fmt(tr1 - tr0)} ga o‘zgardi. Chiziq qiyaligi bir xil bo‘lsa ham foiz asoslari o‘zgargani uchun elastiklik o‘zgaradi.`
          );
        }
      );
    else if (type === 'controls')
      simShell(
        h,
        'Narx nazorati qachon ta’sir qiladi?',
        '<label class="sim-control"><span>Siyosat turi</span><span class="sim-select"><select data-v="policy" aria-label="Siyosat turi"><option value="ceiling">Maksimal narx — yuqori chegara</option><option value="floor">Minimal narx — quyi chegara</option></select></span></label>' +
          slider('p', 'Belgilangan chegara', 10, 110, 40, 5),
        v => {
          const binding = v.policy === 'ceiling' ? v.p < 60 : v.p > 60,
            p = binding ? v.p : 60,
            qd = Math.max(0, (100 - p) / 2),
            qs = Math.max(0, (p - 20) / 2),
            gap = qd - qs,
            traded = Math.min(qd, qs);
          setSim(
            h,
            makeGraph({
              maxQ: 55,
              maxP: 120,
              lines: [
                {
                  p: v.p,
                  label: v.policy === 'ceiling' ? 'Maksimal narx' : 'Minimal narx',
                  tone: 'soc',
                },
              ],
              marks: binding
                ? [
                    { q: 20, p: 60, label: 'Erkin bozor E' },
                    { q: traded, p, label: 'Savdo miqdori' },
                  ]
                : [{ q: 20, p: 60, label: 'Erkin bozor E' }],
            }),
            metric('Chegara', binding ? 'Majburiy / ta’sirli' : 'Ta’sirsiz') +
              metric('Savdo miqdori', fmt(traded)) +
              metric(gap >= 0 ? 'Tanqislik' : 'Ortiqcha taklif', fmt(Math.abs(gap))),
            binding
              ? `Belgilangan narxda Qd=${fmt(qd)}, Qs=${fmt(qs)}. ${gap > 0 ? 'Taklif yetishmaydi; mahsulot navbat, tanish-bilish yoki boshqa usulda taqsimlanishi mumkin.' : 'Xaridorlar taklifning hammasini sotib olmaydi.'} Davlat ortiqchani sotib olmasligi, qora bozor yo‘qligi va savdo qisqa tomon bilan cheklanishi faraz qilingan.`
              : 'Chegara erkin bozor muvozanatini taqiqlamaydi. Natija P=60, Q=20 bo‘lib qoladi; qog‘ozda mavjud cheklov har doim bozorga ta’sir qilavermaydi.'
          );
        }
      );
    else if (type === 'welfare')
      simShell(h, 'Samarali miqdor qayerda?', slider('q', 'Ishlab chiqarilgan miqdor', 0, 38, 20, 1), v => {
        const total = 80 * v.q - 2 * v.q * v.q,
          missed = 800 - total,
          polys = [];
        if (v.q <= 20)
          polys.push({
            points: [
              [0, 20],
              [0, 100],
              [v.q, 100 - 2 * v.q],
              [v.q, 20 + 2 * v.q],
            ],
            tone: 'c',
          });
        else {
          polys.push({
            points: [
              [0, 20],
              [0, 100],
              [20, 60],
            ],
            tone: 'c',
          });
          polys.push({
            points: [
              [20, 60],
              [v.q, 20 + 2 * v.q],
              [v.q, 100 - 2 * v.q],
            ],
            tone: 'loss',
          });
        }
        setSim(
          h,
          makeGraph({
            maxQ: 50,
            maxP: 120,
            areas: polys,
            marks: [{ q: 20, p: 60, label: 'Samarali E' }],
            legend: [['lg-c', 'Umumiy yutuq'], ...(v.q > 20 ? [['lg-loss', 'Yo‘qotilgan yutuq']] : [])],
          }),
          metric('Jami foyda − jami xarajat', fmt(total)) +
            metric('Eng katta umumiy yutuq', 800) +
            metric('Yo‘qotilgan yutuq', fmt(missed)),
          v.q < 20
            ? 'Qo‘shimcha birlikning xaridor uchun bahosi ishlab chiqarish xarajatidan yuqori. Miqdorni oshirish umumiy yutuqni oshiradi.'
            : v.q > 20
              ? '20 birlikdan keyin qo‘shimcha birlikning xarajati uning xaridor uchun bahosidan yuqori. Bunday birliklar majburan ishlab chiqarilsa, umumiy yutuq kamayadi.'
              : 'Talab va taklif kesishgan miqdorda umumiy yutuq eng katta. Faraz: xaridor qiymati talab bilan, barcha ijtimoiy xarajat esa taklif bilan to‘liq ifodalanadi. Tashqi ta’sirlar bo‘lsa, bu xulosa o‘zgaradi.'
        );
      });
    else if (type === 'tax')
      simShell(
        h,
        'Soliq yukini kim ko‘taradi?',
        slider('t', 'Bir birlik uchun soliq', 0, 75, 20, 5) +
          slider('b', 'Talab qiyaligi |ΔP / ΔQ|', 0.5, 4, 2, 0.5) +
          slider('d', 'Taklif qiyaligi ΔP / ΔQ', 0.5, 4, 2, 0.5),
        v => {
          const q0 = 80 / (v.b + v.d),
            p0 = 100 - v.b * q0,
            q = Math.max(0, (80 - v.t) / (v.b + v.d)),
            pb = 100 - v.b * q,
            ps = 20 + v.d * q,
            revenue = v.t * q,
            dwl = 0.5 * v.t * (q0 - q);
          setSim(
            h,
            makeGraph({
              b: v.b,
              d: v.d,
              maxQ: Math.max(45, q0 * 1.6),
              maxP: 115,
              marks:
                v.t === 0
                  ? [{ q: q0, p: p0, label: 'E' }]
                  : [
                      { q: q0, p: p0, label: 'E', dx: -24 },
                      { q, p: pb, label: 'Pb', dy: -12 },
                      { q, p: ps, label: 'Ps', dy: 20 },
                    ],
              areas: [
                {
                  points: [
                    [0, ps],
                    [q, ps],
                    [q, pb],
                    [0, pb],
                  ],
                  tone: 'rev',
                },
                {
                  points: [
                    [q, ps],
                    [q, pb],
                    [q0, p0],
                  ],
                  tone: 'loss',
                },
              ],
              legend:
                v.t > 0
                  ? [
                      ['lg-rev', 'Soliq tushumi'],
                      ['lg-loss', 'Sof yo‘qotish'],
                    ]
                  : [],
            }),
            metric('Xaridor / sotuvchi narxi', `${fmt(pb)} / ${fmt(ps)}`) +
              metric('Soliq tushumi', fmt(revenue)) +
              metric('Sof yo‘qotish', fmt(dwl)),
            `Xaridor yuki: <strong>${fmt(pb - p0)}</strong> (${fmt((v.b / (v.b + v.d)) * 100)}%); sotuvchi yuki: <strong>${fmt(p0 - ps)}</strong> (${fmt((v.d / (v.b + v.d)) * 100)}%). Savdo ${fmt(q0)} dan ${fmt(q)} ga kamaydi. Berilgan bir xil o‘q birliklarida teskari talabning qiyaligi kattalashsa, u nisbatan noelastik bo‘ladi va xaridor ulushi ortadi. Qonuniy soliq to‘lovchisini o‘zgartirish bu hisobni o‘zgartirmaydi.`
          );
        }
      );
    else if (type === 'trade')
      simShell(
        h,
        'Jahon narxi va import boji',
        slider('pw', 'Jahon narxi', 25, 95, 40, 5) + slider('t', 'Import boji / birlik', 0, 40, 10, 5),
        v => {
          const importer = v.pw < 60,
            neutral = v.pw === 60,
            p = importer ? Math.min(60, v.pw + v.t) : v.pw,
            qd = Math.max(0, (100 - p) / 2),
            qs = Math.max(0, (p - 20) / 2),
            net = qd - qs,
            revenue = importer ? (p - v.pw) * Math.max(0, net) : 0,
            cs = 0.5 * (100 - p) * qd,
            ps = 0.5 * (p - 20) * qs,
            freeQd = (100 - v.pw) / 2,
            freeQs = (v.pw - 20) / 2,
            freeTotal = 0.5 * (100 - v.pw) * freeQd + 0.5 * (v.pw - 20) * freeQs,
            dwl = freeTotal - (cs + ps + revenue);
          setSim(
            h,
            makeGraph({
              maxQ: 50,
              maxP: 115,
              lines: [
                { p: v.pw, label: 'Jahon narxi' },
                { p, label: 'Ichki narx', tone: 'soc' },
              ],
              areas: [
                {
                  points: [
                    [0, p],
                    [0, 100],
                    [qd, p],
                  ],
                  tone: 'c',
                },
                {
                  points: [
                    [0, 20],
                    [0, p],
                    [qs, p],
                  ],
                  tone: 'p',
                },
                ...(importer && revenue > 0
                  ? [
                      {
                        points: [
                          [qs, v.pw],
                          [qd, v.pw],
                          [qd, p],
                          [qs, p],
                        ],
                        tone: 'rev',
                      },
                    ]
                  : []),
              ],
              legend: [
                ['lg-c', 'Iste’molchi ortiqchasi (CS)'],
                ['lg-p', 'Ishlab chiqaruvchi ortiqchasi (PS)'],
                ...(importer && revenue > 0 ? [['lg-rev', 'Davlat boj tushumi']] : []),
              ],
            }),
            metric(
              neutral ? 'Savdo hajmi' : net >= 0 ? 'Import' : 'Eksport',
              fmt(Math.abs(net)) + ' birlik'
            ) +
              metric('Davlat boj tushumi', fmt(revenue)) +
              metric('Bojning sof yo‘qotishi', fmt(Math.max(0, dwl))),
            `CS=${fmt(cs)}, PS=${fmt(ps)}. ${importer ? 'Jahon narxi ichki savdosiz narxdan past. Boj ichki narxni ko‘taradi, importni qisqartiradi; yetarlicha katta bo‘lsa, import to‘xtaydi.' : neutral ? 'Jahon narxi savdosiz ichki narxga teng. Ushbu modelda import ham, eksport ham boshlanmaydi.' : 'Mamlakat eksportchi. Bu modeldagi import boji eksport narxiga qo‘llanmaydi.'} Faraz: mamlakat kichik, jahon narxini o‘zgartira olmaydi; transport xarajati va tashqi ta’sirlar yo‘q.`
          );
        }
      );
    else if (type === 'externality')
      simShell(
        h,
        'Xususiy xarajat va jamiyat xarajati',
        slider('e', 'Bir birlikning tashqi zarari', 0, 60, 20, 5) +
          '<label class="sim-check"><input type="checkbox" role="switch" data-v="corrective"> Tashqi zararga teng tuzatuvchi soliq qo‘llash</label>',
        v => {
          const qm = 20,
            qs = (80 - v.e) / 4,
            q = v.corrective ? qs : qm,
            dwl = 0.5 * v.e * (qm - qs),
            harm = v.e * q,
            net = (80 - v.e) * q - 2 * q * q;
          setSim(
            h,
            makeGraph({
              social: v.e > 0 ? v.e : undefined,
              maxP: 170,
              maxQ: 55,
              marks:
                v.e === 0
                  ? [{ q: qm, p: 60, label: 'E' }]
                  : [
                      { q: qm, p: 60, label: 'Bozor', dy: 22 },
                      {
                        q: qs,
                        p: 100 - 2 * qs,
                        label: 'Optimum',
                        dx: -65,
                        dy: -12,
                      },
                    ],
              areas: v.corrective
                ? []
                : [
                    {
                      points: [
                        [qs, 100 - 2 * qs],
                        [qm, 60],
                        [qm, 60 + v.e],
                      ],
                      tone: 'loss',
                    },
                  ],
              legend: !v.corrective && v.e > 0 ? [['lg-loss', 'Samarasizlik yo‘qotishi']] : [],
            }),
            metric('Amaldagi miqdor', fmt(q)) +
              metric('Jami tashqi zarar', fmt(harm)) +
              metric('Samarasizlik yo‘qotishi', fmt(v.corrective ? 0 : dwl)),
            `Ijtimoiy maqbul miqdor: <strong>${fmt(qs)}</strong>. Jami tashqi zarar <strong>${fmt(harm)}</strong> bilan sof samaradorlik yo‘qotishi bir xil emas. ${v.corrective ? 'Soliq tashqi zararni qarorga kiritdi: ishlab chiqarish ijtimoiy optimumga tushdi. Soliq tushumi transfer bo‘lib, sof farovonlik hisobida jamiyatdan yo‘qolgan pul deb qaralmaydi.' : 'Sotuvchi tashqi zararni hisobga olmasa, bozor ortiqcha ishlab chiqaradi. To‘q sariq uchburchak aynan ortiqcha birliklarning sof yo‘qotishini ko‘rsatadi.'}`
          );
        }
      );
    else h.innerHTML = '<p>Ushbu model bobdagi izohli chizmalarda ko‘rsatilgan.</p>';
  });
}
