# -*- coding: utf-8 -*-
"""Перелік Overfull \\hbox з файлом і номером сторінки PDF (приблизно)."""
import io, os, re, sys

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log = io.open(os.path.join(BOOK, 'build', 'main.log'), encoding='utf-8', errors='replace').read()
thr = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0

page = 0
cur_file = '?'
pos = 0
tok = re.compile(r'\[(\d+)|\((\./)?((?:chapters|front|back)/[\w\-]+\.tex)|Overfull \\hbox \(([\d.]+)pt too wide\) (?:in paragraph|in alignment|detected) at lines? (\d+)')
for m in tok.finditer(log):
    if m.group(1):
        page = int(m.group(1))
    elif m.group(3):
        cur_file = m.group(3)
    elif m.group(4):
        w = float(m.group(4))
        if w >= thr:
            print('%6.1fpt  стор.~%d  %s  рядок %s' % (w, page + 1, cur_file, m.group(5)))
