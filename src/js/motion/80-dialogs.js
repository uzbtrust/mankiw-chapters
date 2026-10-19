/* MOTION · dialoglar harakati. Faqat Motion.on(...) orqali ulaning — qarang docs/DESIGN.md
   Qidiruv: masshtab .96 → 1 + xira bo‘lish; boblar menyusi: telefonda pastdan chiqadigan varaq,
   kattaroq ekranda markaziy panel. Fon (::backdrop) animatsiyasi CSS da (.is-closing sinfi bilan). */
(function () {
  'use strict';
  var G = window.gsap;

  function isSheet(d) {
    return d.id === 'mobile-nav' && window.matchMedia('(max-width: 767px)').matches;
  }

  Motion.on('dialog:open', function (p) {
    var d = p && p.dialog;
    if (!d) return;
    if (d.id === 'search-dialog') {
      var input = d.querySelector('#search-input');
      if (input) {
        input.focus();
        input.select();
      }
    }
    if (!Motion.ok()) return;
    G.killTweensOf(d);
    d.classList.remove('is-closing');
    delete d.dataset.closing;
    if (isSheet(d)) {
      G.fromTo(
        d,
        { yPercent: 100 },
        { yPercent: 0, duration: 0.55, ease: Motion.ease.out, clearProps: 'transform' }
      );
    } else {
      G.fromTo(
        d,
        {
          opacity: 0,
          scale: 0.96,
          y: d.id === 'search-dialog' ? -10 : 10,
          transformOrigin: d.id === 'search-dialog' ? '50% 0%' : '50% 50%',
        },
        {
          opacity: 1,
          scale: 1,
          y: 0,
          duration: 0.35,
          ease: Motion.ease.apple,
          clearProps: 'transform,opacity,transformOrigin',
        }
      );
    }
  });

  Motion.on('dialog:close', function (p) {
    var d = p && p.dialog;
    if (!d || !Motion.ok()) return false;
    if (d.dataset.closing) return true;
    d.dataset.closing = '1';
    d.classList.add('is-closing');
    G.killTweensOf(d);
    var finished = false;
    var finish = function () {
      if (finished) return;
      finished = true;
      delete d.dataset.closing;
      d.classList.remove('is-closing');
      p.done();
      G.set(d, { clearProps: 'transform,opacity,transformOrigin' });
    };
    if (isSheet(d)) G.to(d, { yPercent: 100, duration: 0.35, ease: 'power3.in', onComplete: finish });
    else G.to(d, { opacity: 0, scale: 0.97, duration: 0.2, ease: 'power2.in', onComplete: finish });
    /* Tab yashirin bo‘lsa rAF to‘xtaydi — dialog ochiq qolib ketmasin */
    setTimeout(finish, 700);
    return true;
  });

  /* Harakat kamaytirilsa yoki tema o‘zgarsa — ochiq dialogni o‘z holiga qaytaramiz */
  Motion.on('settle', function () {
    Array.prototype.forEach.call(document.querySelectorAll('dialog[open]'), function (d) {
      if (G) G.killTweensOf(d);
      d.classList.remove('is-closing');
      if (G) G.set(d, { clearProps: 'transform,opacity,transformOrigin' });
    });
  });
})();
