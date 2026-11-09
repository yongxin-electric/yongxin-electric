#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter, defaultdict
from urllib.parse import unquote, urlparse
import json
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.').resolve()
config = json.loads((root / 'site-config.json').read_text(encoding='utf-8'))
BASE_URL = config['base_url'].rstrip('/') + '/'

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title_parts = []
        self.meta_description = None
        self.h1_count = 0
        self.canonicals = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        d = {k.lower(): (v or '') for k, v in attrs}
        tag = tag.lower()
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta' and d.get('name', '').lower() == 'description':
            self.meta_description = d.get('content', '').strip()
        elif tag == 'h1':
            self.h1_count += 1
        elif tag == 'link':
            rel = {x.lower() for x in d.get('rel', '').split()}
            if 'canonical' in rel:
                self.canonicals.append(d.get('href', '').strip())
        elif tag == 'img':
            self.images.append((d.get('src', ''), d.get('alt', '')))
    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False
    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
    @property
    def title(self):
        return ' '.join(''.join(self.title_parts).split())

html_files = sorted(p for p in root.glob('*.html') if p.name.lower() != '404.html')
pages = {}
for p in html_files:
    parser = PageParser()
    parser.feed(p.read_text(encoding='utf-8', errors='ignore'))
    pages[p.name] = parser

errors = defaultdict(list)
warnings = defaultdict(list)

def expected_url(name):
    return BASE_URL if name == 'index.html' else BASE_URL + name

for name, page in pages.items():
    if not page.title:
        errors['缺少 title'].append(name)
    if not (page.meta_description or '').strip():
        errors['缺少 meta description'].append(name)
    if page.h1_count != 1:
        errors['H1 數量不是 1'].append(f'{name} ({page.h1_count})')
    if len(page.canonicals) != 1:
        errors['canonical 數量不是 1'].append(f'{name} ({len(page.canonicals)})')
    elif page.canonicals[0] != expected_url(name):
        errors['canonical URL 不正確'].append(f'{name} → {page.canonicals[0]}')
    for src, alt in page.images:
        if not alt.strip():
            errors['圖片缺少 alt'].append(f'{name} → {src}')
    if page.title and len(page.title) > 65:
        warnings['title 超過 65 字元'].append(f'{name} ({len(page.title)})')
    if page.title and len(page.title) < 10:
        warnings['title 過短'].append(f'{name} ({len(page.title)})')
    desc = page.meta_description or ''
    if desc and len(desc) > 170:
        warnings['meta description 超過 170 字元'].append(f'{name} ({len(desc)})')
    if desc and len(desc) < 50:
        warnings['meta description 少於 50 字元'].append(f'{name} ({len(desc)})')

# Duplicate title / descriptions are critical because they weaken page differentiation.
title_map = defaultdict(list)
desc_map = defaultdict(list)
for name, page in pages.items():
    if page.title:
        title_map[page.title].append(name)
    if page.meta_description:
        desc_map[page.meta_description].append(name)
for value, names in title_map.items():
    if len(names) > 1:
        errors['重複 title'].append(' / '.join(names) + f' → {value}')
for value, names in desc_map.items():
    if len(names) > 1:
        errors['重複 meta description'].append(' / '.join(names) + f' → {value}')

# Sitemap checks.
sitemap = root / 'sitemap.xml'
sitemap_names = set()
if not sitemap.exists():
    errors['Sitemap'].append('sitemap.xml 不存在')
else:
    try:
        tree = ET.parse(sitemap)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = [x.text.strip() for x in tree.findall('.//sm:loc', ns) if x.text]
        if len(locs) != len(set(locs)):
            errors['Sitemap'].append('sitemap.xml 有重複 URL')
        for loc in locs:
            if not loc.startswith(BASE_URL):
                errors['Sitemap'].append(f'非本站 URL：{loc}')
                continue
            if loc == BASE_URL:
                sitemap_names.add('index.html')
            else:
                path = unquote(urlparse(loc).path)
                marker = '/yongxin-electric/'
                if marker not in path:
                    errors['Sitemap'].append(f'路徑不正確：{loc}')
                else:
                    sitemap_names.add(path.split(marker, 1)[1])
    except Exception as exc:
        errors['Sitemap'].append(f'XML 解析失敗：{exc}')

html_names = set(pages)
for name in sorted(html_names - sitemap_names):
    errors['HTML 未收錄 Sitemap'].append(name)
for name in sorted(sitemap_names - html_names):
    errors['Sitemap 指向不存在 HTML'].append(name)

# robots.txt checks.
robots = root / 'robots.txt'
if not robots.exists():
    errors['robots.txt'].append('robots.txt 不存在')
else:
    rtext = robots.read_text(encoding='utf-8', errors='ignore')
    expected_sitemap = f'Sitemap: {BASE_URL}sitemap.xml'
    if expected_sitemap not in rtext:
        errors['robots.txt'].append('缺少正確 Sitemap 宣告')
    if 'User-agent: *' not in rtext:
        errors['robots.txt'].append('缺少 User-agent: *')

status = 'PASS' if not any(errors.values()) else 'CHECK'
critical_checks = 6 * len(pages)  # title, description, H1, canonical, alt-presence domain, sitemap membership
critical_issues = sum(len(v) for v in errors.values())
score = max(0, round(100 * (1 - critical_issues / max(critical_checks, 1)), 1))

lines = [
    '# SEO AUDIT', '',
    f'- 狀態：**{status}**',
    f'- 公開 HTML 頁面：**{len(pages)}**',
    f'- Sitemap URL：**{len(sitemap_names)}**',
    f'- SEO 核心檢查分數：**{score} / 100**',
    f'- Critical issues：**{critical_issues}**',
    f'- Warnings：**{sum(len(v) for v in warnings.values())}**', '',
]

section_order = [
    '缺少 title','缺少 meta description','H1 數量不是 1','canonical 數量不是 1',
    'canonical URL 不正確','圖片缺少 alt','重複 title','重複 meta description',
    'Sitemap','HTML 未收錄 Sitemap','Sitemap 指向不存在 HTML','robots.txt'
]
for key in section_order:
    vals = errors.get(key, [])
    lines.append(f'## {key}')
    if vals:
        lines.extend(f'- `{v}`' for v in vals)
    else:
        lines.append('- 無')
    lines.append('')

lines.append('## 非阻擋式警告')
if not any(warnings.values()):
    lines.append('- 無')
else:
    for key, vals in sorted(warnings.items()):
        lines.append(f'### {key}（{len(vals)}）')
        # Keep the report readable; list first 30 and note remainder.
        lines.extend(f'- `{v}`' for v in vals[:30])
        if len(vals) > 30:
            lines.append(f'- …另有 {len(vals)-30} 項')
        lines.append('')

out = root / 'SEO_AUDIT_v7_21_24.md'
out.write_text('\n'.join(lines), encoding='utf-8')
print(out)
sys.exit(0 if status == 'PASS' else 1)
