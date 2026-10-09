# -*- coding: utf-8 -*-
"""Статистика кінців рядків у .tex-файлах."""
import glob, io, os, sys
BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pats = sys.argv[1:] or ['chapters/*.tex', 'front/*.tex', 'back/*.tex', '*.tex']
for pat in pats:
    for p in sorted(glob.glob(os.path.join(BOOK, pat))):
        raw = io.open(p, 'rb').read()
        crlf = raw.count(b'\r\n')
        lf = raw.count(b'\n') - crlf
        print('%-32s CRLF=%5d  LF=%5d%s' % (os.path.relpath(p, BOOK), crlf, lf, '  <-- змішані' if crlf and lf else ''))
