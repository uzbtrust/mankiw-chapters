/* MOTION · o‘qish maketi harakati. Faqat Motion.on(...) orqali ulaning — qarang docs/DESIGN.md
   Bu yerda: bob sarlavhasi kirishi, sirpanuvchi faol belgilar, yopishqoq panel sarlavhasi,
   bob oxiri kirishi va taqdimot rejimi (slayd almashinuvi, boshqaruv paneli).
   Hamma tween Motion.scope ichida; "settle" va "chapter:leave" da qaytariladi. */
(function () {
  'use strict';
  var G = window.gsap;
  var SCOPES = ['reader', 'reader-bar', 'reader-end', 'slide', 'pres-bar'];

  function q(sel, root) {
    return (root || document).querySelector(sel);
  }
  function list(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  /* ---- Sirpanuvchi faol belgi (chap bob ro‘yxati va o‘ng mundarija) ------------------- */
  var tracks = [];
  function initTracks() {
    if (tracks.length) return;
    list('.rail-track').forEach(function (track) {
      var t = {
        track: track,
        ind: q('.rail-ind', track),
        nav: q('nav', track),
        on: false,
      };
      if (!t.ind || !t.nav) return;
      tracks.push(t);
      if (window.ResizeObserver) {
        new ResizeObserver(function () {
          place(t, false);
        }).observe(track);
      }
    });
  }
  function trackFor(navId) {
    for (var i = 0; i < tracks.length; i++) if (tracks[i].nav.id === navId) return tracks[i];
    return null;
  }
  function place(t, animate) {
    if (!t) return;
    var link = q('a.active', t.nav);
    var tr = t.track.getBoundingClientRect();
    if (!link || !tr.height) {
      t.on = false;
      t.ind.classList.remove('is-on');
      return;
    }
    var lr = link.getBoundingClientRect();
    var y = Math.round((lr.top - tr.top) * 10) / 10;
    var h = Math.round(lr.height * 10) / 10;
    var wasOn = t.on;
    t.on = true;
    t.track.classList.add('has-ind');
    if (G) {
      if (animate && wasOn && Motion.ok())
        G.to(t.ind, { y: y, height: h, duration: 0.5, ease: 'power3.inOut', overwrite: true });
      else G.set(t.ind, { y: y, height: h });
    } else {
      t.ind.style.transform = 'translateY(' + y + 'px)';
      t.ind.style.height = h + 'px';
    }
    t.ind.classList.add('is-on');
  }

  /* ---- Yopishqoq panelda bob nomi: sarlavha ketgach sekin paydo bo‘ladi ---------------- */
  function setupBar() {
    Motion.scope(
      'reader-bar',
      function () {
        var name = q('#bar-title');
        var header = q('#chapter-header');
        var bar = q('.reader-bar');
        if (!name || !header || !bar || !window.ScrollTrigger) return;
        var navH = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 52;
        var shown = false;
        var apply = function (on) {
          if (on === shown) return;
          shown = on;
          G.to(name, {
            opacity: on ? 1 : 0,
            y: on ? 0 : 6,
            duration: Motion.dur.xs + 0.1,
            ease: Motion.ease.soft,
            overwrite: true,
          });
        };
        G.set(name, { opacity: 0, y: 6 });
        var st = ScrollTrigger.create({
          trigger: header,
          start: function () {
            return 'bottom top+=' + Math.round(navH + bar.offsetHeight);
          },
          end: '+=1000000',
          onToggle: function (self) {
            apply(self.isActive);
          },
        });
        apply(st.isActive);
      },
      q('#reader')
    );
  }

  /* ---- Bob sarlavhasi va yon panellar kirishi ------------------------------------------- */
  Motion.on('view:reader', function (d) {
    initTracks();
    bindInlineToc();
    var chapterTrack = trackFor('chapter-nav');
    var tocTrack = trackFor('toc-nav');
    if (tocTrack) place(tocTrack, false);
    if (chapterTrack) place(chapterTrack, !d.fromLanding);
    setupBar();

    Motion.scope(
      'reader',
      function (ctx) {
        var header = q('#chapter-header');
        if (!header) return;
        var h1 = q('h1', header);
        var items = list('.eyebrow, h1, .english-title, .lead, .chapter-facts', header);
        if (d.fromLanding) {
          /* Sarlavha: qator-niqob bilan pastdan ochiladi (Apple uslubi); tugagach DOM tiklanadi. */
          var split = null;
          if (h1 && window.SplitText) {
            try {
              split = SplitText.create(h1, { type: 'lines', mask: 'lines', linesClass: 'rd-line' });
              ctx.data.push(split);
              items = items.filter(function (el) {
                return el !== h1;
              });
              G.from(split.lines, {
                yPercent: 108,
                duration: 0.7,
                stagger: 0.08,
                ease: Motion.ease.out,
                onComplete: function () {
                  split.revert();
                },
              });
            } catch (e) {
              split = null;
            }
          }
          G.fromTo(
            items,
            { opacity: 0, y: 32 },
            {
              opacity: 1,
              y: 0,
              duration: 0.5,
              stagger: 0.045,
              ease: Motion.ease.out,
              clearProps: 'transform,opacity',
            }
          );
          G.fromTo(
            '.chapter-sidebar',
            { opacity: 0, x: -16 },
            {
              opacity: 1,
              x: 0,
              duration: 0.6,
              delay: 0.1,
              ease: Motion.ease.out,
              clearProps: 'transform,opacity',
            }
          );
          G.fromTo(
            '.toc-sidebar',
            { opacity: 0, x: 16 },
            {
              opacity: 1,
              x: 0,
              duration: 0.6,
              delay: 0.1,
              ease: Motion.ease.out,
              clearProps: 'transform,opacity',
            }
          );
        } else {
          G.fromTo(
            items,
            { opacity: 0, y: 14 },
            {
              opacity: 1,
              y: 0,
              duration: 0.4,
              stagger: 0.03,
              ease: Motion.ease.soft,
              clearProps: 'transform,opacity',
            }
          );
        }
      },
      q('#reader')
    );
  });

  /* Ichki mundarija ochilganda ro‘yxat yumshoq ochiladi (height + opacity) */
  var tocBound = false;
  function bindInlineToc() {
    var host = q('#inline-toc');
    if (tocBound || !host) return;
    tocBound = true;
    host.addEventListener(
      'toggle',
      function (e) {
        var det = e.target;
        if (!det || !det.open || !Motion.ok()) return;
        var box = q('.toc-items', det);
        if (!box) return;
        G.fromTo(
          box,
          { height: 0, opacity: 0, overflow: 'hidden' },
          {
            height: 'auto',
            opacity: 1,
            duration: 0.45,
            ease: Motion.ease.out,
            clearProps: 'height,opacity,overflow',
            onComplete: Motion.refresh,
          }
        );
      },
      true
    );
  }

  Motion.on('section:active', function () {
    place(trackFor('toc-nav'), true);
  });

  /* ---- Bob oxiri: ko‘rinishga kelganda yumshoq paydo bo‘ladi ---------------------------- */
  Motion.on('chapter:ready', function () {
    var end = q('#chapter-end');
    if (!end || !end.children.length || !window.ScrollTrigger) return;
    var items = [];
    list(':scope > *', end).forEach(function (el) {
      if (el.classList.contains('chapter-end-nav')) items.push.apply(items, list(':scope > *', el));
      else items.push(el);
    });
    Motion.scope(
      'reader-end',
      function () {
        G.fromTo(
          items,
          { opacity: 0, y: 28 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            stagger: 0.08,
            ease: Motion.ease.out,
            clearProps: 'transform,opacity',
            scrollTrigger: {
              trigger: end,
              start: 'top 88%',
              once: true,
              onLeave: function (self) {
                if (self.animation) self.animation.progress(1);
              },
            },
          }
        );
      },
      end
    );
    Motion.refresh();
  });
  Motion.on('models:mounted', function () {
    Motion.refresh();
  });

  /* ---- Taqdimot rejimi -------------------------------------------------------------------- */
  var entering = false;
  Motion.on('presentation:enter', function () {
    entering = true;
    var bar = q('#presentation-bar');
    if (!bar) return;
    Motion.scope(
      'pres-bar',
      function () {
        G.fromTo(
          bar,
          { opacity: 0, y: 28 },
          {
            opacity: 1,
            y: 0,
            duration: 0.5,
            delay: 0.1,
            ease: Motion.ease.out,
            clearProps: 'transform,opacity',
          }
        );
      },
      bar
    );
  });
  /* Slayd almashinuvi: yo‘nalishga qarab qisqa surilish + xira bo‘lish (≤ 0.5 s) */
  Motion.on('presentation:slide', function (d) {
    var first = entering;
    entering = false;
    if (!d || !d.el) return;
    Motion.scope(
      'slide',
      function () {
        if (first)
          G.fromTo(
            d.el,
            { opacity: 0, y: 28 },
            { opacity: 1, y: 0, duration: 0.5, ease: Motion.ease.out, clearProps: 'transform,opacity' }
          );
        else
          G.fromTo(
            d.el,
            { opacity: 0, x: 56 * (d.direction || 1) },
            { opacity: 1, x: 0, duration: 0.45, ease: Motion.ease.out, clearProps: 'transform,opacity' }
          );
      },
      d.el
    );
  });
  Motion.on('presentation:exit', function () {
    entering = false;
    Motion.revert('slide');
    Motion.revert('pres-bar');
    setupBar();
  });

  /* ---- Hayot sikli ------------------------------------------------------------------------- */
  Motion.on('chapter:leave', function () {
    SCOPES.forEach(Motion.revert);
  });
  Motion.on('settle', function () {
    SCOPES.forEach(Motion.revert);
  });
  window.addEventListener('afterprint', function () {
    if (q('#reader') && !q('#reader').hidden) setupBar();
  });
})();
