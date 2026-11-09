#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.').resolve()
config = json.loads((root / 'site-config.json').read_text(encoding='utf-8'))
BASE_URL = config['base_url'].rstrip('/') + '/'

def is_content_html(p):
    name = p.name.lower()
    if name == '404.html':
        return False
    if re.fullmatch(r'google[a-z0-9_-]+\.html', name):
        return False
    return True

html_files = [p for p in sorted(root.glob('*.html')) if is_content_html(p)]
changed = 0
for p in html_files:
    href = BASE_URL if p.name == 'index.html' else BASE_URL + p.name
    text = p.read_text(encoding='utf-8', errors='strict')
    new_tag = f'<link rel="canonical" href="{href}"/>'
    # Remove all existing canonical tags, then reinsert one normalized tag.
    cleaned = re.sub(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>\s*', '', text, flags=re.I)
    if '</head>' not in cleaned.lower():
        raise RuntimeError(f'No </head> in {p.name}')
    updated = re.sub(r'</head>', new_tag + '</head>', cleaned, count=1, flags=re.I)
    if updated != text:
        p.write_text(updated, encoding='utf-8')
        changed += 1
print(f'canonical synchronized: {len(html_files)} content HTML, {changed} changed')
