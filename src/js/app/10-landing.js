/* Qismlar va "darsda o‘tilgan" boblar content/course.json dan keladi (build.py → COURSE). */
const parts = COURSE.parts;
const taught = COURSE.taughtInClass || [];
const CARD_ARROW =
  '<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4.4 2.4 3.6 3.6-3.6 3.6"/></svg>';
let directoryMarkup = '';
function navLink(c) {
  return `<a href="#bob-${c.id}" data-chapter="${c.id}"><span>${String(c.id).padStart(2, '0')}</span><span>${esc(c.title)}</span></a>`;
}
function chapterCard(c) {
  const id = c.id,
    num = String(id).padStart(2, '0');
  const tags =
    (taught.includes(id) ? '<span class="tag">DARSDA O‘TILGAN</span>' : '') +
    (finished.includes(id) ? '<span class="tag tag-done">✓ O‘QILGAN</span>' : '');
  return `<div class="card-item"><a class="chapter-card" href="#bob-${id}" aria-labelledby="ch${id}-t" aria-describedby="ch${id}-m"><span class="card-top"><span class="card-num" aria-hidden="true">${num}</span><span class="card-arrow" aria-hidden="true">${CARD_ARROW}</span></span><span class="card-body"><h4 class="card-title" id="ch${id}-t">${esc(c.title)}</h4><p class="card-lead">${esc(c.lead)}</p></span><span class="card-foot" id="ch${id}-m"><span class="card-meta"><span>${c.sections.length} bo‘lim</span><span>${c.sourcePages[0]}–${c.sourcePages[1]}-sahifalar</span></span>${tags ? `<span class="card-tags">${tags}</span>` : ''}</span></a></div>`;
}
function renderDirectory() {
  const markup = parts
    .map(
      p =>
        `<div class="part-group"><header class="part-head"><p class="part-label">${esc(p.label)}</p><h3 class="part-title">${esc(p.title)}</h3></header><div class="part-cards">${p.chapters
          .map(id => {
            const c = CHAPTERS.find(c => c.id === id);
            return c ? chapterCard(c) : '';
          })
          .join('')}</div></div>`
    )
    .join('');
  /* Bir xil bo‘lsa, DOM'ni almashtirmaymiz: harakat (GSAP) holati va fokus saqlanib qoladi. */
  if (markup !== directoryMarkup) {
    $('#chapter-list').innerHTML = markup;
    directoryMarkup = markup;
  }
  const links = CHAPTERS.map(navLink).join('');
  $('#chapter-nav').innerHTML = links;
  $('#mobile-chapter-links').innerHTML = links;
  const diagrams = CHAPTERS.reduce(
    (s, c) => s + (c.diagramCount || 0) + (c.interactiveTypes?.length || 0),
    0
  );
  const answers = CHAPTERS.reduce(
    (s, c) =>
      s +
      (c.totalAnswered ??
        (c.reviewAnswered || 0) + (c.applicationsAnswered || 0) + (c.quickQuizAnswered || 0)),
    0
  );
  for (const [sel, value] of [
    ['#total-diagrams', diagrams],
    ['#total-answers', answers],
  ]) {
    const el = $(sel);
    el.textContent = value;
    el.dataset.value = value; /* harakat qatlami sanash uchun yakuniy qiymatni shundan oladi */
  }
  const last = lastLocation && CHAPTERS.find(c => c.id === lastLocation.chapter);
  const resume = $('#resume-link');
  resume.hidden = !last;
  if (last) {
    resume.href = `#bob-${last.id}${lastLocation.section ? '/' + lastLocation.section : ''}`;
    resume.innerHTML = `<span class="resume-label">O‘qishni davom ettirish</span><strong class="resume-title">${esc(last.title)}</strong>`;
  }
}
