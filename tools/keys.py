# -*- coding: utf-8 -*-
"""Аналіз ключів \\cite та \\bibitem у проєкті посібника."""
import re, sys, glob, os, io

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()

cite_re = re.compile(r'\\cite\{([^}]*)\}')
bib_re = re.compile(r'\\bibitem\{([^}]*)\}')

core = set()
if os.path.exists(os.path.join(BOOK, 'bib-core.tex')):
    core = set(bib_re.findall(read(os.path.join(BOOK, 'bib-core.tex'))))

extra = {}
for p in sorted(glob.glob(os.path.join(BOOK, 'chapters', '*-sources.tex'))):
    for k in bib_re.findall(read(p)):
        extra[k] = os.path.basename(p)

defined = core | set(extra)

used = {}
for p in sorted(glob.glob(os.path.join(BOOK, 'chapters', 'ch[0-9][0-9].tex'))):
    name = os.path.basename(p)[:-4]
    txt = read(p)
    ks = set()
    for grp in cite_re.findall(txt):
        for k in grp.split(','):
            k = k.strip()
            if k:
                ks.add(k)
    used[name] = ks

allused = set()
for v in used.values():
    allused |= v

print('bib-core: %d ключів' % len(core))
print('chNN-sources: %d ключів' % len(extra))
print('використано у розділах: %d' % len(allused))
print()
for name in sorted(used):
    own = sorted(k for k in used[name] if k.startswith(name + ':'))
    print('%s: усього %d, власних %d' % (name, len(used[name]), len(own)))
print()
missing = sorted(allused - defined)
print('НЕВИЗНАЧЕНІ КЛЮЧІ (%d):' % len(missing))
cur = None
for k in missing:
    pref = k.split(':')[0] if ':' in k else '(ядро)'
    if pref != cur:
        cur = pref
        print('\n  [%s]' % cur)
    print('   ', k)

unused = sorted(defined - allused)
print('\n\nВИЗНАЧЕНІ, АЛЕ НЕ ВИКОРИСТАНІ (%d): %s' % (len(unused), ', '.join(unused)))
