let searchPromise = null,
  searchSerial = 0,
  searchTimer = null;
async function getSearchIndex() {
  if (!searchPromise)
    searchPromise = (async () => {
      let rows;
      if (COURSE_ONLINE) {
        const r = await fetch(SEARCH_INDEX_URL);
        if (!r.ok) throw new Error('Search unavailable');
        rows = await r.json();
      } else
        rows = CHAPTERS.flatMap(c =>
          Array.from(
            document.getElementById(`template-${c.id}`).content.querySelectorAll('.lesson-section')
          ).flatMap(s => [
            {
              c: c.id,
              i: s.id,
              t: s.querySelector('h2')?.textContent || '',
              x: s.textContent.replace(/\s+/g, ' ').trim(),
            },
            ...Array.from(s.querySelectorAll('details.answer[id]')).map(q => ({
              c: c.id,
              i: q.id,
              t: q.querySelector('summary')?.textContent || '',
              x: q.textContent.replace(/\s+/g, ' ').trim(),
              q: true,
            })),
          ])
        );
      return rows.map(r => {
        const chapter = CHAPTERS.find(c => c.id === r.c);
        return {
          chapter,
          id: r.i,
          title: r.t,
          text: r.x,
          question: !!r.q,
          nt: norm(r.t),
          nx: norm(r.x),
          nc: norm(chapter.title),
        };
      });
    })().catch(e => {
      searchPromise = null;
      throw e;
    });
  return searchPromise;
}
const escRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
/* Normallashtirilgan (diakritiksiz) matndagi o‘rinni asl matndagi o‘ringa o‘tkazadi. */
function origIndex(text, nPos) {
  let n = 0,
    i = 0;
  for (; i < text.length && n < nPos; i++) n += norm(text[i]).length;
  return i;
}
function highlight(text, raw) {
  const t = esc(text);
  if (raw.length < 2) return t;
  try {
    return text
      .split(new RegExp(`(${escRe(raw)})`, 'giu'))
      .map((part, i) => (i % 2 ? `<mark>${esc(part)}</mark>` : esc(part)))
      .join('');
  } catch {
    return t;
  }
}
function setActiveResult(i, scroll) {
  const items = $$('#search-results .search-result');
  if (!items.length) return;
  const n = (i + items.length) % items.length;
  items.forEach((a, k) => {
    a.classList.toggle('is-active', k === n);
    a.setAttribute('aria-selected', String(k === n));
  });
  $('#search-input').setAttribute('aria-activedescendant', items[n].id);
  if (scroll) items[n].scrollIntoView({ block: 'nearest' });
}
function activeResultIndex() {
  return $$('#search-results .search-result').findIndex(a => a.classList.contains('is-active'));
}
function renderNoResults() {
  $('#search-results').innerHTML = '';
  $('#search-input').removeAttribute('aria-activedescendant');
  $('#search-input').setAttribute('aria-expanded', 'false');
}
async function search() {
  const serial = ++searchSerial,
    raw = $('#search-input').value.trim(),
    q = norm(raw);
  if (q.length < 2) {
    $('#search-status').textContent =
      'Kamida ikki harf yozing. Atama, savol yoki misolni qidirishingiz mumkin.';
    renderNoResults();
    return;
  }
  $('#search-status').textContent = 'Qidirilmoqda…';
  try {
    const index = await getSearchIndex();
    if (serial !== searchSerial || norm($('#search-input').value.trim()) !== q) return;
    const hits = index
      .map(s => ({
        ...s,
        score: s.nt.includes(q) ? (s.question ? 4 : 3) : s.nc.includes(q) ? 2 : s.nx.includes(q) ? 1 : 0,
      }))
      .filter(s => s.score)
      .sort((a, b) => b.score - a.score)
      .slice(0, 18);
    $('#search-status').textContent = hits.length
      ? `${hits.length} mos bo‘lim topildi. Natijani bosib, bobga o‘ting.`
      : 'Mos bo‘lim topilmadi. Boshqa atama yoki qisqaroq so‘z bilan sinab ko‘ring.';
    $('#search-results').innerHTML = hits
      .map((s, i) => {
        const pos = s.nx.indexOf(q),
          start = pos > 70 ? origIndex(s.text, pos - 70) : 0,
          snip = s.text.slice(start, start + 220).trim();
        return `<a class="search-result" id="search-hit-${i}" role="option" aria-selected="false" href="#bob-${s.chapter.id}/${s.id}"><small>${String(s.chapter.id).padStart(2, '0')}-BOB · ${s.question ? 'SAVOL · ' : ''}${esc(s.chapter.title)}</small><strong>${highlight(s.title, raw)}</strong><p>${start ? '…' : ''}${highlight(snip, raw)}…</p></a>`;
      })
      .join('');
    $('#search-input').setAttribute('aria-expanded', String(hits.length > 0));
    if (hits.length) setActiveResult(0, false);
    else $('#search-input').removeAttribute('aria-activedescendant');
    $('#search-results').scrollTop = 0;
  } catch {
    if (serial === searchSerial) {
      $('#search-status').textContent =
        'Qidiruv ma’lumoti yuklanmadi. Internet aloqasi tiklangach, so‘zni qayta yozib ko‘ring.';
      renderNoResults();
    }
  }
}
const searchDialog = $('#search-dialog');
function openSearch() {
  openDialog(searchDialog);
  $('#search-input').focus();
  $('#search-input').select();
}
$('#search-open').addEventListener('click', openSearch);
$('#search-close').addEventListener('click', () => closeDialog(searchDialog));
$('#search-input').addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(search, 160);
});
/* Klaviatura: ↑/↓ natijani tanlaydi, Enter ochadi (Esc dialogning o‘zi yopadi). */
$('#search-input').addEventListener('keydown', e => {
  if (e.isComposing) return;
  /* type=search da Esc brauzerda avval matnni tozalaydi — bizga esa dialogni yopish kerak. */
  if (e.key === 'Escape') {
    e.preventDefault();
    closeDialog(searchDialog);
    return;
  }
  const items = $$('#search-results .search-result');
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    if (!items.length) return;
    e.preventDefault();
    setActiveResult(activeResultIndex() + (e.key === 'ArrowDown' ? 1 : -1), true);
  } else if (e.key === 'Enter') {
    clearTimeout(searchTimer);
    const current = items[Math.max(0, activeResultIndex())];
    if (current) {
      e.preventDefault();
      current.click();
    } else if (norm($('#search-input').value.trim()).length >= 2) {
      e.preventDefault();
      search();
    }
  }
});
$('#search-results').addEventListener('click', e => {
  if (e.target.closest('a')) closeDialog(searchDialog);
});
$('#search-results').addEventListener('mousemove', e => {
  const a = e.target.closest('.search-result');
  if (a && !a.classList.contains('is-active'))
    setActiveResult($$('#search-results .search-result').indexOf(a), false);
});
searchDialog.addEventListener('click', e => {
  if (e.target === searchDialog) {
    const r = searchDialog.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)
      closeDialog(searchDialog);
  }
});
