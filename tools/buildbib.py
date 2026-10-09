# -*- coding: utf-8 -*-
"""Формування загального списку джерел.

1. Збирає \\bibitem із bib-core.tex та chapters/chNN-sources.tex.
2. Виявляє дублікати (однаковий DOI або URL) і зводить їх до одного ключа,
   переписуючи \\cite у файлах розділів (резервні копії -- у build/bak).
3. Залишає лише процитовані джерела.
4. Упорядковує: спершу кириличні описи (за українським алфавітом),
   далі латиничні (за латинським алфавітом).
5. Записує back/bib-generated.tex.
"""
import io, os, re, glob, shutil, sys
from urllib.parse import unquote

BOOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from texio import read_tex, write_tex

def read(p):
    return read_tex(p)[0]

def write(p, t, like=None):
    """Запис зі збереженням кінців рядків і BOM файлу-зразка (або самого p)."""
    src = like or p
    if os.path.exists(src):
        _, eol, bom = read_tex(src)
    else:
        eol, bom = '\r\n', False
    write_tex(p, t, eol, bom)

# ---------- 1. Збирання записів ----------
item_re = re.compile(r'\\bibitem\{([^}]*)\}(.*?)(?=\\bibitem\{|\Z)', re.S)

def strip_comments(t):
    return re.sub(r'(?m)(?<!\\)%.*$', '', t)

entries = []          # (key, body, source_file)
files = [os.path.join(BOOK, 'bib-core.tex')] + \
        sorted(glob.glob(os.path.join(BOOK, 'chapters', 'ch[0-9][0-9]-sources.tex')))
for p in files:
    t = strip_comments(read(p))
    for m in item_re.finditer(t):
        body = re.sub(r'\s+', ' ', m.group(2)).strip()
        entries.append((m.group(1).strip(), body, os.path.basename(p)))

# ---------- 2. Сигнатури та дублікати ----------
def signature(body):
    m = re.search(r'DOI:?\s*(10\.\d{4,9}/[^\s,;]+)', body, re.I)
    if m:
        return 'doi:' + m.group(1).rstrip('.').lower()
    m = re.search(r'\\url\{([^}]*)\}', body)
    if m:
        u = unquote(m.group(1)).lower().strip()
        u = re.sub(r'^https?://(www\.)?', '', u).rstrip('/.')
        return 'url:' + u
    t = re.sub(r'\\[a-zA-Z]+|[{}~]', ' ', body).lower()
    return 'txt:' + re.sub(r'\W+', '', t)[:90]

# використані ключі
chapter_files = sorted(glob.glob(os.path.join(BOOK, 'chapters', 'ch[0-9][0-9].tex')))
cite_re = re.compile(r'\\cite\{([^}]*)\}')
used = set()
for p in chapter_files + [os.path.join(BOOK, 'front', 'vstup.tex'),
                          os.path.join(BOOK, 'back', 'dodatky.tex')]:
    if os.path.exists(p):
        for g in cite_re.findall(read(p)):
            used.update(k.strip() for k in g.split(',') if k.strip())

by_sig = {}
for key, body, src in entries:
    by_sig.setdefault(signature(body), []).append((key, body, src))

alias = {}      # дубльований ключ -> канонічний
canon = {}      # канонічний ключ -> опис
for sig, group in by_sig.items():
    # канонічним стає ключ ядра (без двокрапки), інакше перший за порядком
    group.sort(key=lambda e: (':' in e[0], e[2]))
    ck, cb, _ = group[0]
    # серед дублікатів беремо найповніший опис
    cb = max((e[1] for e in group), key=len)
    canon[ck] = cb
    for k, _, _ in group[1:]:
        if k != ck:
            alias[k] = ck

# дублікати, які не розпізнаються автоматично (різні URL одного документа)
MANUAL_ALIAS = {}
for k, v in MANUAL_ALIAS.items():
    alias[k] = v
    canon.pop(k, None)

# ключі з однаковим ім'ям, але різним змістом
seen = {}
for key, body, src in entries:
    if key in seen and signature(seen[key]) != signature(body):
        print('УВАГА: ключ %s визначено двічі з різним змістом' % key)
    seen[key] = body

# ---------- 3. Переписування \cite ----------
if alias:
    bak = os.path.join(BOOK, 'build', 'bak')
    os.makedirs(bak, exist_ok=True)
    for p in chapter_files:
        t = read(p)
        def repl(m):
            ks = [k.strip() for k in m.group(1).split(',')]
            out = []
            for k in ks:
                k = alias.get(k, k)
                if k not in out:
                    out.append(k)
            return '\\cite{' + ','.join(out) + '}'
        nt = cite_re.sub(repl, t)
        if nt != t:
            dst = os.path.join(bak, os.path.basename(p))
            if not os.path.exists(dst):
                shutil.copy2(p, dst)
            write(p, nt)

used_c = set(alias.get(k, k) for k in used)
missing = sorted(k for k in used_c if k not in canon)
unused = sorted(k for k in canon if k not in used_c)

# ---------- 4. Сортування ----------
UA = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
UA_RANK = {c: i for i, c in enumerate(UA)}

def plain(body):
    t = re.sub(r'\\url\{[^}]*\}', '', body)
    t = re.sub(r'\\(emph|textit|textbf|textsc)\{', '', t)
    t = re.sub(r'\\[a-zA-Z]+\s?', '', t)
    t = t.replace('{', '').replace('}', '').replace('~', ' ')
    t = re.sub(r'^[^\w«"]+', '', t)
    return t.strip().lower()

def sort_key(item):
    k, b = item
    s = plain(b)
    s = s.lstrip('«"\'„ ')
    first = s[:1]
    is_cyr = bool(re.match(r'[\u0400-\u04FF]', first))
    if is_cyr:
        return (0, [UA_RANK.get(c, 100 + ord(c)) if c in UA_RANK or '\u0400' <= c <= '\u04FF'
                    else 50 for c in s[:60]])
    return (1, [ord(c) for c in s[:60]])

items = sorted(((k, canon[k]) for k in canon if k in used_c), key=sort_key)

# ---------- 5. Запис ----------
out = ['% Згенеровано tools/buildbib.py -- не редагувати вручну', '']
for k, b in items:
    out.append('\\bibitem{%s} %s' % (k, b))
    out.append('')
write(os.path.join(BOOK, 'back', 'bib-generated.tex'), '\n'.join(out))

ua = sum(1 for k, b in items if sort_key((k, b))[0] == 0)
print('записів усього: %d; унікальних документів: %d' % (len(entries), len(canon)))
print('зведено дублікатів: %d' % len(alias))
for k in sorted(alias):
    print('   %s -> %s' % (k, alias[k]))
print('у списку (процитовані): %d, з них кириличних: %d, латиничних: %d' % (len(items), ua, len(items) - ua))
print('невизначені ключі: %s' % (', '.join(missing) or 'немає'))
print('непроцитовані (виключено): %s' % (', '.join(unused) or 'немає'))
