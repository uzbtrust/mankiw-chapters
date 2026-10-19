/* MOTION · interaktiv modellar harakati. Faqat Motion.on(...) orqali ulaning — qarang docs/DESIGN.md

   Slayder → ko‘rsatilayotgan holatni ~0,35 s da silliq yaqinlashtirish simulations.js ichida
   (u yerda chizma va raqamlar har kadrda qayta chiziladi, oxirida aniq qiymatga "yopishadi").
   Bu fayl: kartaning birinchi ko‘rinishdagi paydo bo‘lishi (karta + egri chiziqlar chizilishi +
   ko‘rsatkichlar) va bobdan chiqishda/`settle`da hamma narsani oxirgi holatga keltirish. */
(function () {
  'use strict';
  var M = window.Motion;
  if (!M) return;

  /* Ketayotgan tweenlarni tugatib, hamma modelni aniq (oxirgi) holatga keltiradi. */
  function settleModels() {
    var hosts = document.querySelectorAll('[data-interactive]');
    for (var i = 0; i < hosts.length; i++) if (hosts[i].__sim) hosts[i].__sim.settle();
  }

  function reveal(card) {
    var G = window.gsap;
    var curves = card.querySelectorAll('.sim-chart .cv'); /* faqat uzluksiz egri chiziqlar */
    var metrics = card.querySelectorAll('.sim-metric');
    var tl = G.timeline({ paused: true });
    tl.fromTo(
      card,
      { opacity: 0, y: 32 },
      { opacity: 1, y: 0, duration: M.dur.s + 0.1, ease: M.ease.out, clearProps: 'opacity,transform' },
      0
    );
    if (curves.length && window.DrawSVGPlugin)
      tl.fromTo(
        curves,
        { drawSVG: '0%' },
        {
          drawSVG: '100%',
          duration: 0.8,
          ease: M.ease.inOut,
          stagger: 0.08,
          clearProps: 'strokeDasharray,strokeDashoffset',
          /* DrawSVG qoldirgan inline dash qiymatlarini ham tozalaymiz. */
          onComplete: function () {
            for (var i = 0; i < curves.length; i++) {
              curves[i].style.removeProperty('stroke-dasharray');
              curves[i].style.removeProperty('stroke-dashoffset');
            }
          },
        },
        0.15
      );
    if (metrics.length)
      tl.fromTo(
        metrics,
        { opacity: 0, y: 12 },
        { opacity: 1, y: 0, duration: 0.45, stagger: 0.06, clearProps: 'opacity,transform' },
        0.3
      );
    /* clearProps bilan fromTo'ning "from" holati o‘z-o‘zidan qo‘llanmaydi — aniq chizamiz. */
    tl.progress(0);
    var finish = function () {
      tl.progress(1);
    };
    window.ScrollTrigger.create({
      trigger: card,
      start: 'top 88%',
      once: true,
      onEnter: function () {
        tl.play();
      },
      onLeave: finish,
      onEnterBack: finish,
    });
  }

  M.on('models:mounted', function (e) {
    var container = e && e.container;
    if (!container) return;
    /* Scope'da ishlatiladigan ScrollTrigger bo‘lmasa — hech narsa yashirilmaydi. */
    if (!window.ScrollTrigger) return;
    M.scope(
      'models',
      function () {
        container.querySelectorAll('.interactive[data-mounted="true"]').forEach(reveal);
      },
      container
    );
    M.refresh();
  });

  M.on('chapter:leave', function () {
    settleModels();
    M.revert('models');
  });

  M.on('settle', function () {
    settleModels();
    M.revert('models');
  });
})();
