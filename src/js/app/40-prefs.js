function setSize(n) {
  fontSize = Math.max(16, Math.min(24, n));
  document.documentElement.style.setProperty('--reader-size', fontSize + 'px');
  storeLocal('econ-size', fontSize);
  $('#font-down').disabled = fontSize === 16;
  $('#font-up').disabled = fontSize === 24;
}
/* Tema: ikonlar CSS orqali almashadi (html.dark). `animate` — faqat foydalanuvchi bosganda:
   brauzer qo‘llasa, butun sahifa View Transition bilan yumshoq o‘tadi. */
function setTheme(dark, animate) {
  const apply = () => {
    document.documentElement.classList.toggle('dark', dark);
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#000000' : '#ffffff');
    emit('theme:change', { dark });
  };
  const calm = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (animate && !calm && document.startViewTransition) {
    /* O‘tish bekor qilinsa (tez-tez bosilsa, sahifa yashirin bo‘lsa) va'dalar xato bermasin */
    const vt = document.startViewTransition(apply);
    ['ready', 'finished', 'updateCallbackDone'].forEach(k => vt[k] && vt[k].catch(() => {}));
  } else apply();
  $('#theme-toggle').setAttribute('aria-label', dark ? 'Kunduzgi rejimni yoqish' : 'Tungi rejimni yoqish');
  /* faqat foydalanuvchi tanlovi saqlanadi; aks holda tizim (tungi/kunduzgi) sozlamasi kuzatilaveradi */
  if (animate) storeLocal('econ-dark', dark);
}
let themeDark = document.documentElement.classList.contains('dark');
$('#font-down').addEventListener('click', () => setSize(fontSize - 1));
$('#font-up').addEventListener('click', () => setSize(fontSize + 1));
$('#theme-toggle').addEventListener('click', () => {
  themeDark = !themeDark;
  setTheme(themeDark, true);
});
/* Qidiruv tugmasidagi yorliq: Mac'da ⌘K, boshqa tizimlarda Ctrl K */
if (!/Mac|iPhone|iPad|iPod/.test(navigator.platform || navigator.userAgent)) {
  const kbd = $('.search-kbd');
  if (kbd) kbd.textContent = 'Ctrl K';
}
