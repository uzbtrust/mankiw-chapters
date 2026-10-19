/* MOTION · maqola mazmuni harakati. Faqat Motion.on(...) orqali ulaning — qarang docs/DESIGN.md

   1) Sarlavha / karta / formula / jadval / chizma — ko‘rinishga kelganda bir marta yumshoq paydo bo‘ladi
      (ScrollTrigger.batch, once). Oddiy abzaslar va ro‘yxatlar HECH QACHON animatsiya qilinmaydi.
   2) SVG chizmalar: uzluksiz egri chiziqlar DrawSVGPlugin bilan "chiziladi", so‘ng ortiqchalik
      yuzalari va yozuvlar paydo bo‘ladi (jami ≈ 1 s).
   3) details.answer: summary bosilganda .answer-body balandligi + shaffofligi silliq ochiladi / yopiladi.
      Boshqa joydan (d.open = …, havola, chop etish) ochilsa — darhol, animatsiyasiz.
   4) anchor:jump → havola ustidagi hamma narsa darhol ko‘rinadi; settle / chapter:leave → hammasi tiklanadi.
   Hech narsa CSS orqali yashirilmaydi: boshlang‘ich holat faqat shu yerda (gsap) o‘rnatiladi. */
(function () {
  'use strict';
  if (!window.Motion) return;

  var M = window.Motion;
  var SCOPE = 'chapter';
  var HEADINGS = '.lesson-section > .section-kicker, .lesson-section > h2';
  var CARDS = [
    '.example',
    '.callout',
    '.recap',
    '.warning',
    '.formula',
    '.key-concepts',
    '.concept-grid',
    '.comparison',
    '.step-list',
    'figure.diagram',
  ].join(',');
  var TABLES = '.table-wrap';
  // chizma egri chiziqlari (demand / supply / ikkinchi chiziqlar) — o‘qlar va to‘r chiziqlari emas
  var CURVE_STROKES = ['#17695f', '#c06843', '#82563f', '#a14e30', '#9d472e', '#3f968a', '#7d86a0'];
  // prettier-ignore
  var AREA_FILLS = [
    '#d4e9df', '#d7eee7', '#dcece7', '#d8e9df', '#e0eee7', '#91c5b0', '#b5d9cc', '#cbe7dd',
    '#f2dacf', '#f4ddcd', '#f7e8df', '#d4b2a0', '#e6bfa9', '#f0bdb2', '#d98258', '#f2ded5',
    '#dec878', '#d9e4f2', '#e2e8f1', '#edf0ee',
  ];

  var state = null; // { items: [{ el, done() }] }
  var pendingJump = null; // anchor:jump chapter:ready dan oldin kelishi mumkin
  var runs = new Map(); // details.answer -> animatsiya

  function G() {
    return window.gsap;
  }
  function all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }
  function inAnswer(el) {
    return !!el.closest('details.answer');
  }
  function tidy(el) {
    if (el.hasAttribute('style') && !el.getAttribute('style')) el.removeAttribute('style');
  }
  function container() {
    return document.getElementById('chapter-content');
  }

  /* ------------------------------------------------------------------ 1) paydo bo‘lish */
  function setupReveal(root, items) {
    var g = G();
    var st = window.ScrollTrigger;
    if (!st) return;

    function group(targets, y, dur) {
      targets = targets.filter(function (el) {
        return !inAnswer(el);
      });
      if (!targets.length) return;
      g.set(targets, y ? { opacity: 0, y: y } : { opacity: 0 });
      var show = function (batch, fired) {
        // "once" ni o‘zimiz bajaramiz: ScrollTrigger yaratilish paytida (refresh ichida) o‘zini o‘ldirsa xato beradi
        requestAnimationFrame(function () {
          (fired || []).forEach(function (t) {
            t.kill();
          });
        });
        g.to(batch, {
          opacity: 1,
          y: 0,
          duration: dur,
          ease: M.ease.out,
          stagger: 0.08,
          overwrite: 'auto',
          clearProps: 'opacity,transform',
          onComplete: function () {
            batch.forEach(tidy);
          },
        });
      };
      var triggers = st.batch(targets, {
        start: 'top 88%',
        interval: 0.1,
        batchMax: 4,
        onEnter: show,
        onEnterBack: show,
        onLeave: show,
      });
      triggers.forEach(function (t) {
        items.push({
          el: t.trigger,
          done: function () {
            g.killTweensOf(t.trigger);
            g.set(t.trigger, { clearProps: 'opacity,transform' });
            tidy(t.trigger);
            t.kill();
          },
        });
      });
    }

    group(all(HEADINGS, root), 22, 0.8);
    group(all(CARDS, root), 28, 0.9);
    group(all(TABLES, root), 0, 0.7);
  }

  /* ------------------------------------------------------------------ 2) SVG chizish */
  function curvesOf(svg) {
    var out = [];
    all('path, polyline, line', svg).forEach(function (el) {
      if (el.closest('defs, marker')) return;
      var stroke = el.getAttribute('stroke');
      if (CURVE_STROKES.indexOf(stroke) < 0) return;
      if (
        el.hasAttribute('stroke-dasharray') ||
        el.hasAttribute('marker-end') ||
        el.hasAttribute('marker-start')
      )
        return;
      if (parseFloat(el.getAttribute('stroke-width') || '1') < 2.5) return;
      var fill = el.getAttribute('fill');
      if (fill && fill !== 'none') return;
      var len = 0;
      try {
        len = el.getTotalLength();
      } catch (e) {
        len = 0;
      }
      if (len > 40) out.push(el);
    });
    return out;
  }
  function areasOf(svg) {
    return all('polygon, rect, path', svg).filter(function (el) {
      return !el.closest('defs, marker') && AREA_FILLS.indexOf(el.getAttribute('fill')) >= 0;
    });
  }

  function setupDraw(root, items) {
    var g = G();
    if (!window.ScrollTrigger || !window.DrawSVGPlugin) return;
    all('figure.diagram > svg', root).forEach(function (svg) {
      if (inAnswer(svg)) return;
      var curves = curvesOf(svg);
      if (!curves.length) return;
      var areas = areasOf(svg);
      var marks = all('text, circle', svg).filter(function (el) {
        return !el.closest('defs, marker') && areas.indexOf(el) < 0;
      });
      var tl = g.timeline({
        scrollTrigger: { trigger: svg, start: 'top 85%', toggleActions: 'play none none none' },
        defaults: { ease: 'power2.out' },
        onComplete: function () {
          g.set(curves, { clearProps: 'strokeDasharray,strokeDashoffset' });
          g.set(areas.concat(marks), { clearProps: 'opacity' });
          curves.concat(areas, marks).forEach(tidy);
          if (tl.scrollTrigger) tl.scrollTrigger.kill();
        },
      });
      tl.from(curves, { drawSVG: '0%', duration: 0.7, ease: 'power2.inOut', stagger: { amount: 0.25 } }, 0.1);
      if (areas.length) tl.from(areas, { opacity: 0, duration: 0.45, stagger: { amount: 0.15 } }, 0.5);
      if (marks.length) tl.from(marks, { opacity: 0, duration: 0.4, stagger: { amount: 0.25 } }, 0.55);
      items.push({
        el: svg,
        done: function () {
          tl.revert(); // hammasini asl, to‘liq ko‘rinadigan holatga qaytaradi (ScrollTrigger ham o‘ladi)
        },
      });
    });
  }

  // Bob oxiriga yetganda ekranda turgan, lekin "88%" chizig‘iga yetmay qolgan narsa bo‘lmasin.
  function setupSafetyNet(root, items) {
    window.ScrollTrigger.create({
      trigger: root,
      start: 'bottom bottom+=2',
      onEnter: flush,
      onEnterBack: flush,
    });
    function flush() {
      items.slice().forEach(function (it) {
        var r = it.el.getBoundingClientRect();
        if (r.top < window.innerHeight) it.done();
      });
    }
  }

  /* ------------------------------------------------------------------ 4) sakrash */
  function jumpTo(target) {
    if (!state || !target) return;
    state.items.slice().forEach(function (it) {
      if (it.el === target || it.el.contains(target) || precedes(it.el, target)) it.done();
    });
  }
  function precedes(el, target) {
    return !!(target.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_PRECEDING);
  }

  /* ------------------------------------------------------------------ 3) javoblar */
  function clearBody(body) {
    G().set(body, { clearProps: 'height,paddingTop,paddingBottom,opacity,overflow' });
    tidy(body);
  }
  function stopAnswers() {
    runs.forEach(function (tw, d) {
      tw.kill();
      var body = d.querySelector(':scope > .answer-body');
      if (body) clearBody(body);
      d.classList.remove('is-closing');
    });
    runs.clear();
  }
  function toggleAnswer(d) {
    var g = G();
    var body = d.querySelector(':scope > .answer-body');
    var opening = d.classList.contains('is-closing') || !d.open;
    var prev = runs.get(d);
    var fromH = null;
    var fromO = 0;
    if (prev) {
      prev.kill();
      runs.delete(d);
      if (body) {
        fromH = body.offsetHeight;
        fromO = parseFloat(getComputedStyle(body).opacity);
      }
    }
    if (!body) {
      if (d.open !== opening) {
        d._c50 = true;
        d.open = opening;
      }
      return;
    }
    d.classList.remove('is-closing');
    if (opening) {
      if (!d.open) {
        d._c50 = true;
        d.open = true;
      }
      clearBody(body);
      var cs = getComputedStyle(body);
      var pt = parseFloat(cs.paddingTop);
      var pb = parseFloat(cs.paddingBottom);
      var h = body.offsetHeight;
      var k = fromH == null || !h ? 0 : Math.min(1, fromH / h);
      g.set(body, {
        overflow: 'hidden',
        height: k * h,
        paddingTop: k * pt,
        paddingBottom: k * pb,
        opacity: fromO,
      });
      runs.set(
        d,
        g.to(body, {
          height: h,
          paddingTop: pt,
          paddingBottom: pb,
          opacity: 1,
          duration: 0.5,
          ease: M.ease.soft,
          onComplete: function () {
            runs.delete(d);
            clearBody(body);
            M.refresh();
          },
        })
      );
    } else {
      d.classList.add('is-closing');
      g.set(body, { overflow: 'hidden' });
      runs.set(
        d,
        g.to(body, {
          height: 0,
          paddingTop: 0,
          paddingBottom: 0,
          opacity: 0,
          duration: 0.36,
          ease: M.ease.inOut,
          onComplete: function () {
            runs.delete(d);
            d._c50 = true;
            d.open = false;
            d.classList.remove('is-closing');
            clearBody(body);
            M.refresh();
          },
        })
      );
    }
  }

  document.addEventListener('click', function (e) {
    if (!M.ok() || !e.target || !e.target.closest) return;
    var summary = e.target.closest('summary');
    if (!summary || e.defaultPrevented) return;
    var d = summary.parentNode;
    if (!d || !d.matches || !d.matches('#chapter-content details.answer')) return;
    e.preventDefault();
    toggleAnswer(d);
  });
  // d.open = … (barchasini ochish, havola, chop etish) — animatsiyasiz; faqat layout yangilanadi.
  document.addEventListener(
    'toggle',
    function (e) {
      var d = e.target;
      if (!d || !d.matches || !d.matches('#chapter-content details.answer')) return;
      if (d._c50) {
        d._c50 = false;
        return;
      }
      var tw = runs.get(d);
      if (tw) {
        tw.kill();
        runs.delete(d);
        var body = d.querySelector(':scope > .answer-body');
        if (body) clearBody(body);
        d.classList.remove('is-closing');
      }
      M.refresh();
    },
    true
  );

  /* ------------------------------------------------------------------ hayot sikli */
  function teardown() {
    stopAnswers();
    M.revert(SCOPE);
    state = null;
  }

  M.on('chapter:ready', function (d) {
    teardown();
    var root = (d && d.container) || container();
    if (!root || !M.ok() || !window.ScrollTrigger) {
      pendingJump = null;
      return;
    }
    var items = [];
    M.scope(
      SCOPE,
      function () {
        setupReveal(root, items);
        setupDraw(root, items);
        setupSafetyNet(root, items);
      },
      root
    );
    state = { items: items };
    var target = (d && d.anchor && document.getElementById(d.anchor)) || pendingJump;
    pendingJump = null;
    if (target && root.contains(target)) jumpTo(target);
    M.refresh();
  });

  M.on('anchor:jump', function (d) {
    var target = d && d.target;
    if (!target) return;
    if (state) jumpTo(target);
    else pendingJump = target;
  });

  M.on('answers:all', function () {
    stopAnswers();
    M.refresh();
  });
  M.on('models:mounted', function () {
    M.refresh();
  });
  M.on('chapter:leave', function () {
    pendingJump = null;
    teardown();
  });
  M.on('settle', function () {
    teardown();
  });
})();
