#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.').resolve()
tools = root / 'tools'
steps = [
    ('Apply canonical', [sys.executable, str(tools / 'apply_canonical.py'), str(root)]),
    ('Build sitemap', [sys.executable, str(tools / 'build_sitemap.py'), str(root)]),
    ('Site sync audit', [sys.executable, str(tools / 'site_sync_audit.py'), str(root)]),
    ('SEO audit', [sys.executable, str(tools / 'seo_audit.py'), str(root)]),
]
failed = []
for label, cmd in steps:
    print(f'== {label} ==')
    result = subprocess.run(cmd)
    if result.returncode != 0:
        failed.append(label)
if failed:
    print('RELEASE AUDIT: CHECK — ' + ', '.join(failed))
    sys.exit(1)
print('RELEASE AUDIT: PASS')
