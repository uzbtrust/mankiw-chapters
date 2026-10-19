# Iqtisodiyot — design & motion brief

Shared contract for everyone editing `src/`. Read it fully before touching a file.

## 1. What this site is (do not lose sight of it)

A study site for one student preparing for an **oral university exam** on chapters 1–10 of Mankiw's
*Principles of Economics* (10e), explained in **Uzbek (Latin, with `o‘` `g‘` using U+2018)**.
The reader must be able to read long explanations comfortably, understand graphs, open worked answers,
use interactive models, and present a chapter section-by-section. It is used on **phones** and on slow
connections. The mood is **calm, focused, quiet** — not flashy.

Chapter content (`content/chapters/*`) follows **[RULE.md](../RULE.md)** — the single standard for chapter structure,
components, LaTeX and diagram colours, enforced by `scripts/build.py` (`check_standard`). Design work in `src/` must not
change chapter files; if a new component is needed, add its CSS here, document it in RULE.md §5 and the check in build.py.

## 2. Hard constraints

* **Quality over size (owner's decision).** There is **no strict byte budget** — do not cut polish, motion or
  detail to save bytes. Still keep the architecture lazy (chapters, models and search load on demand), no
  external fonts/CDNs/icon fonts, and only the GSAP bundle already in the build (`gsap`, `ScrollTrigger`,
  `ScrollToPlugin`, `SplitText`, `DrawSVGPlugin`, `CustomEase` — registered in `src/js/motion/00-core.js`;
  more GSAP plugins such as `Flip` may be added to the vendor list in `scripts/build.py` if truly needed —
  ask the lead). Avoid pointless bloat (huge base64 blobs, duplicated CSS), but never trade quality for bytes.
* **Fonts = San Francisco via the system stack** (`var(--font)`). Never load a webfont. Use
  `font-weight` 400/500/600/700, tight tracking on large type (`--track-display`, `--track-hero`),
  `font-variant-numeric: tabular-nums` for numbers.
* **Accessibility.** WCAG AA contrast in light and dark, visible `:focus-visible`, ≥44×44 px touch
  targets on touch, semantic HTML, `prefers-reduced-motion` honoured (`Motion.ok()`), nothing important
  conveyed by colour alone, text never smaller than 12 px (body ≥ 16 px).
* **Never hide content behind JS.** Content must be visible if GSAP fails to load. Initial hidden states
  are set by GSAP at runtime (`gsap.set` / `from` / `fromTo`) — never by CSS. Every reveal must also
  complete on `onEnterBack` / `onLeave`, and must be undone by `Motion.revert(scope)` / the `settle`
  event (print, presentation mode, anchor jumps, reduced-motion toggled on).
* **Offline build must keep working** (all CSS/JS is inlined into one HTML file by `scripts/build.py`).
  No absolute asset URLs in CSS/JS; no `fetch` of new files.
* **Dark mode** = `<html class="dark">` (set before first paint by `partials/head.html`). Only change
  tokens in `00-tokens.css`; components use `var(--…)` so dark mode is automatic. Test both.
* **Mobile first.** Verify at 375 px, 768 px, 1440 px wide. No horizontal page scroll. Wide diagrams/tables
  scroll inside their own container.
* Respect `docs/chapter-contract.md` class names used by chapter HTML (list in §6).

## 2b. Locked decisions

* UI copy stays Uzbek. Keep every existing label; you may rewrite microcopy for clarity/brevity.
* No emoji. Icons = tiny inline SVG (1.5 px round-cap strokes, `currentColor`, SF-Symbols feel) or plain
  typographic glyphs. No icon font.
* Only one accent colour (`--accent`, Apple blue). `--demand` (blue) / `--supply` (orange) / `--good` /
  `--bad` / `--social` are *semantic chart colours*, not decoration.

## 3. Design language — "Apple, quietly"

Reference: apple.com product pages, Apple Newsroom articles, developer.apple.com documentation.

* **Space is the design.** Big vertical rhythm (`--s-8`…`--s-10` between sections), generous line height,
  short measures. When in doubt, remove a border, a box, a label.
* **Type does the work.** Huge display headings (600–700, `--track-display`), calm 17–19 px body in
  `--fg`, secondary text in `--fg-3`. A clear 3-level hierarchy per screen. Centred headings on
  landing sections; left-aligned in articles.
* **Surfaces, not outlines.** Prefer `--bg-alt` cards with `--r-lg`/`--r-xl` radii and no border;
  hairlines (`--line`) only to separate list rows. Shadows are soft and rare (`--shadow-sm|md`).
* **Glass chrome.** Top bar and sticky sub-bars: `background: var(--glass); backdrop-filter: saturate(180%)
  blur(20px)` + 1 px `--line-soft` bottom edge. Dialogs/sheets get `--shadow-lg` + blurred `--backdrop`.
* **Pills & links.** Primary action = `--accent` pill (`--r-pill`), secondary = text link with a `›`.
  Hover = slight lightening, press = `scale(.97)`. No underlined links in chrome.
* **Colour discipline.** Light: white / `#f5f5f7` alternation. Dark: black / `#111113` / `#1c1c1e`.
  No beige, no green paper tint, no gradients except a very subtle one on the hero.
* **Alignment.** Everything snaps to the 8 px scale. Content width `--max` (1120) for landing,
  `--read` (700) for article text, `--max-wide` (1280) for the three-column reader shell.

## 4. Motion language — "smooth, slightly springy, never showy"

GSAP only for anything that moves with choreography; CSS transitions only for hover/press/colour.
Animate **`transform` and `opacity` only** (never `top/left/height/width` except unavoidable accordion
height with `overflow:hidden`). Use `will-change` sparingly and remove it afterwards.

| Token | Use |
|---|---|
| `Motion.dur.xs .25 / s .5 / m .8 / l 1.2` | durations |
| `expo.out` (`Motion.ease.out`) | entrances, big reveals |
| `power3.out` (`Motion.ease.soft`) | default |
| `power3.inOut` | position changes, indicators |
| `apple` (CustomEase 0.28,0.11,0.32,1) | UI micro-interactions |

Patterns that feel Apple: fade + 24–40 px rise with 0.06–0.1 s stagger; headline mask/word reveal
(`SplitText` `type:'lines,words'` + `mask:'lines'` — revert it after); sliding active indicators;
number count-ups with `snap`; SVG curves drawn with `DrawSVGPlugin`; subtle parallax on hero visual
(≤ 40 px); dialog = scale .96→1 + fade + backdrop blur-in; accordion = height + opacity.
Scroll reveals use `ScrollTrigger.batch` or one trigger per block with `once:true`, `start:'top 88%'`.
**Do not animate every paragraph** — animate section headings, cards, figures, and first-view elements.
Timelines are short (< 1.4 s for the whole hero; < 0.7 s for anything in the reader).

### Lifecycle

Subscribe only through `Motion.on(event, handler)` (events listed in `src/js/motion/00-core.js`). Create all
tweens inside `Motion.scope('<name>', () => {…}, rootEl)` so they can be reverted:

* `chapter:leave` → `Motion.revert('chapter')` (and other scopes you created for that chapter)
* `settle` → revert / `progress(1)` everything so the page is in its final readable state
* After DOM size changes (images, details, models mounted) → `Motion.refresh()`

Motion modules may be loaded before `app/*.js`: do **not** touch app globals (`$`, `CHAPTERS`, `activeChapter`)
at load time; use `document.querySelector` inside handlers.

## 5. File ownership (one owner per file — never edit another owner's file)

| Owner | Files |
|---|---|
| **core (lead)** | `00-tokens.css`, `10-base.css`, `motion/00-core.js`, `app/00-core.js`, `app/90-boot.js`, `index.html`, `scripts/*`, `docs/*` |
| **chrome + landing** | `20-chrome.css`, `30-landing.css`, `partials/head.html`, `partials/chrome.html`, `partials/landing.html`, `app/10-landing.js`, `app/40-prefs.js`, `motion/20-chrome.js`, `motion/30-landing.js` |
| **reader** | `40-reader.css`, `80-dialogs.css`, `90-print.css`, `partials/reader.html`, `partials/dialogs.html`, `app/20-reader.js`, `app/30-reader-controls.js`, `app/50-search.js`, `app/60-mobile-nav.js`, `motion/40-reader.js`, `motion/80-dialogs.js` |
| **content** | `50-content.css`, `60-diagrams.css`, `motion/50-content.js` |
| **simulations** | `70-simulations.css`, `js/simulations.js`, `motion/70-simulations.js` |

Need a token, a new event, or a change in someone else's file? Do **not** edit it: put it in your final
report ("Requests") and work around it. You may add *new* tokens locally as custom properties scoped to your
own selector (e.g. `.landing { --card-pad: 32px }`).

CSS load order is the file-name order. Later files win; keep selectors shallow (≤ 3 levels) and scope to
your area so owners don't collide.

## 6. DOM contracts (JS depends on these — keep them)

**IDs** (all in `partials/*.html`): `landing boblar chapter-list total-diagrams total-answers resume-link
reader chapter-nav mobile-chapter-links reading-progress search-open search-dialog search-input search-status
search-results search-close theme-toggle font-down font-up mobile-nav-open mobile-nav mobile-nav-close
reader-position answer-toggle presentation-toggle print-button chapter-header inline-toc chapter-content
chapter-end toc-nav back-to-top presentation-bar slide-prev slide-next slide-position slide-exit announcer main`.

**Data/state hooks:** `[data-chapter]` and `[data-section]` links get class `active` (+ `aria-current` on
chapter links); `[data-complete]` button gets `.is-complete`; `body.is-presentation` while presenting;
`#reading-progress` width is set in `%`; `hidden` attribute toggles `#landing`/`#reader`/`#presentation-bar`
and each section in presentation mode; `<details class="answer" open>`; the buttons' `textContent`/`aria-label`
is rewritten by JS (so icons must live in a child element that JS does not overwrite **or** JS in your owned
file must be updated).

**Classes emitted by JS (restyle freely, keep names or change them in the owning JS file):**
`chapter-row row-number row-meta learned-tag row-arrow part-group part-title resume-link` (landing list) ·
`search-result quiet-button complete-button end-note chapter-end-nav chapter-loading load-error model-pending
english-title lead chapter-facts toc-items eyebrow` (reader).

**Classes in chapter HTML (content/ — fixed):** `lesson-section section-kicker example callout recap warning
formula table-wrap concept-grid comparison step-list key-concepts source-note diagram diagram-wide answer
q-number answer-body interactive[data-interactive]`, plus `<figure class="diagram"><svg …><figcaption>`,
`<details class="answer" data-kind data-q id>` / `<summary><span class="q-number">`, headings `h2 h3 h4`,
lists, `strong`, `a`, `table`.

**Classes emitted by `simulations.js`:** `sim-heading sim-intro sim-controls sim-control sim-check
sim-number sim-chart sim-metrics sim-metric sim-reading sim-note`.

## 7. Working method

```bash
# build to YOUR private dir (never ./dist), lenient so another owner's typo can't block you
python3 scripts/build.py --no-offline --lenient --out /private/tmp/claude-501/-Volumes-Rocket-Iqtisod/e2307a79-7d10-4345-9df7-2025f956ee7b/scratchpad/dist-<you>
python3 -m http.server <your-port> --directory <that dir>      # run in background
```

Browser pane is **shared with other agents**: first `tabs_create` your own tab and pass its `tabId` on every
call; never touch other tabs. Use `resize_window` (`mobile`, `tablet`, `desktop`, `colorScheme`) on *your*
tab; reset to desktop when done. Deep links: `/#bob-4`, `/#bob-7/c7-s3`, `/#boblar`, `/#bosh-sahifa`.
Rebuild after each edit batch (fast). Check `read_console_messages` for errors.

Verification checklist before reporting: light + dark · 375 / 768 / 1440 · keyboard tab order & focus ring ·
`prefers-reduced-motion` (emulate via `matchMedia` override or reasoning) · no console errors · deep link
jump leaves nothing invisible · print preview not broken (`@media print`) · `node --check` passes on JS.

No `npm install`, no deploying, no git, no edits outside your files, no changes to `content/`.

## 8. Final report format (short)

`Files changed` · `What it looks/behaves like` (3–6 bullets) · `Contracts you changed` · `Requests for other
owners` · `Known issues`. Do not paste code.

## 9. Contract changes made during the redesign (current state)

Documented so the next edit starts from reality, not from §6 above.

* **Top bar:** `.reading-line` (with `#reading-progress`) now lives *inside* `<header class="topbar">`. `#font-down` / `#font-up`
  keep their ids but are `.size-btn` inside `.size-control` (an `A` glyph, no `A−`/`A+` text). `#theme-toggle` holds two SVGs;
  `setTheme(dark, animate)` swaps them (View Transitions crossfade where supported) and persists `econ-dark` **only on a user
  click** — otherwise the system theme is followed. Head script sets `<html class="dark">` and `theme-color` before first paint.
* **Shared primitives** (`20-chrome.css`, documented at the top of the file): `.btn .btn-primary .btn-secondary .btn-lg .link-more
  .icon-button .quiet-button[.is-on|aria-pressed] kbd .skip-link`.
* **Landing list markup:** `.part-group > .part-head (.part-label, h3.part-title) + .part-cards > .card-item > a.chapter-card`.
  `#total-diagrams` / `#total-answers` carry `data-value`; `#resume-link` = `.resume-label` + `.resume-title`.
* **Reader:** sticky glass `.reader-bar` (`#bar-title`, `.bar-actions`) sits outside the grid; `.rail-track` / `.rail-ind` wrap
  `#chapter-nav` and `#toc-nav`; button labels live in `.qb-label` / `.cb-label` (written by `setLabel()` in `20-reader.js`);
  icon sprite `#rd-*` (`.rd-ico`) lives in `dialogs.html`; chapter end uses `.end-card .end-prev .end-next`; `#slide-progress`
  shows slide progress. `section:active` fires after `.active` is set. Presentation scales type via `--reader-size` on
  `#chapter-content`.
* **Content:** card surfaces use a local `--card` (`--bg-alt` in light, `--bg-elev` in dark). `details.answer.is-closing` while
  an answer animates shut. Diagrams are re-themed purely from CSS (attribute selectors on the original hex colours, plus
  per-figure overrides keyed on `aria-label` where the caption names a colour) — chapter HTML is untouched.
* **Simulations:** controls use `.sim-select`, switches (`role="switch"`), `--p` on ranges, HTML `.sim-legend`, `.is-long`
  metrics, `host.__sim.settle()`. Display values tween ~0.35 s via GSAP; final render uses the exact computed values
  (parity-tested against the original `simulations.js`: 430 samples, 0 mismatches).

* **Content standard (2026-10):** every chapter = lesson sections `cN-s1…` + `cN-terms` (`.key-concepts > dl`, `dt .en`) +
  `cN-quick` + `cN-review` + `cN-apps` + `cN-oral`; box labels fixed (`Oddiy misol.`, `Keng tarqalgan xato.`, `Qisqasi.` …).
* **Maths:** chapter HTML holds LaTeX (`\( \)`, `\[ \]`); build renders MathML via Temml (`scripts/tex.cjs`). Styles in
  `50-content.css` (`math`, `.formula-title`, `.formula-legend`); font = system math font (STIX Two Math), no webfont.
* **Tables:** build adds `class="t-stack"` + `data-label` to 4+ column tables; ≤ 560 px they render as cards.
* **Course data:** `content/course.json` (parts, `taughtInClass`) → global `COURSE`; chapter count is discovered from files
  and injected into partials via `<!--@count-->` / `<!--@count2-->`.

### Testing tip
When the in-app browser pane is hidden, `requestAnimationFrame` is throttled to ~2 fps and GSAP looks "half-faded" in
screenshots. Wait a few seconds (or `gsap.globalTimeline.progress(1)`) before judging a frame.
