#!/usr/bin/env python3
"""Kitob PDF dan bitta bob matnini sahifa belgilari bilan ajratib olish (RULE.md §2).

    # 1) bob qaysi PDF sahifalarida ekanini topish
    python3 scripts/extract_chapter.py KITOB.pdf --find "Chapter 11"
    # 2) matnni ajratish (PDF sahifalari bo‘yicha); --offset = kitob sahifasi − PDF sahifasi
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
ap.add_argument('--find', help='shu matn uchraydigan PDF sahifalarini chiqarish')
ap.add_argument('--chapter', type=int)
ap.add_argument('--pages', help='PDF sahifalari, masalan 231-252')
ap.add_argument('--offset', type=int, default=0, help='kitob sahifasi = PDF sahifasi + offset')
args = ap.parse_args()

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass

POPPLER = bool(shutil.which('pdftotext') and shutil.which('pdfinfo'))
if not POPPLER:
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit('pdftotext ham, pypdf ham topilmadi. O‘rnating:  python -m pip install --user pypdf')
    READER = PdfReader(args.pdf)


def page_text(n):
    if POPPLER:
        r = subprocess.run(['pdftotext', '-layout', '-f', str(n), '-l', str(n), args.pdf, '-'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        return r.stdout
    page = READER.pages[n - 1]
    try:
        return page.extract_text(extraction_mode='layout') or ''
    except TypeError:  # eski pypdf
        return page.extract_text() or ''


def page_count():
    if not POPPLER:
        return len(READER.pages)
    r = subprocess.run(['pdfinfo', args.pdf], capture_output=True, text=True, encoding='utf-8', errors='replace')
    m = re.search(r'Pages:\s+(\d+)', r.stdout)
    return int(m[1]) if m else 0


if args.find:
    needle = re.sub(r'\s+', ' ', args.find.lower())
    for n in range(1, page_count() + 1):
        if needle in re.sub(r'\s+', ' ', page_text(n).lower()):
            print(f'PDF sahifa {n} (kitob ≈ {n + args.offset})')
    sys.exit(0)

if not (args.chapter and args.pages):
    sys.exit('--chapter va --pages kerak (yoki --find)')
a, b = (int(x) for x in args.pages.split('-'))
out = ROOT / 'reference' / 'source-text' / f'chapter-{args.chapter:02}.txt'
out.parent.mkdir(parents=True, exist_ok=True)
parts = [f'=== KITOB SAHIFASI {n + args.offset}; PDF SAHIFASI {n} ===\n{page_text(n).rstrip()}\n' for n in range(a, b + 1)]
out.write_text('\n'.join(parts), encoding='utf-8')
print(f'{out.relative_to(ROOT)}: {b - a + 1} sahifa, {sum(len(p.split()) for p in parts)} so‘z')
