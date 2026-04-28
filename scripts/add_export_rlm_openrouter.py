#!/usr/bin/env python3
import json
import shutil
from datetime import datetime
from pathlib import Path
import re

nb_path = Path('rlm_lisette_v2.ipynb')
if not nb_path.exists():
    print(f"Notebook not found: {nb_path}")
    raise SystemExit(1)

with nb_path.open('r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
modified = 0
pattern_class_rlm = re.compile(r'^\s*class\s+RLM\b', re.MULTILINE)
pattern_openrouter = re.compile(r'openrouter', re.IGNORECASE)
for i, cell in enumerate(cells):
    if cell.get('cell_type') != 'code':
        continue
    src = cell.get('source', '')
    if isinstance(src, list):
        src_text = ''.join(src)
    else:
        src_text = src
    # skip if already has export marker at first non-empty line
    lines = src_text.splitlines()
    first_nonempty = None
    for ln in lines:
        if ln.strip() == '':
            continue
        first_nonempty = ln.strip()
        break
    if first_nonempty and first_nonempty.startswith('#| export'):
        continue
    # match RLM class or openrouter anywhere in the cell
    if pattern_class_rlm.search(src_text) or pattern_openrouter.search(src_text):
        # insert marker
        if isinstance(src, list):
            cell['source'] = ['#| export\n'] + src
        else:
            cell['source'] = '#| export\n' + src_text
        modified += 1

if modified == 0:
    print('No matching cells modified.')
else:
    bak = nb_path.with_suffix('.ipynb.bak.' + datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'))
    shutil.copy2(nb_path, bak)
    with nb_path.open('w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f'Modified {modified} code cells; backup written to {bak}')
