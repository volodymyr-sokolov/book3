# -*- coding: utf-8 -*-
"""Пошук імовірних дублікатів у згенерованому списку (за суфіксом ключа та назвою)."""
import io, os, re, collections

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = io.open(os.path.join(BOOK, 'back', 'bib-generated.tex'), encoding='utf-8').read()
items = re.findall(r'\\bibitem\{([^}]*)\} (.*)', t)

by_suffix = collections.defaultdict(list)
for k, b in items:
    by_suffix[re.sub(r'[-_]', '', k.split(':')[-1])].append((k, b))
for s, v in sorted(by_suffix.items()):
    if len(v) > 1:
        print('--- суфікс', s)
        for k, b in v:
            print('   %s | %s' % (k, b[:120]))

# схожі назви: перші 45 символів без розмітки
def norm(b):
    b = re.sub(r'\\url\{[^}]*\}', '', b)
    b = re.sub(r'\\[a-zA-Z]+|[{}~]', '', b)
    return re.sub(r'\W+', '', b.lower())[:45]
by_title = collections.defaultdict(list)
for k, b in items:
    by_title[norm(b)].append((k, b))
for s, v in by_title.items():
    if len(v) > 1:
        print('--- схожий початок опису')
        for k, b in v:
            print('   %s | %s' % (k, b[:160]))

# документи з однаковими номерами RFC / SP / законів
by_num = collections.defaultdict(list)
for k, b in items:
    for m in re.findall(r'(RFC \d{3,4}|SP 800-\d+[A-Z]?(?:[ -]?(?:Rev\.|r)\s?\d)?|№ ?\d{2,4}-[IVX]+|№ ?\d{2,4}(?= від)|FIPS \d{3})', b):
        by_num[m.replace(' ', '')].append(k)
for n, ks in sorted(by_num.items()):
    if len(set(ks)) > 1:
        print('--- номер %s: %s' % (n, ', '.join(sorted(set(ks)))))
