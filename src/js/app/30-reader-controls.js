$('#presentation-toggle').addEventListener('click', () => {
  if (presentation) {
    exitPresentation();
    return;
  }
  presentation = true;
  document.body.classList.add('is-presentation');
  $('#presentation-toggle').setAttribute('aria-pressed', 'true');
  setLabel($('#presentation-toggle'), 'O‘qish rejimi');
  $('#presentation-bar').hidden = false;
  emit('settle');
  emit('presentation:enter');
  showSlide(0);
  $('#slide-next').focus({ preventScroll: true });
});
$('#slide-prev').addEventListener('click', () => showSlide(slideIndex - 1));
$('#slide-next').addEventListener('click', () => showSlide(slideIndex + 1));
$('#slide-exit').addEventListener('click', exitPresentation);
$('#answer-toggle').addEventListener('click', () => {
  allAnswers = !allAnswers;
  $$('#chapter-content details.answer').forEach(d => (d.open = allAnswers));
  setLabel($('#answer-toggle'), allAnswers ? 'Yechimlarni yopish' : 'Yechimlarni ochish');
  $('#answer-toggle').setAttribute('aria-pressed', String(allAnswers));
  emit('answers:all', { open: allAnswers });
});
$('#chapter-end').addEventListener('click', e => {
  const b = e.target.closest('[data-complete]');
  if (!b) return;
  const id = Number(b.dataset.complete);
  const done = !finished.includes(id);
  finished = done ? [...finished, id] : finished.filter(n => n !== id);
  b.querySelector('.cb-label').textContent = done ? 'Bob o‘qib chiqildi' : 'Bobni o‘qib chiqdim';
  b.classList.toggle('is-complete', done);
  b.setAttribute('aria-pressed', String(done));
  storeLocal('econ-finished', finished);
});
$('#back-to-top').addEventListener('click', e => {
  e.preventDefault();
  if (presentation) showSlide(0);
  else window.scrollTo({ top: 0, behavior: 'smooth' });
});
let printOpenStates = [];
window.addEventListener('beforeprint', () => {
  emit('settle');
  printOpenStates = $$('#chapter-content details.answer').map(d => d.open);
  $$('#chapter-content details.answer').forEach(d => (d.open = true));
});
window.addEventListener('afterprint', () => {
  $$('#chapter-content details.answer').forEach((d, i) => (d.open = printOpenStates[i] ?? false));
});
$('#print-button').addEventListener('click', () => window.print());
