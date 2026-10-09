#!/bin/bash
# Використання: bash testchapter.sh chapters/ch01.tex
CH="$1"
BASE=$(basename "$CH" .tex)
mkdir -p build
cat > "_test_$BASE.tex" <<HDR
\documentclass[10pt,a5paper,twoside,openright]{book}
\input{preamble.tex}
\begin{document}
\input{$CH}
\end{document}
HDR
xelatex -interaction=nonstopmode -output-directory=build "_test_$BASE.tex" > /dev/null 2>&1
xelatex -interaction=nonstopmode -output-directory=build "_test_$BASE.tex" 2>&1 | grep -E "^!|Missing character|Undefined control|LaTeX Error|Output written" | head -40
rm -f "_test_$BASE.tex"
