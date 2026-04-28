#!/usr/bin/env python3
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

nb_path = Path('rlm_lisette_v2.ipynb')
if not nb_path.exists():
    print(f"Notebook not found: {nb_path}")
    raise SystemExit(1)

with nb_path.open('r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb.get('cells', [])
modified = 0
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
    # detect def/class definitions anywhere in the cell (top-level or nested)
    if re.search(r'^\s*(def|class)\s+', src_text, re.MULTILINE):
        # insert marker
        if isinstance(src, list):
            # ensure marker plus a newline
            cell['source'] = ['#| export\n'] + src
        else:
            cell['source'] = '#| export\n' + src_text
        modified += 1

if modified == 0:
    print('No cells modified.')
else:
    # backup
    bak = nb_path.with_suffix('.ipynb.bak.' + datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'))
    shutil.copy2(nb_path, bak)
    with nb_path.open('w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f'Modified {modified} code cells; backup written to {bak}')
