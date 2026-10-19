/* MOTION · bosh sahifa harakati. Faqat Motion.on(...) orqali ulaning — qarang docs/DESIGN.md

   view:landing        → hero kirishi (birinchi marta to‘liq, qaytganda qisqa) + aylantirishdagi paydo bo‘lishlar
   view:reader | settle → hammasi revert() qilinadi (kontent o‘zining tabiiy, ko‘rinadigan holatiga qaytadi)

   Qoidalar: boshlang‘ich yashirin holatni faqat GSAP qo‘yadi (CSS emas); har bir paydo bo‘lish
   onEnter / onEnterBack / onLeave'da ham yakunlanadi (sakrab o‘tilganda ham hech narsa yashirin qolmasin);
   tugagach clearProps bilan inline stil qoldirilmaydi. */
(function () {
  'use strict';
  var M = window.Motion;
  if (!M) return;

  var built = false; // 'landing' scope tirik
  var played = false; // hero kirishi shu sahifa umrida bir marta bo‘ldi
  var counted = false; // raqamlar bir marta sanaldi
  var sample = null; // #chapter-list DOM almashganini bilish uchun birinchi karta
  var watcher = null;
  var CLEAR = 'opacity,transform,transformOrigin';

  function all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function teardown() {
    if (watcher) {
      watcher.disconnect();
      watcher = null;
    }
    built = false;
    sample = null;
    M.revert('landing');
  }

  /* ---------------------------------------------------------------- hero */
  function heroFull(G, root, q) {
    var tl = G.timeline({ defaults: { ease: M.ease.out } });
    var h1 = q('.hero-title')[0];
    var split = null;

    tl.from(q('.hero-eyebrow'), { opacity: 0, y: 14, duration: 0.7, clearProps: CLEAR }, 0);

    if (window.SplitText && h1) {
      split = window.SplitText.create(h1, {
        type: 'lines,words',
        mask: 'lines',
        linesClass: 'split-line',
      });
      tl.from(split.words, { yPercent: 120, duration: 1, stagger: 0.07 }, 0.04);
      tl.call(
        function () {
          split.revert();
        },
        null,
        1.22
      );
    } else if (h1) {
      tl.from(h1, { opacity: 0, y: 30, duration: 0.9, clearProps: CLEAR }, 0.04);
    }

    tl.from(q('.hero-lead'), { opacity: 0, y: 26, duration: 0.9, clearProps: CLEAR }, 0.26)
      .from(
        q('.hero-actions, .hero-resume'),
        { opacity: 0, y: 22, duration: 0.8, stagger: 0.08, clearProps: CLEAR },
        0.4
      )
      .from(
        q('.hero-card'),
        { opacity: 0, y: 56, scale: 0.965, transformOrigin: '50% 0%', duration: 1, clearProps: CLEAR },
        0.4
      );
    return tl;
  }

  function heroShort(G, q) {
    return G.from(q('.hero-eyebrow, .hero-title, .hero-lead, .hero-actions, .hero-resume, .hero-card'), {
      opacity: 0,
      y: 18,
      duration: 0.6,
      stagger: 0.05,
      ease: M.ease.soft,
      clearProps: CLEAR,
    });
  }

  /* Talab–taklif chizmasi: o‘qlar → egri chiziqlar → yo‘naltiruvchi chiziqlar → muvozanat nuqtasi → yozuvlar */
  function chartIntro(G, ctx, q, startedAt) {
    var ST = window.ScrollTrigger;
    var card = q('.hero-card')[0];
    var dot = q('.hc-dot')[0];
    if (!card || !dot || !ST) return;
    var cx = dot.getAttribute('cx');
    var cy = dot.getAttribute('cy');
    var origin = cx + ' ' + cy;
    var draw = !!window.DrawSVGPlugin;
    var axis = q('.hc-axis');
    var dem = q('.hc-demand');
    var sup = q('.hc-supply');
    var guideH = q('.hc-guide-h');
    var guideV = q('.hc-guide-v');
    var ring = q('.hc-ring');
    var labels = q('.hc-text');
    var everything = q('.hc-axis, .hc-curve, .hc-guide, .hc-ring, .hc-dot, .hc-text');

    var tl = G.timeline({
      paused: true,
      defaults: { ease: M.ease.soft },
      onComplete: function () {
        G.set(everything, { clearProps: 'all' });
        everything.forEach(function (el) {
          el.removeAttribute('style');
          el.removeAttribute('transform');
        });
      },
    });
    if (draw) {
      tl.fromTo(axis, { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.5, ease: M.ease.inOut }, 0)
        .fromTo(dem, { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.75, ease: 'power2.out' }, 0.08)
        .fromTo(sup, { drawSVG: '0%' }, { drawSVG: '100%', duration: 0.75, ease: 'power2.out' }, 0.2);
    } else {
      tl.from([axis, dem, sup], { opacity: 0, duration: 0.5, stagger: 0.1 }, 0);
    }
    tl.from(guideH, { scaleX: 0, svgOrigin: origin, duration: 0.5, ease: M.ease.out }, 0.62)
      .from(guideV, { scaleY: 0, svgOrigin: origin, duration: 0.5, ease: M.ease.out }, 0.62)
      .from(q('.hc-dot'), { scale: 0, svgOrigin: origin, duration: 0.55, ease: 'back.out(2.8)' }, 0.66)
      .from(ring, { scale: 0, opacity: 0, svgOrigin: origin, duration: 0.7, ease: M.ease.out }, 0.72)
      .from(labels, { opacity: 0, y: 6, duration: 0.5, stagger: 0.05 }, 0.72);

    // yumshoq "puls" halqasi (vaqtinchalik element)
    var pulse = ring[0] ? ring[0].cloneNode() : null;
    if (pulse) {
      pulse.setAttribute('class', 'hc-pulse');
      pulse.setAttribute('aria-hidden', 'true');
      pulse.style.fill = 'none';
      pulse.style.stroke = 'currentColor';
      pulse.style.strokeWidth = '1.6';
      pulse.style.opacity = '0';
      ring[0].parentNode.insertBefore(pulse, ring[0]);
      tl.fromTo(
        pulse,
        { scale: 0.7, opacity: 0.5, svgOrigin: origin },
        {
          scale: 3,
          opacity: 0,
          duration: 1,
          ease: 'power2.out',
          onComplete: function () {
            if (pulse.parentNode) pulse.parentNode.removeChild(pulse);
          },
        },
        0.8
      );
    }

    var started = false;
    function play() {
      if (started) return;
      started = true;
      var wait = Math.max(0.05, 0.5 - (performance.now() - startedAt) / 1000);
      ctx.add(function () {
        G.delayedCall(wait, function () {
          tl.play(0);
        });
      });
    }
    function finish() {
      started = true;
      tl.progress(1);
    }
    ST.create({
      trigger: card,
      start: 'top 84%',
      once: true,
      onEnter: play,
      onEnterBack: finish,
      onLeave: finish,
    });
    return function () {
      if (pulse && pulse.parentNode) pulse.parentNode.removeChild(pulse);
    };
  }

  function parallax(G, q) {
    var card = q('.hero-card')[0];
    var svg = q('.hero-chart')[0];
    if (!card || !svg || !window.ScrollTrigger) return;
    G.fromTo(
      svg,
      { y: 18 },
      {
        y: -18,
        ease: 'none',
        scrollTrigger: { trigger: card, start: 'top bottom', end: 'bottom top', scrub: 0.6 },
      }
    );
  }

  /* ------------------------------------------------------------ revealing */
  function countUp(G, ctx, els) {
    if (counted) return;
    counted = true;
    els.forEach(function (stat, i) {
      var num = stat.querySelector('.stat-num');
      if (!num) return;
      var target = parseInt(num.getAttribute('data-value') || num.textContent, 10);
      if (!isFinite(target)) return;
      num.style.minWidth = num.offsetWidth + 'px'; // raqam kengayganda matn "sakramasin"
      num.textContent = '0';
      var o = { v: 0 };
      ctx.add(function () {
        G.to(o, {
          v: target,
          duration: 1.5,
          delay: 0.1 + i * 0.12,
          ease: 'power3.out',
          snap: { v: 1 },
          onUpdate: function () {
            num.textContent = o.v;
          },
          onComplete: function () {
            num.textContent = target;
            num.style.minWidth = '';
          },
        });
      });
    });
  }

  function revealer(G, ctx, q) {
    var ST = window.ScrollTrigger;
    return function (sel, opt) {
      var els = q(sel);
      if (!els.length || !ST) return;
      opt = opt || {};
      var shown = [];
      G.set(els, { opacity: 0, y: opt.y == null ? 32 : opt.y });
      function show(batch) {
        var fresh = batch.filter(function (el) {
          if (shown.indexOf(el) > -1) return false;
          shown.push(el);
          return true;
        });
        if (!fresh.length) return;
        ctx.add(function () {
          G.to(fresh, {
            opacity: 1,
            y: 0,
            duration: opt.dur || 0.9,
            ease: M.ease.out,
            stagger: opt.stagger || 0.08,
            clearProps: CLEAR,
          });
        });
        if (opt.onShow) opt.onShow(fresh);
      }
      ST.batch(els, {
        start: 'top 90%',
        once: true,
        onEnter: show,
        onEnterBack: show,
        onLeave: show,
      });
    };
  }

  /* --------------------------------------------------------------- build */
  function build(root, hero) {
    var G = window.gsap;
    built = true;
    var startedAt = performance.now();
    M.scope(
      'landing',
      function (ctx) {
        try {
          var q = G.utils.selector(root);
          var cleanups = [];
          sample = root.querySelector('.chapter-card');

          // sonlarning yakuniy qiymati (sanash yarim yo‘lda to‘xtatilsa ham tiklanadi)
          var nums = q('.stat-num');
          var finals = nums.map(function (n) {
            return n.getAttribute('data-value') || n.textContent;
          });
          cleanups.push(function () {
            nums.forEach(function (n, i) {
              n.textContent = finals[i];
              n.style.minWidth = '';
            });
          });

          if (hero === 'full') {
            heroFull(G, root, q);
            var off = chartIntro(G, ctx, q, startedAt);
            if (off) cleanups.push(off);
          } else if (hero === 'short') {
            heroShort(G, q);
          }
          parallax(G, q);

          var reveal = revealer(G, ctx, q);
          reveal('.stat', {
            y: 28,
            stagger: 0.1,
            onShow: function (els) {
              countUp(G, ctx, els);
            },
          });
          reveal('.catalogue .section-head', { y: 28, dur: 1 });
          reveal('.part-head', { y: 22 });
          reveal('.card-item', { y: 44, stagger: 0.08, dur: 1 });
          reveal('.method .section-head', { y: 28, dur: 1 });
          reveal('.step', { y: 36, stagger: 0.1 });
          reveal('.site-footer .wrap', { y: 16 });

          return function () {
            cleanups.forEach(function (fn) {
              fn();
            });
          };
        } catch (err) {
          console.error('[Motion] landing', err);
          setTimeout(teardown, 0); // yarim yaratilgan hammasini qaytaramiz
        }
      },
      root
    );
    M.refresh();
  }

  /* ------------------------------------------------------------- events */
  M.on('view:landing', function (e) {
    var root = document.getElementById('landing');
    if (!root || !M.ok()) return;
    var first = root.querySelector('.chapter-card');
    if (built && sample === first) return; // bosh sahifada qoldik (masalan, #boblar'ga o‘tdik)

    var hash = e && e.hash;
    var hero;
    if (built || hash === 'boblar') hero = 'none';
    else if (!played) hero = performance.now() < 2500 ? 'full' : 'none';
    else hero = 'short';
    played = true;

    teardown();
    build(root, hero);

    // bosh sahifa yashirilganda (reader ko‘rinsa) — hammasini qaytaramiz, hodisa kelmasa ham
    if (window.MutationObserver) {
      watcher = new MutationObserver(function () {
        if (root.hidden) teardown();
      });
      watcher.observe(root, { attributes: true, attributeFilter: ['hidden'] });
    }
  });

  M.on('view:reader', teardown);
  M.on('settle', teardown);
  M.on('chapter:leave', function () {
    var root = document.getElementById('landing');
    if (root && root.hidden) teardown();
  });
})();
