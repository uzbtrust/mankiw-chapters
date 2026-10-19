/* ==========================================================================
   MOTION · yadro — GSAP sozlamasi, hodisa shinasi va xavfsizlik qoidalari.

   Boshqa hamma harakat fayllari (src/js/motion/NN-*.js) faqat shu obyekt orqali
   ilovaga ulanadi:   Motion.on('chapter:ready', ({ container }) => { … })

   Hodisalar (app/*.js shularni chaqiradi — mazmuni docs/DESIGN.md da):
     view:landing        { hash }
     view:reader         { chapter, fromLanding }       bob sarlavhasi chizildi, mazmun hali yo‘q
     chapter:ready       { chapter, anchor, container, sections }   mazmun DOM’ga qo‘yildi
     chapter:leave       { chapter }                    bob almashmoqda / bosh sahifaga qaytilmoqda
     models:mounted      { container }                  interaktiv modellar o‘rnatildi
     section:active      { id, el }                     o‘qilayotgan bo‘lim o‘zgardi
     anchor:jump         { target }                     hash orqali aniq joyga sakrandi
     presentation:enter | presentation:exit
     presentation:slide  { el, index, direction, total }
     answers:all         { open }
     dialog:open         { dialog }
     dialog:close        { dialog, done }   animatsiyani tugatgach done() ni chaqiring va true qaytaring
     theme:change        { dark }
     settle              barcha kutayotgan animatsiyani tugatib, kontentni oxirgi ko‘rinishga keltiring
                         (chop etish, taqdimot rejimi, "harakatni kamaytirish" yoqilganda)
   ========================================================================== */
(function () {
  'use strict';
  var G = window.gsap;
  var handlers = Object.create(null);
  var scopes = Object.create(null);
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  var M = (window.Motion = {
    /** GSAP yuklanganmi? */
    enabled: !!G,
    /** Foydalanuvchi "harakatni kamaytirish"ni yoqganmi? */
    reduced: function () {
      return !!mq.matches;
    },
    /** Animatsiya qilish xavfsizmi (GSAP bor va harakat kamaytirilmagan)? Har safar tekshiring. */
    ok: function () {
      return !!G && !mq.matches;
    },
    /** Yagona vaqt va egri chiziqlar. Qattiq yozilgan qiymat o‘rniga shularni ishlating. */
    dur: { xs: 0.25, s: 0.5, m: 0.8, l: 1.2 },
    ease: { out: 'expo.out', soft: 'power3.out', inOut: 'power3.inOut', apple: 'apple' },

    on: function (name, fn) {
      (handlers[name] = handlers[name] || []).push(fn);
      return fn;
    },
    off: function (name, fn) {
      handlers[name] = (handlers[name] || []).filter(function (f) {
        return f !== fn;
      });
    },
    /** true qaytadi, agar kamida bitta tinglovchi true qaytargan bo‘lsa. */
    emit: function (name, payload) {
      var list = handlers[name];
      if (!list) return false;
      var handled = false;
      list.slice().forEach(function (fn) {
        try {
          if (fn(payload) === true) handled = true;
        } catch (err) {
          console.error('[Motion] ' + name, err);
        }
      });
      return handled;
    },

    /**
     * Nomlangan gsap.context. Bir nom bilan qayta chaqirilsa, avvalgisi revert() qilinadi
     * (ya’ni elementlar o‘zining tabiiy, ko‘rinadigan holatiga qaytadi).
     * Bob almashganda M.revert('chapter') chaqiring.
     */
    scope: function (name, fn, root) {
      M.revert(name);
      if (!M.ok()) return null;
      scopes[name] = G.context(fn, root || document.body);
      return scopes[name];
    },
    revert: function (name) {
      if (scopes[name]) {
        scopes[name].revert();
        delete scopes[name];
      }
    },
    /** ScrollTrigger’ni layout o‘zgargandan keyin xavfsiz yangilash. */
    refresh: function () {
      if (window.ScrollTrigger)
        requestAnimationFrame(function () {
          ScrollTrigger.refresh();
        });
    },
  });

  if (G) {
    var plugins = ['ScrollTrigger', 'ScrollToPlugin', 'SplitText', 'DrawSVGPlugin', 'CustomEase']
      .map(function (n) {
        return window[n];
      })
      .filter(Boolean);
    G.registerPlugin.apply(G, plugins);
    if (window.CustomEase) window.CustomEase.create('apple', '0.28,0.11,0.32,1');
    G.defaults({ ease: 'power3.out', duration: 0.8 });
    G.config({ nullTargetWarn: false });
    if (window.ScrollTrigger) ScrollTrigger.config({ ignoreMobileResize: true });
  }

  // Foydalanuvchi sessiya o‘rtasida "harakatni kamaytirish"ni yoqsa — hammasini tugatamiz.
  var onChange = function () {
    if (mq.matches) M.emit('settle');
  };
  if (mq.addEventListener) mq.addEventListener('change', onChange);
  else if (mq.addListener) mq.addListener(onChange);
})();
