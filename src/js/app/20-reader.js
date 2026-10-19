let navigationSerial = 0,
  renderedChapter = null,
  modelPromise = null;
const chapterTemplates = new Map(),
  chapterRequests = new Map();
const pad2 = n => String(n).padStart(2, '0');
const rdIcon = name => `<svg class="rd-ico" aria-hidden="true"><use href="#rd-${name}"/></svg>`;
/* Tugma matni: yorliq <span class="qb-label"> ichida bo‘lsa, ikonka saqlanadi. */
function setLabel(btn, text) {
  const label = btn.querySelector('.qb-label, .cb-label');
  if (label) label.textContent = text;
  else btn.textContent = text;
  btn.title = text;
}
const prefersReducedMotion = () => !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
async function getChapterTemplate(c) {
  const inline = document.getElementById(`template-${c.id}`);
  if (inline) return inline.content;
  if (chapterTemplates.has(c.id)) return chapterTemplates.get(c.id);
  if (!chapterRequests.has(c.id)) {
    const request = fetch(c.contentUrl)
      .then(async r => {
        if (!r.ok) throw new Error('Chapter unavailable');
        const t = document.createElement('template');
        t.innerHTML = await r.text();
        chapterTemplates.set(c.id, t.content);
        return t.content;
      })
      .catch(e => {
        chapterRequests.delete(c.id);
        throw e;
      });
    chapterRequests.set(c.id, request);
  }
  return chapterRequests.get(c.id);
}
function ensureModels() {
  if (typeof mountSimulations === 'function') return Promise.resolve();
  if (!modelPromise)
    modelPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = SIM_SCRIPT_URL;
      script.onload = resolve;
      script.onerror = () => {
        script.remove();
        modelPromise = null;
        reject(new Error('Model unavailable'));
      };
      document.head.append(script);
    });
  return modelPromise;
}
function attachModels(c, anchor) {
  if (typeof mountSimulations === 'function') {
    mountSimulations($('#chapter-content'));
    emit('models:mounted', { container: $('#chapter-content') });
    return;
  }
  const host = $('#chapter-content [data-interactive]');
  if (!host) return;
  const pending = document.createElement('p');
  pending.className = 'source-note model-pending';
  pending.textContent = 'Interaktiv model yuklanmoqda…';
  host.before(pending);
  ensureModels()
    .then(() => {
      if (activeChapter?.id !== c.id || renderedChapter !== c.id) {
        pending.remove();
        return;
      }
      const target = anchor ? document.getElementById(anchor) : null,
        top = target?.getBoundingClientRect().top;
      pending.remove();
      mountSimulations($('#chapter-content'));
      emit('models:mounted', { container: $('#chapter-content') });
      if (target && top > -120 && top < innerHeight)
        window.scrollBy({
          top: target.getBoundingClientRect().top - top,
          behavior: 'instant',
        });
      updateProgress();
    })
    .catch(() => {
      if (!pending.isConnected) return;
      pending.textContent = 'Model yuklanmadi. Internet aloqasini tekshirib, qayta urinib ko‘ring. ';
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'quiet-button';
      b.textContent = 'Qayta yuklash';
      b.addEventListener('click', () => {
        pending.remove();
        attachModels(c, anchor);
      });
      pending.append(b);
    });
}
function applyAnchor(anchor, same) {
  if (anchor) {
    const target = document.getElementById(anchor);
    if (target) {
      if (presentation) {
        slideIndex = activeSections.findIndex(s => s.contains(target) || s === target);
        showSlide(Math.max(0, slideIndex));
      }
      target.closest('details')?.setAttribute('open', '');
      target.scrollIntoView({
        behavior: same && !prefersReducedMotion() ? 'smooth' : 'instant',
        block: 'start',
      });
      emit('anchor:jump', { target });
    }
  } else if (!same) window.scrollTo({ top: 0, behavior: 'instant' });
  updateProgress();
}
function chapterEndHTML(id) {
  const done = finished.includes(id),
    prev = CHAPTERS.find(c => c.id === id - 1),
    next = CHAPTERS.find(c => c.id === id + 1);
  const card = (cls, href, kicker, title, icon, after) =>
    `<a class="end-card ${cls}" href="${href}"><small>${after ? kicker + icon : icon + kicker}</small><span class="end-title">${title}</span></a>`;
  return `<p class="end-note">Endi shu bobning asosiy g‘oyasini kitobga qaramay, o‘z so‘zingiz bilan tushuntirib ko‘ring.</p><button type="button" class="complete-button ${done ? 'is-complete' : ''}" data-complete="${id}" aria-pressed="${done}">${rdIcon('check')}<span class="cb-label">${done ? 'Bob o‘qib chiqildi' : 'Bobni o‘qib chiqdim'}</span></button><div class="chapter-end-nav">${
    prev
      ? card('end-prev', `#bob-${prev.id}`, 'Oldingi bob', esc(prev.title), rdIcon('chev-l'), false)
      : card('end-prev', '#bosh-sahifa', 'Bosh sahifa', 'Boblar ro‘yxati', rdIcon('chev-l'), false)
  }${
    next
      ? card('end-next', `#bob-${next.id}`, 'Keyingi bob', esc(next.title), rdIcon('chev-r'), true)
      : card('end-next', '#bosh-sahifa', 'Bosh sahifa', 'Barcha boblar', rdIcon('chev-r'), true)
  }</div>`;
}
async function renderChapter(id, anchor) {
  const c = CHAPTERS.find(x => x.id === id);
  if (!c) {
    location.hash = 'bosh-sahifa';
    return;
  }
  const serial = ++navigationSerial,
    same = activeChapter?.id === id && renderedChapter === id;
  const fromLanding = !$('#landing').hidden;
  $('#landing').hidden = true;
  $('#reader').hidden = false;
  $$('[data-chapter]').forEach(a => {
    a.classList.toggle('active', Number(a.dataset.chapter) === id);
    if (Number(a.dataset.chapter) === id) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  storeLocal('econ-last', { chapter: id, section: anchor || '' });
  lastLocation = { chapter: id, section: anchor || '' };
  if (same) {
    applyAnchor(anchor, true);
    return;
  }
  emit('chapter:leave', { chapter: activeChapter });
  exitPresentation();
  sectionObserver?.disconnect();
  activeChapter = c;
  renderedChapter = null;
  activeSections = [];
  allAnswers = false;
  $('#reading-progress').style.width = '0';
  setLabel($('#answer-toggle'), 'Yechimlarni ochish');
  $('#answer-toggle').setAttribute('aria-pressed', 'false');
  $('#answer-toggle').disabled = true;
  $('#presentation-toggle').disabled = true;
  $('#print-button').disabled = true;
  $('#chapter-content').innerHTML = '<p class="chapter-loading" role="status">Bob yuklanmoqda…</p>';
  $('#chapter-end').innerHTML = '';
  $('#chapter-header').innerHTML =
    `<p class="eyebrow"><b>${pad2(id)}-BOB</b> · IQTISODIYOT ASOSLARI</p><h1>${esc(c.title)}</h1><p class="english-title" lang="en">${esc(c.englishTitle)}</p><p class="lead">${esc(c.lead)}</p><div class="chapter-facts"><span><strong>${c.sourcePages[0]}–${c.sourcePages[1]}</strong>kitob sahifalari</span><span><strong>${c.sections.length}</strong>tushuntirish bo‘limi</span><span><strong>${c.totalAnswered}</strong>izohli javob</span></div>`;
  const toc = c.sections
    .map(
      (s, i) =>
        `<a href="#bob-${id}/${s.id}" data-section="${s.id}"><span class="toc-num">${pad2(i + 1)}</span><span>${esc(s.title)}</span></a>`
    )
    .join('');
  $('#toc-nav').innerHTML = toc;
  $('#inline-toc').innerHTML =
    `<details><summary><span>Bob mundarijasi <span class="toc-count">· ${c.sections.length} bo‘lim</span></span>${rdIcon('chev-d')}</summary><div class="toc-items">${toc}</div></details>`;
  $('#reader-position').textContent = `${pad2(id)} / ${pad2(CHAPTERS.length)}`;
  $('#bar-title').textContent = c.title;
  document.title = `${c.title} · Iqtisodiyot`;
  $('#announcer').textContent = `${id}-bob: ${c.title}`;
  emit('view:reader', { chapter: c, fromLanding });
  if (!anchor) {
    const heading = $('#chapter-header h1');
    heading.setAttribute('tabindex', '-1');
    heading.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
  try {
    const template = await getChapterTemplate(c);
    if (serial !== navigationSerial || activeChapter?.id !== id) return;
    $('#chapter-content').replaceChildren(template.cloneNode(true));
    activeSections = $$('#chapter-content>.lesson-section');
    renderedChapter = id;
    $('#answer-toggle').disabled = false;
    $('#presentation-toggle').disabled = false;
    $('#print-button').disabled = false;
    $('#chapter-end').innerHTML = chapterEndHTML(id);
    attachModels(c, anchor);
    watchSections();
    applyAnchor(anchor, false);
    emit('chapter:ready', {
      chapter: c,
      anchor,
      container: $('#chapter-content'),
      sections: activeSections,
    });
  } catch {
    if (serial !== navigationSerial) return;
    $('#chapter-content').innerHTML =
      '<div class="load-error" role="status"><h2>Bob yuklanmadi</h2><p>Internet aloqasi tiklangach, qayta urinib ko‘ring. Yuklangan boblar shu oynada saqlanadi.</p><button class="quiet-button" id="chapter-retry" type="button">Qayta yuklash</button></div>';
    $('#chapter-retry').addEventListener('click', () => renderChapter(id, anchor));
  }
}
function route() {
  const h = decodeURIComponent(location.hash.slice(1));
  const m = h.match(/^bob-(\d+)(?:\/(.+))?$/);
  if (m) {
    renderChapter(Number(m[1]), m[2]);
    return;
  }
  emit('chapter:leave', { chapter: activeChapter });
  navigationSerial++;
  exitPresentation();
  sectionObserver?.disconnect();
  activeChapter = null;
  renderedChapter = null;
  activeSections = [];
  $('#landing').hidden = false;
  $('#reader').hidden = true;
  $('#reading-progress').style.width = '0';
  renderDirectory();
  document.title = 'Iqtisodiyot · Tushunib o‘rganing';
  emit('view:landing', { hash: h });
  if (h === 'boblar') requestAnimationFrame(() => $('#boblar').scrollIntoView());
  else window.scrollTo({ top: 0, behavior: 'instant' });
}
let currentSectionId = null;
/* O‘ng panel bo‘limlari sig‘masa, faol havola ko‘rinib turishi uchun panelning o‘zi suriladi (sahifa emas). */
function revealInRail(link) {
  const rail = link?.closest('.toc-sidebar');
  if (!rail || rail.scrollHeight <= rail.clientHeight) return;
  const r = link.getBoundingClientRect(),
    b = rail.getBoundingClientRect();
  if (r.top < b.top + 8) rail.scrollTop -= b.top + 8 - r.top;
  else if (r.bottom > b.bottom - 8) rail.scrollTop += r.bottom - b.bottom + 8;
}
function watchSections() {
  sectionObserver?.disconnect();
  currentSectionId = null;
  if (!('IntersectionObserver' in window)) return;
  sectionObserver = new IntersectionObserver(
    entries => {
      const hit = entries
        .filter(e => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (hit) {
        const changed = hit.target.id !== currentSectionId;
        currentSectionId = hit.target.id;
        $$('[data-section]').forEach(a => a.classList.toggle('active', a.dataset.section === hit.target.id));
        revealInRail($('#toc-nav a.active'));
        if (changed) emit('section:active', { id: hit.target.id, el: hit.target });
        if (activeChapter) {
          lastLocation = { chapter: activeChapter.id, section: hit.target.id };
          storeLocal('econ-last', lastLocation);
        }
      }
    },
    { rootMargin: '-100px 0px -55% 0px', threshold: [0, 0.1, 0.4] }
  );
  activeSections.forEach(s => sectionObserver.observe(s));
}
function updateProgress() {
  if (!activeChapter) return;
  const article = $('#chapter-content');
  const top = article.getBoundingClientRect().top + window.scrollY;
  const travel = article.offsetHeight - window.innerHeight + 100;
  const pct = presentation
    ? (slideIndex + 1) / activeSections.length
    : Math.max(0, Math.min(1, (window.scrollY - top + 120) / Math.max(1, travel)));
  $('#reading-progress').style.width = `${pct * 100}%`;
}
function showSlide(n) {
  const previous = slideIndex;
  slideIndex = Math.max(0, Math.min(activeSections.length - 1, n));
  activeSections.forEach((s, i) => (s.hidden = i !== slideIndex));
  $('#slide-position').textContent = `${slideIndex + 1} / ${activeSections.length}`;
  $('#slide-progress').style.setProperty('--p', (slideIndex + 1) / Math.max(1, activeSections.length));
  $('#slide-prev').disabled = slideIndex === 0;
  $('#slide-next').disabled = slideIndex === activeSections.length - 1;
  window.scrollTo({ top: 0, behavior: 'instant' });
  updateProgress();
  emit('presentation:slide', {
    el: activeSections[slideIndex],
    index: slideIndex,
    direction: slideIndex >= previous ? 1 : -1,
    total: activeSections.length,
  });
}
function exitPresentation() {
  const was = presentation;
  if (was) emit('presentation:exit');
  presentation = false;
  document.body.classList.remove('is-presentation');
  $('#presentation-bar').hidden = true;
  $('#presentation-toggle').setAttribute('aria-pressed', 'false');
  setLabel($('#presentation-toggle'), 'Taqdimot');
  activeSections.forEach(s => (s.hidden = false));
  if (was) {
    /* Chiqqanda o‘sha bo‘limda qolamiz. */
    activeSections[slideIndex]?.scrollIntoView({ behavior: 'instant', block: 'start' });
    $('#presentation-toggle').focus({ preventScroll: true });
  }
}
