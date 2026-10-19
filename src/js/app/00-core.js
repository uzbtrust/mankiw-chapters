const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
const esc = s =>
  String(s ?? '').replace(
    /[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );
const norm = s =>
  String(s)
    .toLocaleLowerCase('uz')
    .normalize('NFD')
    .replace(/[‘’ʻʼ'`]/g, '')
    .replace(/\p{Diacritic}/gu, '');
const storeLocal = (k, v) => {
  try {
    localStorage.setItem(k, JSON.stringify(v));
  } catch {}
};
const readLocal = (k, fallback) => {
  try {
    return JSON.parse(localStorage.getItem(k)) ?? fallback;
  } catch {
    return fallback;
  }
};
/* Harakat qatlami bilan aloqa: Motion yo‘q bo‘lsa ham sayt to‘liq ishlaydi. */
const emit = (name, payload) => (window.Motion ? window.Motion.emit(name, payload) : false);
/* Dialoglar: ochilish/yopilish animatsiyasi uchun yagona kirish nuqtasi. */
function openDialog(d) {
  if (d.open) return;
  d.showModal();
  emit('dialog:open', { dialog: d });
}
function closeDialog(d) {
  if (!d.open) return;
  if (!emit('dialog:close', { dialog: d, done: () => d.close() })) d.close();
}
document.addEventListener(
  'cancel',
  e => {
    if (e.target instanceof HTMLDialogElement) {
      e.preventDefault();
      closeDialog(e.target);
    }
  },
  true
);
let activeChapter = null,
  activeSections = [],
  slideIndex = 0,
  presentation = false,
  sectionObserver = null,
  allAnswers = false;
let finished = readLocal('econ-finished', []),
  fontSize = readLocal('econ-size', 18),
  lastLocation = readLocal('econ-last', null);
