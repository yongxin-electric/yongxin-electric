#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import json
import re
import sys
import xml.etree.ElementTree as ET

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

html_files = sorted(p.name for p in root.glob('*.html') if is_content_html(p))
core_order = [
    'index.html', 'about.html', 'products.html', 'brands.html', 'services.html',
    'case-studies.html', 'technical.html', 'contact.html'
]
rank = {name: i for i, name in enumerate(core_order)}
html_files.sort(key=lambda n: (rank.get(n, len(core_order)), n))

ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
urlset = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
for name in html_files:
    url = ET.SubElement(urlset, '{http://www.sitemaps.org/schemas/sitemap/0.9}url')
    loc = ET.SubElement(url, '{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    loc.text = BASE_URL if name == 'index.html' else BASE_URL + quote(name)

tree = ET.ElementTree(urlset)
ET.indent(tree, space='  ')
sitemap = root / 'sitemap.xml'
tree.write(sitemap, encoding='utf-8', xml_declaration=True)

robots = root / 'robots.txt'
robots.write_text(
    'User-agent: *\nAllow: /\n\n' + f'Sitemap: {BASE_URL}sitemap.xml\n',
    encoding='utf-8'
)
print(f'{sitemap} ({len(html_files)} URLs)')
print(f'{robots}')
