# -*- coding: utf-8 -*-
import typst
import glob
import os

PREAMBLE = """
#set text(font: ("SimSun", "Times New Roman"), size: 12pt, lang: "zh")
#let hei-font = ("SimHei", "SimSun")
#let song-font = ("SimSun", "Times New Roman")
"""

sections = sorted(glob.glob('paper/sections/*.typ')) + ['paper/references.typ']

for sec in sections:
    rel_path = os.path.relpath(sec, 'paper').replace('\\', '/')
    temp_file = 'paper/_test_sec.typ'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(PREAMBLE + f'\n#include("{rel_path}")\n')
    try:
        typst.compile(temp_file, output='paper/_test_sec.pdf', root='.')
        print(f"OK: {sec}")
    except Exception as e:
        print(f"ERROR in {sec}: {e}")

if os.path.exists('paper/_test_sec.typ'):
    os.remove('paper/_test_sec.typ')
if os.path.exists('paper/_test_sec.pdf'):
    os.remove('paper/_test_sec.pdf')
