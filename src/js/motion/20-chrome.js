/* MOTION · chrome (topbar) harakati. Faqat Motion.on(...) orqali ulaning — qarang docs/DESIGN.md

   Yuqori panelning shisha foni va chizig‘i sahifa boshida (scrollY < 8px) ko‘rinmaydi va
   foydalanuvchi pastga aylantirganda silliq paydo bo‘ladi. GSAP yo‘q / harakat kamaytirilgan
   bo‘lsa, CSS holati (doim ko‘rinadigan shisha panel) o‘zgarishsiz qoladi. */
(function () {
  'use strict';
  var THRESHOLD = 8;
  var bg = null;
  var shown = null; // null = noma’lum (keyingi scrollda qayta hisoblanadi)
  var ticking = false;

  function scrollTop() {
    return window.pageYOffset || document.documentElement.scrollTop || 0;
  }

  function apply(show) {
    if (show === shown || !bg || !window.Motion.ok()) return;
    var first = shown === null;
    shown = show;
    window.gsap.to(bg, {
      opacity: show ? 1 : 0,
      duration: first ? 0 : 0.35,
      ease: 'power2.out',
      overwrite: true,
    });
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      apply(scrollTop() >= THRESHOLD);
    });
  }

  function init() {
    bg = document.querySelector('.topbar-bg');
    if (!bg || !window.Motion || !window.Motion.ok()) return;
    apply(scrollTop() >= THRESHOLD);
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Chop etish / taqdimot / "harakatni kamaytirish": panel to‘liq ko‘rinadigan holatga qaytadi.
  if (window.Motion) {
    window.Motion.on('settle', function () {
      if (!bg || !window.gsap) return;
      window.gsap.killTweensOf(bg);
      window.gsap.set(bg, { clearProps: 'opacity' });
      shown = null;
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
