#!/usr/bin/env python3
"""Kitob PDF dan bitta bob matnini sahifa belgilari bilan ajratib olish (RULE.md §2, BOB_QOSHISH.md §3).

    # 1) PDF da qaysi boblar bor va qaysi sahifalarda
    python3 scripts/extract_chapter.py KITOB.pdf --list
    # 2) bob matnini ajratish — sahifalar avtomatik topiladi
    python3 scripts/extract_chapter.py KITOB.pdf --chapter 11
    # (zaxira) qo‘lda: matn qidirish va PDF sahifalarini berish; --offset = kitob sahifasi − PDF sahifasi
    python3 scripts/extract_chapter.py KITOB.pdf --find "Public Goods"
    python3 scripts/extract_chapter.py KITOB.pdf --chapter 11 --pages 231-252 --offset -2

Natija: reference/source-text/chapter-11.txt — har sahifa oldida
"=== KITOB SAHIFASI 229; PDF SAHIFASI 231 ===" qatori.
Kerak: poppler (pdftotext) — bo‘lmasa avtomatik pypdf ishlatiladi (python -m pip install --user pypdf).
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('pdf')
ap.add_argument('--list', action='store_true', help='PDF dagi barcha boblar: raqam, nom, sahifalar')
ap.add_argument('--find', help='shu matn uchraydigan PDF sahifalarini chiqarish')
ap.add_argument('--chapter', type=int)
ap.add_argument('--pages', help='PDF sahifalari, masalan 231-252 (berilmasa — avtomatik topiladi)')
ap.add_argument('--offset', type=int, help='kitob sahifasi = PDF sahifasi + offset (berilmasa — sarlavhalardan)')
args = ap.parse_args()

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass

POPPLER = bool(shutil.which('pdftotext'))
if not POPPLER:
    try:
        import logging
        logging.disable(logging.WARNING)  # pypdf shrift ogohlantirishlari matnga ta’sir qilmaydi
        from pypdf import PdfReader
    except ImportError:
        sys.exit('pdftotext ham, pypdf ham topilmadi. O‘rnating:  python -m pip install --user pypdf')


def load_pages():
    """Barcha sahifalar matni (layout saqlangan): pages[0] — 1-sahifa."""
    if POPPLER:
        r = subprocess.run(['pdftotext', '-layout', args.pdf, '-'], capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        pages = r.stdout.split('\f')
        return pages[:-1] if pages and not pages[-1].strip() else pages
    out = []
    for page in PdfReader(args.pdf).pages:
        try:
            out.append(page.extract_text(extraction_mode='layout') or '')
        except TypeError:  # eski pypdf
            out.append(page.extract_text() or '')
    return out


PAGES = load_pages()


def lines(n):
    return [l.strip() for l in PAGES[n - 1].splitlines() if l.strip()]


def opener(n):
    """Bob boshlanish sahifasi: birinchi qatorda yolg‘iz «Chapter», keyin yolg‘iz raqam (Mankiw dizayni).
    pypdf raqamni yo‘qotishi mumkin — unda raqam keyingi toq sahifa sarlavhasidan («Chapter 2 … 19») olinadi."""
    ls = lines(n)
    if not ls or not re.fullmatch(r'chapter(\s+\d+)?', ls[0].lower()):
        return None
    if m := re.fullmatch(r'chapter\s+(\d+)', ls[0].lower()):
        return int(m[1])
    if len(ls) > 1 and ls[1].isdigit():
        return int(ls[1])
    for k in range(n + 1, min(n + 3, len(PAGES)) + 1):
        for l in lines(k)[:2]:
            if m := re.match(r'Chapter\s+(\d+)\b', l):
                return int(m[1])
    return None


def book_page(n):
    """Sahifa sarlavhasidagi kitob sahifa raqami: juft «18  Part I …», toq «Chapter 2 … 19»."""
    for l in lines(n)[:2]:
        if m := re.match(r'(\d+)\s{2,}Part\b', l):
            return int(m[1])
        if m := re.match(r'Chapter\s+\d+\b.*?\s{2,}(\d+)$', l):
            return int(m[1])
    return None


def chapter_title(start, end):
    for n in range(start + 1, min(end, start + 4) + 1):
        for l in lines(n)[:2]:
            if m := re.match(r'Chapter\s+\d+\s+(.+?)\s{2,}\d+$', l):
                return m[1]
    return ''


def chapter_part(start, end):
    """Bob qaysi qismda: juft sahifa sarlavhasi «18  Part I  Introduction» → «Part I Introduction»."""
    for n in range(start + 1, end + 1):
        for l in lines(n)[:1]:
            if m := re.match(r'\d+\s{2,}(Part\s+[IVXLC]+)\s+(.+)$', l):
                return f'{m[1]} {re.sub(r"\s+", " ", m[2])}'
    return ''


def chapters():
    """{bob: (boshi, oxiri, offset, nomi, qismi)} — PDF sahifalari bo‘yicha."""
    starts = sorted((n, c) for n in range(1, len(PAGES) + 1) if (c := opener(n)) is not None)
    found = {}
    for i, (start, ch) in enumerate(starts):
        end = starts[i + 1][0] - 1 if i + 1 < len(starts) else len(PAGES)
        while end > start and len(' '.join(lines(end)).split()) < 40:  # bo‘sh / qism sarlavhasi sahifalari
            end -= 1
        offs = [b - n for n in range(start, end + 1) if (b := book_page(n)) is not None]
        offset = max(set(offs), key=offs.count) if offs else 0
        found[ch] = (start, end, offset, chapter_title(start, end), chapter_part(start, end))
    return found


if args.list:
    found = chapters()
    if not found:
        sys.exit('Bob boshlanish sahifalari topilmadi (boshqa dizayndagi PDF?). --find bilan qo‘lda toping.')
    for ch, (a, b, off, title, part) in sorted(found.items()):
        print(f'Bob {ch:>2}: PDF {a}-{b} (kitob {a + off}-{b + off}, offset {off:+d})  {title}  [{part}]')
    sys.exit(0)

if args.find:
    needle = re.sub(r'\s+', ' ', args.find.lower())
    for n in range(1, len(PAGES) + 1):
        if needle in re.sub(r'\s+', ' ', PAGES[n - 1].lower()):
            print(f'PDF sahifa {n} (kitob ≈ {n + (args.offset or 0)})')
    sys.exit(0)

if not args.chapter:
    sys.exit('--chapter N kerak (yoki --list / --find)')
if args.pages:
    a, b = (int(x) for x in args.pages.split('-'))
    offset = args.offset or 0
else:
    found = chapters()
    if args.chapter not in found:
        have = ', '.join(map(str, sorted(found))) or 'hech biri'
        sys.exit(f'{args.chapter}-bob bu PDF da topilmadi (bor boblar: {have}). Bob bor PDF kerak '
                 f'yoki --find "…" bilan topib, --pages A-B bering.')
    a, b, offset, title, part = found[args.chapter]
    offset = args.offset if args.offset is not None else offset
    print(f'{args.chapter}-bob «{title}» [{part}]: PDF {a}-{b}, kitob {a + offset}-{b + offset}')
out = ROOT / 'reference' / 'source-text' / f'chapter-{args.chapter:02}.txt'
out.parent.mkdir(parents=True, exist_ok=True)
parts = [f'=== KITOB SAHIFASI {n + offset}; PDF SAHIFASI {n} ===\n{PAGES[n - 1].rstrip()}\n' for n in range(a, b + 1)]
out.write_text('\n'.join(parts), encoding='utf-8')
print(f'{out.relative_to(ROOT)}: {b - a + 1} sahifa, {sum(len(p.split()) for p in parts)} so‘z')
