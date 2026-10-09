# -*- coding: utf-8 -*-
"""Читання/запис .tex зі збереженням кінців рядків (CRLF або LF) і BOM."""
import io

def read_tex(path):
    """Повертає (текст із \\n, eol, bom)."""
    with io.open(path, 'rb') as f:
        raw = f.read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    if bom:
        raw = raw[3:]
    eol = '\r\n' if b'\r\n' in raw else '\n'
    txt = raw.decode('utf-8').replace('\r\n', '\n')
    return txt, eol, bom

def write_tex(path, txt, eol='\n', bom=False):
    data = txt.replace('\r\n', '\n')
    if eol != '\n':
        data = data.replace('\n', eol)
    raw = data.encode('utf-8')
    if bom:
        raw = b'\xef\xbb\xbf' + raw
    with io.open(path, 'wb') as f:
        f.write(raw)
