#!/usr/bin/env python3
"""Iqtisodiyot saytini yig‘ish.

    python3 scripts/build.py                 # dist/ (Vercel) + outputs/ (internetsiz nusxa)
    python3 scripts/build.py --out /tmp/x    # boshqa papkaga yig‘ish
    python3 scripts/build.py --no-offline    # internetsiz nusxani yaratmaslik (tezroq)
    python3 scripts/build.py --lenient       # sintaksis xatosi bor JS faylni o‘tkazib yuborish
    python3 scripts/build.py --clean         # dist/ ni avval tozalash
    python3 scripts/build.py --lenient       # + RULE.md andozasidan chetlashish xato emas, ogohlantirish bo‘ladi
    python3 scripts/build.py --check 11      # faqat 11-bobni RULE.md bo‘yicha tekshirish, barcha xatolar ro‘yxati
    python3 scripts/build.py --status        # har bir bob: tayyor ✓ yoki nechta muammo qolgan

Bob qo‘shish: content/chapters/chapter-NN.html + .json va content/course.json (qism/bo‘lim). Qoidalar: RULE.md.

Manba:  content/chapters/*.html|json  ·  content/course.json  ·  src/index.html + src/partials/*  ·  src/css/*.css
        src/js/motion/*.js + src/js/app/*.js  ·  src/js/simulations.js  ·  node_modules/gsap
Natija: <out>/index.html va hash’langan <out>/assets/* , <out>/chapters/*  (qayta o‘zgartirmang!)
"""
import argparse
import gzip
import os
import hashlib
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

# Windows konsoli ham o‘zbekcha harflarni (o‘, g‘, ’) to‘g‘ri chiqarsin
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
CONTENT = ROOT / 'content' / 'chapters'
GSAP_DIR = ROOT / 'node_modules' / 'gsap' / 'dist'
ESBUILD = ROOT / 'node_modules' / '.bin' / ('esbuild.cmd' if os.name == 'nt' else 'esbuild')
TEX = ROOT / 'scripts' / 'tex.cjs'
COURSE_FILE = ROOT / 'content' / 'course.json'
GSAP_FILES = ['gsap', 'ScrollTrigger', 'ScrollToPlugin', 'SplitText', 'DrawSVGPlugin', 'CustomEase']

VOID = ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr')

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--out', default=str(ROOT / 'dist'))
ap.add_argument('--no-offline', action='store_true')
ap.add_argument('--lenient', action='store_true')
ap.add_argument('--clean', action='store_true')
ap.add_argument('--check', type=int, metavar='N', help='faqat N-bobni tekshirish (hech narsa yozilmaydi)')
ap.add_argument('--status', action='store_true', help='barcha boblarning RULE.md holati (qaysi bob tayyor)')
args = ap.parse_args()
OUT = Path(args.out).resolve()


def digest(s):
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()[:12]


def compact(d):
    return json.dumps(d, ensure_ascii=False, separators=(',', ':'))


# --------------------------------------------------------------------------- mazmun tekshiruvi
class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.sections, self.questions, self.interactive, self.text, self.bad, self.stack = [], [], [], [], [], [], []
        self.diagrams = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'section' and 'lesson-section' in a.get('class', ''):
            self.sections.append(a.get('id'))
            if self.stack:
                self.bad.append('Lesson section is not a root sibling: ' + str(a.get('id')))
        if tag == 'details' and 'answer' in a.get('class', ''):
            self.questions.append((a.get('data-kind'), a.get('data-q')))
        if tag == 'svg':
            self.diagrams += 1
        if 'data-interactive' in a:
            self.interactive.append(a['data-interactive'])
        if tag in ('script', 'style', 'iframe', 'html', 'head', 'body'):
            self.bad.append('Forbidden wrapper ' + tag)
        if any(k.lower().startswith('on') for k in a):
            self.bad.append('Inline handler')
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.bad.append('Unbalanced closing ' + tag)
            if tag in self.stack:
                self.stack = self.stack[: len(self.stack) - 1 - self.stack[::-1].index(tag)]
        else:
            self.stack.pop()

    def handle_data(self, d):
        self.text.append(d)


class Node:
    def __init__(self, tag, attrs=None):
        self.tag, self.attrs, self.children = tag, attrs or {}, []

    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.walk()

    def text(self, skip_answers=False):
        if self.tag in ('svg', 'annotation') or (skip_answers and self.tag == 'details' and 'answer' in self.attrs.get('class', '').split()):
            return ''
        return re.sub(r'\s+', ' ', ' '.join(c.text(skip_answers) if isinstance(c, Node) else c for c in self.children)).strip()

    def first(self, tag):
        return next((n for n in self.walk() if n.tag == tag), None)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Node('root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs))
        self.stack[-1].children.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_endtag(self, tag):
        if len(self.stack) > 1 and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_data(self, d):
        self.stack[-1].children.append(d)


# --------------------------------------------------------------------------- RULE.md andozasi
TAIL = ['terms', 'quick', 'review', 'apps', 'oral']
TAIL_KICKER = {'terms': r'Atamalar', 'quick': r'QuickQuiz · \d+ savol', 'review': r'Takrorlash · \d+ savol',
               'apps': r'Masalalar · \d+ topshiriq', 'oral': r'Og‘zaki imtihon'}
TAIL_TITLE = {'terms': 'Asosiy atamalar', 'quick': 'Tezkor savollar: javob va sabab', 'review': 'Takrorlash savollari',
              'apps': 'Masalalar va qo‘llash', 'oral': 'Og‘zaki javob rejasi va tuzoqlar'}
TAIL_KIND = {'quick': 'quick', 'review': 'review', 'apps': 'application'}
LESSON_LABEL = r'(?:\d+-\d+[a-z]?(?:–[a-z])?|Kirish|Yakun|Ilova)'
MAX_P_WORDS = 80
BOX_LABELS = {'callout': ['Oddiy misol.', 'Muhim.', 'Eslatma.'],
              'warning': ['Keng tarqalgan xato.', 'Imtihon tuzoqlari.', 'Diqqat.'],
              'recap': ['Qisqasi.']}


def strip_tags(h):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h)).strip()


def tex_unescape(t):
    return t.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&nbsp;', ' ')


# 360 px telefonda formula uchun joy — o‘sha formula shrifti em larida (asosiy matnda / javob ichida):
# display .formula ≈ 11,4 / 10,5;  step-list qatoridagi \( … \) ≈ 13,9 / 11,8.
# tex_width() haqiqiy o‘lchovdan −5…+9% adashadi (≈110 formula bilan solishtirilgan) — chegara shunga ozgina yuqoriroq.
FIT_EM = {'formula': {'main': 11.75, 'answer': 10.75}, 'step': {'main': 14.0, 'answer': 11.9}}
TEX_TOKEN = re.compile(r'\{,\}|\\[A-Za-z]+|\\.|\S')
TEX_EM = {r'\qquad': 2, r'\quad': 1, r'\,': .17, r'\:': .22, r'\;': .28, r'\!': -.17, '\\ ': .25,
          ',': .45, '{,}': .28, '/': .5, r'\%': .75, r'\Rightarrow': 1.56, r'\Longrightarrow': 2.16, r'\iff': 2.16, r'\implies': 2.16}
TEX_EM.update(dict.fromkeys(['=', '<', '>', r'\le', r'\ge', r'\leq', r'\geq', r'\approx', r'\ne', r'\neq', r'\equiv', r'\to'], 1.22))
TEX_EM.update(dict.fromkeys(['+', '-', r'\times', r'\cdot', r'\pm', r'\div'], 1.1))
TEX_EM.update(dict.fromkeys(['(', ')', '[', ']', '|', r'\{', r'\}', r'\lvert', r'\rvert', r'\vert'], .33))
TEX_EM.update({op: .5 * (len(op) - 1) + .17 for op in (r'\max', r'\min', r'\ln', r'\log', r'\exp', r'\lim')})


def _tex_arg(toks, i):
    """i dagi bitta argument: {…} guruhi yoki bitta token → (tokenlar, keyingi i)."""
    if i >= len(toks):
        return [], i
    if toks[i] != '{':
        return [toks[i]], i + 1
    depth, j = 0, i
    while j < len(toks):
        depth += {'{': 1, '}': -1}.get(toks[j], 0)
        j += 1
        if not depth:
            break
    return toks[i + 1:j - 1], j


def _tex_run(toks, s, d):
    """Tokenlar kengligi (em). s — o‘lcham ko‘paytuvchisi, d — display uslubi (TeX: unda \\frac to‘liq o‘lchamda)."""
    w, i = 0.0, 0
    while i < len(toks):
        t = toks[i]
        i += 1
        if t == '{':
            a, i = _tex_arg(toks, i - 1)
            w += _tex_run(a, s, d)
        elif t in (r'\frac', r'\dfrac', r'\tfrac'):
            a, i = _tex_arg(toks, i)
            b, i = _tex_arg(toks, i)
            k = s if t == r'\dfrac' or (t == r'\frac' and d) else s * .75
            w += max(_tex_run(a, k, False), _tex_run(b, k, False)) + .15 * s
        elif t in ('_', '^'):
            a, i = _tex_arg(toks, i)
            w += _tex_run(a, s * .7, False)
        elif t in (r'\text', r'\textrm', r'\mathrm', r'\operatorname'):
            a, i = _tex_arg(toks, i)
            w += .47 * s * len(''.join(a))
        elif t in (r'\left', r'\right'):
            a, i = _tex_arg(toks, i)
            w += 0 if a == ['.'] else .33 * s
        elif t in (r'\sum', r'\prod'):
            w += 1.2 * s
            while d and i < len(toks) and toks[i] in ('_', '^'):  # displayda chegaralar ostida/ustida turadi
                _, i = _tex_arg(toks, i + 1)
        elif t in TEX_EM:
            w += TEX_EM[t] * s
        else:
            w += s * (.75 if t[0] == '\\' else .5 if t.isdigit() else .68 if t.isupper() else .55)
    return w


def tex_width(tex, display=True):
    """Formulaning taxminiy kengligi (em): qatorlar (\\\\) ichidan eng kengi, & ustunlari qo‘shiladi."""
    cols = {}
    for line in re.sub(r'\\(?:begin|end)\{\w+\*?\}', '', tex).split('\\\\'):
        for k, cell in enumerate(line.split('&')):
            cols[k] = max(cols.get(k, 0), _tex_run(TEX_TOKEN.findall(cell), 1, display))
    return sum(cols.values())


def check_standard(n, body, meta):
    """RULE.md §4–§6 dagi mexanik qoidalar. Har bir buzilish — bitta tushunarli xabar."""
    errs = []
    flat = re.sub(r'<svg\b.*?</svg>', '', body, flags=re.S)
    secs = re.findall(r'<section class="lesson-section" id="([^"]+)">(.*?)</section>', flat, flags=re.S)
    ids = [i for i, _ in secs]
    k = len(ids) - len(TAIL)
    want = [f'c{n}-s{i}' for i in range(1, k + 1)] + [f'c{n}-{t}' for t in TAIL]
    if ids != want:
        errs.append(f'bo‘limlar tartibi/ID: kerak {want}, bor {ids}')
    titles = {s['id']: s['title'] for s in meta['sections']}
    for sid, inner in secs:
        m = re.match(r'\s*<div class="section-kicker">(.*?)</div>\s*<h2>(.*?)</h2>', inner, flags=re.S)
        if not m:
            errs.append(f'{sid}: bo‘lim <div class="section-kicker"> va <h2> bilan boshlanishi kerak')
            continue
        kicker, h2 = strip_tags(m[1]), strip_tags(m[2])
        tail = sid.split('-', 1)[1]
        if tail in TAIL:
            if not re.fullmatch(TAIL_KICKER[tail], kicker):
                errs.append(f'{sid}: kicker «{kicker}» → «{TAIL_KICKER[tail]}» shaklida bo‘lsin')
            if h2 != TAIL_TITLE[tail]:
                errs.append(f'{sid}: sarlavha «{TAIL_TITLE[tail]}» bo‘lsin')
            kinds = re.findall(r'<details class="answer" data-kind="([^"]+)"', inner)
            if tail in TAIL_KIND:
                if not kinds or set(kinds) != {TAIL_KIND[tail]}:
                    errs.append(f'{sid}: faqat data-kind="{TAIL_KIND[tail]}" javoblari bo‘lsin')
                cnt = re.search(r'(\d+)', kicker)
                if cnt and int(cnt[1]) != len(kinds):
                    errs.append(f'{sid}: kickerda {cnt[1]}, aslida {len(kinds)} savol')
            elif kinds:
                errs.append(f'{sid}: bu bo‘limda savol-javob bo‘lmasin')
        else:
            if not re.fullmatch(LESSON_LABEL + r' · \S.{0,60}', kicker):
                errs.append(f'{sid}: kicker «{kicker}» → «{n}-1a · Qisqa mavzu» (kitob raqami) yoki «Kirish · …» / «Yakun · …» / «Ilova · …» shaklida bo‘lsin')
            if '<details class="answer"' in inner:
                errs.append(f'{sid}: savol-javoblar faqat quick/review/apps bo‘limlarida')
        if titles.get(sid) != h2:
            errs.append(f'{sid}: JSON sections[].title h2 bilan bir xil bo‘lsin («{h2}»)')
    terms = dict(secs).get(f'c{n}-terms', '')
    dl = re.search(r'<div class="key-concepts">\s*<dl>(.*?)</dl>\s*</div>', terms, flags=re.S)
    if not dl:
        errs.append(f'c{n}-terms: <div class="key-concepts"><dl>…</dl></div> bo‘lsin')
    else:
        dts = re.findall(r'<dt>(.*?)</dt>', dl[1], flags=re.S)
        if len(dts) < 5:
            errs.append(f'c{n}-terms: kamida 5 ta atama bo‘lsin')
        if any('<span class="en">' not in d for d in dts):
            errs.append(f'c{n}-terms: har bir <dt> ichida <span class="en">English</span> bo‘lsin')
        if len(dts) != len(re.findall(r'<dd>', dl[1])):
            errs.append(f'c{n}-terms: har bir <dt> dan keyin bitta <dd>')
    oral = dict(secs).get(f'c{n}-oral', '')
    for need, what in [('<ul class="recap">', 'ul.recap'), ('<ol class="step-list">', 'ol.step-list'), ('<div class="warning">', 'div.warning')]:
        if need not in oral:
            errs.append(f'c{n}-oral: {what} bo‘lsin')
    for cls, labels in BOX_LABELS.items():
        for m in re.finditer(r'<div class="' + cls + r'">\s*(?:<p>)?\s*(<strong>(.*?)</strong>)?', flat):
            if m[2] not in labels:
                errs.append(f'.{cls} «<strong>{" / ".join(labels)}</strong>» bilan boshlansin, hozir: «{strip_tags(m[0])[:40]}»')
    for m in re.finditer(r'<details class="answer" data-kind="quick"[^>]*>.*?<div class="answer-body">\s*<p>\s*<strong>(.*?)</strong>', flat, flags=re.S):
        if not re.match(r'To‘g‘ri javob: [a-e]\) \S', m[1]):
            errs.append(f'QuickQuiz javobi «To‘g‘ri javob: b) variant matni.» bilan boshlansin, hozir: «{strip_tags(m[1])[:40]}»')
    if len(re.findall(r'<details class="answer" data-kind="quick"', flat)) != len(re.findall(
            r'<details class="answer" data-kind="quick"[^>]*>.*?<div class="answer-body">\s*<p>\s*<strong>', flat, flags=re.S)):
        errs.append('QuickQuiz: har javob <div class="answer-body"><p><strong>To‘g‘ri javob: …</strong> bilan boshlansin')
    for f in re.findall(r'<div class="formula">(.*?)</div>', flat, flags=re.S):
        if '\\[' not in f:
            errs.append('formula: .formula ichida LaTeX \\[ … \\] bo‘lsin, oddiy matn emas: ' + strip_tags(f)[:50])
    answers = [m.span() for m in re.finditer(r'<details class="answer".*?</details>', flat, flags=re.S)]
    for m in re.finditer(r'\\\[(.+?)\\\]', flat, flags=re.S):
        tex = tex_unescape(m[1]).strip()
        if '\\qquad' in tex:
            errs.append(f'formula «{tex[:50]}»: tenglamalarni \\qquad bilan yonma-yon yozmang — har biri alohida qatorda: '
                        '\\begin{gathered} … \\\\ … \\end{gathered} (RULE.md §6)')
            continue
        where = 'answer' if any(a <= m.start() < b for a, b in answers) else 'main'
        if (w := tex_width(tex)) > FIT_EM['formula'][where]:
            errs.append(f'formula telefonga sig‘maydi (≈{w:.1f}em > {FIT_EM["formula"][where]}em): «{tex[:50]}» — '
                        'qatorlarga bo‘ling: gathered yoki aligned (RULE.md §6)')
    for ol in re.finditer(r'<ol class="step-list">.*?</ol>', flat, flags=re.S):
        where = 'answer' if any(a <= ol.start() < b for a, b in answers) else 'main'
        for m in re.finditer(r'\\\((.+?)\\\)', ol[0], flags=re.S):
            tex = tex_unescape(m[1]).strip()
            if (w := tex_width(tex, display=False)) > FIT_EM['step'][where]:
                errs.append(f'qadamdagi formula telefonga sig‘maydi (≈{w:.1f}em > {FIT_EM["step"][where]}em): «{tex[:50]}» — '
                            'a/b o‘rniga \\dfrac{a}{b} yozing yoki ikki qadamga bo‘ling (RULE.md §6)')
    if re.search(r'<su[bp]>', flat):
        errs.append('<sub>/<sup> o‘rniga LaTeX \\( … \\) ishlating')
    for t in re.findall(r'<table>.*?</table>', flat, flags=re.S):
        if '<thead>' not in t or '<tbody>' not in t:
            errs.append('jadval: <thead> va <tbody> bo‘lsin')
    if len(re.findall(r'<table>', flat)) != len(re.findall(r'<div class="table-wrap"><table>', flat)):
        errs.append('jadval: har bir <table> <div class="table-wrap"> ichida bo‘lsin')
    for para in re.findall(r'<p>(.*?)</p>', flat, flags=re.S):
        w = len(strip_tags(re.sub(r'\\[\[(].*?\\[\])]', 'X', para)).split())
        if w > MAX_P_WORDS:
            errs.append(f'paragraf {w} so‘z (> {MAX_P_WORDS}): «{strip_tags(para)[:50]}…» — bo‘ling')
    return errs


def label_table(m):
    """Telefonda keng jadval kartalarga aylanadi: har bir katakka ustun nomi data-label bo‘lib yoziladi."""
    t = m[0]
    if 'colspan' in t or 'rowspan' in t:
        return t
    head = re.search(r'<thead>.*?</thead>', t, flags=re.S)
    if not head:
        return t
    labels = [strip_tags(h) for h in re.findall(r'<th\b[^>]*>(.*?)</th>', head[0], flags=re.S)]
    if len(labels) < 4:
        return t

    def row(r):
        i = iter(labels)
        return re.sub(r'<(td|th)(?=[\s>])', lambda c: f'<{c[1]} data-label="{html_attr(next(i, ""))}"', r[0])

    body = re.sub(r'<tr\b.*?</tr>', row, t[head.end():], flags=re.S)
    return '<table class="t-stack">' + t[len('<table>'):head.end()] + body


def html_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


MATH_RE = re.compile(r'\\\[(.+?)\\\]|\\\((.+?)\\\)', re.S)


def render_math(bodies):
    """\\( … \\) va \\[ … \\] dagi LaTeX ni yig‘ish vaqtida MathML ga aylantiradi (Temml, scripts/tex.cjs)."""
    jobs = [(n, m) for n, body in bodies for m in MATH_RE.finditer(body)]
    if not jobs:
        return bodies
    req = [{'tex': tex_unescape(m[1] if m[1] is not None else m[2]).strip(), 'display': m[1] is not None} for _, m in jobs]
    r = subprocess.run(['node', str(TEX)], input=json.dumps(req), capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        raise SystemExit('LaTeX: scripts/tex.cjs ishlamadi (npm install qiling): ' + r.stderr.strip()[:300])
    res = json.loads(r.stdout)
    bad = [f'  Bob {n}: {q["tex"][:70]!r} → {o["error"][:120]}' for (n, _), q, o in zip(jobs, req, res) if 'error' in o]
    if bad:
        raise SystemExit('LaTeX xatolari:\n' + '\n'.join(bad))
    it = iter(res)
    out = []
    for n, body in bodies:
        out.append((n, MATH_RE.sub(lambda m: next(it)['html'], body)))
    return out


def load_course(count):
    c = json.loads(COURSE_FILE.read_text(encoding='utf-8'))
    listed = [i for p in c['parts'] for i in p['chapters']]
    if sorted(listed) != list(range(1, count + 1)):
        raise SystemExit(f'content/course.json: parts[].chapters 1…{count} ni bir martadan sanashi kerak, hozir {listed}')
    return c


def chapter_numbers():
    nums = sorted(int(m[1]) for f in CONTENT.glob('chapter-*.html') if (m := re.fullmatch(r'chapter-(\d+)\.html', f.name)))
    if not nums or nums != list(range(1, len(nums) + 1)):
        raise SystemExit(f'Boblar 1 dan uzluksiz raqamlanishi kerak (chapter-01 … chapter-NN). Topildi: {nums}')
    return nums


def load_chapters():
    chapters, bodies, report = [], [], []
    for n in ([args.check] if args.check else chapter_numbers()):
        hp = CONTENT / f'chapter-{n:02}.html'
        jp = hp.with_suffix('.json')
        if not jp.exists():
            raise SystemExit(f'Chapter {n}: {jp.name} yo‘q')
        body, c = hp.read_text(encoding='utf-8'), json.loads(jp.read_text(encoding='utf-8'))
        parser = Inspector()
        parser.feed(body)
        errors = parser.bad[:]
        if parser.stack:
            errors.append('Unclosed tags: ' + ','.join(parser.stack))
        if len(parser.ids) != len(set(parser.ids)):
            errors.append('Duplicate IDs')
        if any(not str(i).startswith(f'c{n}-') for i in parser.sections):
            errors.append('Wrong section IDs')
        if set(parser.sections) != set(s['id'] for s in c['sections']):
            errors.append('Section/metadata mismatch')
        if re.search(r'[Ѐ-ӿ]', body + json.dumps(c, ensure_ascii=False)):
            errors.append('Cyrillic text')
        for kind, key, answered in [('review', 'sourceReviewCount', 'reviewAnswered'),
                                    ('application', 'sourceApplicationCount', 'applicationsAnswered'),
                                    ('quick', 'sourceQuickQuizCount', 'quickQuizAnswered')]:
            qs = [q for k, q in parser.questions if k == kind]
            if len(qs) != c[key]:
                errors.append(f'{kind} expected {c[key]}, actual {len(qs)}')
            if len(qs) != len(set(qs)):
                errors.append(f'Duplicate {kind} numbers')
            c[answered] = len(qs)
        if errors and not args.check:
            raise SystemExit(f'Chapter {n}: ' + ', '.join(errors))
        for msg in check_standard(n, body, c):
            if args.lenient and not args.check:
                print(f'  ! Bob {n} (RULE.md): {msg}')
            else:
                errors.append(msg)
        if errors and args.check:
            raise SystemExit(f'Bob {n}: {len(errors)} ta muammo\n  - ' + '\n  - '.join(errors))
        if errors:
            raise SystemExit(f'Chapter {n} RULE.md andozasiga mos emas:\n  - ' + '\n  - '.join(errors)
                             + '\n  (vaqtincha o‘tkazib yuborish: --lenient)')
        c['id'] = n
        c['wordCount'] = len(re.findall(r'\S+', ' '.join(parser.text)))
        c['diagramCount'] = parser.diagrams
        c['interactiveTypes'] = parser.interactive
        c['totalAnswered'] = len(parser.questions)

        def question_anchor(m):
            tag = m[0]
            if re.search(r'\bid="', tag):
                return tag
            kind, num = re.search(r'data-kind="([^"]+)"', tag), re.search(r'data-q="([^"]+)"', tag)
            return tag[:-1] + f' id="c{n}-q-{kind[1]}-{num[1]}">' if kind and num else tag

        body = re.sub(r'<details\b[^>]*class="answer"[^>]*>', question_anchor, body)
        body = re.sub(r'<div\b[^>]*data-interactive="[^"]+"[^>]*>',
                      lambda m: m[0] if re.search(r'\bid="', m[0]) else m[0][:-1] + f' id="c{n}-model">', body)

        def wide_figure(m):
            vb = re.search(r'viewBox="([^"]+)"', m[0])
            if vb and float(vb[1].split()[2]) > 800:
                return m[0].replace('class="diagram"', 'class="diagram diagram-wide"', 1)
            return m[0]

        body = re.sub(r'<figure\b.*?</figure>', wide_figure, body, flags=re.S)
        body = re.sub(r'<table>.*?</table>', label_table, body, flags=re.S)
        body = re.sub(r'href="#(c' + str(n) + r'-[^"\s]+)"', lambda m: 'href="#bob-' + str(n) + '/' + m[1] + '"', body)
        chapters.append(c)
        bodies.append((n, body))
        report.append({'chapter': n, 'words': c['wordCount'], 'sections': len(c['sections']), 'diagrams': parser.diagrams,
                       'interactive': parser.interactive, 'answers': len(parser.questions), 'warnings': c.get('warnings', [])})
    return chapters, bodies, report


def build_search_rows(bodies):
    rows = []
    for n, body in bodies:
        tree = Tree()
        tree.feed(body)
        for section in tree.root.children:
            if not isinstance(section, Node) or section.tag != 'section':
                continue
            h = section.first('h2')
            rows.append({'c': n, 'i': section.attrs['id'], 't': h.text() if h else '', 'x': section.text(True)})
            for q in section.walk():
                if q.tag == 'details' and 'answer' in q.attrs.get('class', '').split():
                    h = q.first('summary')
                    rows.append({'c': n, 'i': q.attrs['id'], 't': h.text() if h else '', 'x': q.text(), 'q': True})
    return rows


# --------------------------------------------------------------------------- aktivlar (CSS/JS)
def esbuild(code, loader, minify_args):
    if not ESBUILD.exists():
        return code
    try:
        r = subprocess.run([str(ESBUILD), f'--loader={loader}', *minify_args], input=code, capture_output=True, text=True, encoding='utf-8')
    except OSError as e:
        print('  ! esbuild ishga tushmadi (minify o‘tkazib yuborildi):', e)
        return code
    if r.returncode != 0:
        print('  ! esbuild:', r.stderr.strip()[:300])
        return code
    return r.stdout


def js_ok(path):
    r = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True, encoding='utf-8')
    return r.returncode == 0, r.stderr.strip()


def collect_js(*dirs):
    parts = []
    for d in dirs:
        for f in sorted((SRC / 'js' / d).glob('*.js')):
            ok, err = js_ok(f)
            if not ok:
                msg = f'{f.relative_to(ROOT)}: {err.splitlines()[0] if err else "sintaksis xatosi"}'
                if args.lenient:
                    print('  ! o‘tkazib yuborildi —', msg)
                    continue
                raise SystemExit('JS sintaksis xatosi → ' + msg)
            parts.append(f'/* ---- {f.relative_to(SRC)} ---- */\n' + f.read_text(encoding='utf-8'))
    return '\n'.join(parts)


def vendor_js():
    if not GSAP_DIR.exists():
        raise SystemExit('GSAP topilmadi. Avval:  npm install')
    return '\n;'.join((GSAP_DIR / f'{n}.min.js').read_text(encoding='utf-8') for n in GSAP_FILES) + '\n'


def assemble(template):
    """<!--@include partials/x.html--> yo‘riqnomalarini fayl mazmuni bilan almashtiradi."""
    return re.sub(r'<!--@include ([^ ]+?)-->', lambda m: (SRC / m[1].strip()).read_text(encoding='utf-8').strip(), template)


def status():
    rows = []
    for n in chapter_numbers():
        r = subprocess.run([sys.executable, str(Path(__file__)), '--check', str(n)], capture_output=True, text=True, encoding='utf-8')
        first = (r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else '?'
        rows.append((n, r.returncode == 0, first))
    for n, ok, first in rows:
        print(f'  {n:>2}-bob  {"✓ tayyor" if ok else "✗ " + first.split(": ", 1)[-1]}')
    done = sum(ok for _, ok, _ in rows)
    print(f'Tayyor: {done}/{len(rows)}.  Tugallanmagan: {", ".join(str(n) for n, ok, _ in rows if not ok) or "yo‘q"}')


def main():
    if args.status:
        return status()
    if args.clean and OUT.exists():
        shutil.rmtree(OUT)
    chapters, bodies, report = load_chapters()
    bodies = render_math(bodies)
    if args.check:
        print(f'Bob {args.check}: RULE.md bo‘yicha xato yo‘q ✓ ({chapters[0]["wordCount"]} so‘z, '
              f'{chapters[0]["diagramCount"]} chizma, {chapters[0]["totalAnswered"]} javob)')
        return
    course = load_course(len(chapters))
    search_rows = build_search_rows(bodies)
    search_data = compact(search_rows)

    css_raw = '\n'.join(f.read_text(encoding='utf-8') for f in sorted((SRC / 'css').glob('*.css')))
    css = esbuild(css_raw, 'css', ['--minify'])
    app_js = esbuild(collect_js('motion', 'app'), 'js', ['--minify-whitespace', '--minify-syntax'])
    models_js = esbuild((SRC / 'js' / 'simulations.js').read_text(encoding='utf-8'), 'js', ['--minify-whitespace', '--minify-syntax'])
    ok, err = js_ok(SRC / 'js' / 'simulations.js')
    if not ok:
        if args.lenient:
            print('  ! simulations.js o‘tkazib yuborildi —', err.splitlines()[0] if err else '')
            models_js = ''
        else:
            raise SystemExit('JS sintaksis xatosi → src/js/simulations.js: ' + err.splitlines()[0])
    vendor = vendor_js()

    assets = {
        'css': f'/assets/app.{digest(css)}.css',
        'app': f'/assets/app.{digest(app_js)}.js',
        'vendor': f'/assets/vendor.{digest(vendor)}.js',
        'models': f'/assets/models.{digest(models_js)}.js',
        'search': f'/assets/search.{digest(search_data)}.json',
    }
    runtime = []
    for c, (n, body) in zip(chapters, bodies):
        r = {k: c[k] for k in ('id', 'title', 'englishTitle', 'lead', 'sourcePages', 'diagramCount', 'interactiveTypes', 'totalAnswered')}
        r['sections'] = [{'id': s['id'], 'title': s['title']} for s in c['sections']]
        r['contentUrl'] = f'/chapters/chapter-{n:02}.{digest(body)}.html'
        runtime.append(r)

    template = assemble((SRC / 'index.html').read_text(encoding='utf-8')).replace('<!--@count-->', str(len(chapters))).replace('<!--@count2-->', f'{len(chapters):02}')
    templates = '\n'.join(f'<template id="template-{n}">\n{body}\n</template>' for n, body in bodies)

    def data_js(online):
        return ('const CHAPTERS=' + compact(runtime).replace('</', '<\\/') + ';const COURSE=' + compact(course).replace('</', '<\\/')
                + ';const COURSE_ONLINE=' + ('true' if online else 'false')
                + ';const SEARCH_INDEX_URL=' + compact(assets['search'] if online else None)
                + ';const SIM_SCRIPT_URL=' + compact(assets['models'] if online else None) + ';')

    def render(online):
        if online:
            styles = f'<link rel="stylesheet" href="{assets["css"]}">'
            scripts = (f'<script>{data_js(True)}</script>\n<script defer src="{assets["vendor"]}"></script>\n'
                       f'<script defer src="{assets["app"]}"></script>')
            tpl = ''
        else:
            styles = f'<style>{css}</style>'
            scripts = f'<script>{data_js(False)}</script>\n<script>{vendor}</script>\n<script>{app_js}</script>\n<script>{models_js}</script>'
            tpl = templates
        return template.replace('<!--@styles-->', styles).replace('<!--@templates-->', tpl).replace('<!--@scripts-->', scripts)

    online_html, offline_html = render(True), render(False)

    # --- yozish (eski hash’langan fayllar saqlanadi: oldingi keshlangan sahifalar ishlashda qoladi)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'index.html').write_text(online_html, encoding='utf-8')
    files = [(assets['css'], css), (assets['app'], app_js), (assets['vendor'], vendor), (assets['models'], models_js), (assets['search'], search_data)]
    files += [(c['contentUrl'], body) for c, (n, body) in zip(runtime, bodies)]
    for url, data in files:
        f = OUT / url.lstrip('/')
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(data, encoding='utf-8')
    if not args.no_offline:
        out = ROOT / 'outputs' / f'iqtisodiyot-{len(chapters)}-bob.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(offline_html, encoding='utf-8')

    gz = lambda s: len(gzip.compress(s.encode()))
    first_load = gz(online_html) + gz(css) + gz(vendor) + gz(app_js)
    info = {
        'chapters': len(chapters), 'words': sum(c['wordCount'] for c in chapters), 'diagrams': sum(c['diagramCount'] for c in chapters),
        'interactive': sum(len(c['interactiveTypes']) for c in chapters), 'answers': sum(r['answers'] for r in report),
        'offlineBytes': len(offline_html.encode()), 'onlineHtmlBytes': len(online_html.encode()),
        'gzip': {'html': gz(online_html), 'css': gz(css), 'vendorGsap': gz(vendor), 'app': gz(app_js), 'firstLoadTotal': first_load,
                 'models': gz(models_js), 'search': gz(search_data)},
        'searchRows': len(search_rows),
    }
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build' / 'coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'build' / 'build-info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(info, ensure_ascii=False))
    print(f'Birinchi yuklash (gzip): {first_load / 1024:.1f} KB  →  {OUT}')


main()
