document.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    openDialog(searchDialog);
    $('#search-input').focus();
  }
  if (!presentation || ['INPUT', 'SELECT', 'TEXTAREA', 'SUMMARY'].includes(e.target.tagName)) return;
  if (e.key === 'ArrowRight') {
    e.preventDefault();
    showSlide(slideIndex + 1);
  }
  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    showSlide(slideIndex - 1);
  }
  if (e.key === 'Escape') exitPresentation();
});
window.addEventListener('hashchange', route);
window.addEventListener('scroll', updateProgress, { passive: true });
window.addEventListener('resize', updateProgress);
setTheme(document.documentElement.classList.contains('dark'));
setSize(fontSize);
renderDirectory();
window.addEventListener('DOMContentLoaded', route);
