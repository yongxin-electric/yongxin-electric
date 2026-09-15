#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.').resolve()
product_files = sorted(p.name for p in root.glob('product-*.html'))
category_files = sorted(p.name for p in root.glob('category-*.html'))
entry_pages = ['index.html', 'products.html', 'brands.html'] + category_files

raw = (root / 'assets' / 'product-search-index.js').read_text(encoding='utf-8')
arr = json.loads(raw.split('=', 1)[1].strip().rstrip(';'))
search_hrefs = [item.get('href', '') for item in arr]
search_set = set(search_hrefs)
product_set = set(product_files)
missing_in_index = sorted(product_set - search_set)
missing_product_files = sorted(set(h for h in search_hrefs if h.startswith('product-')) - product_set)

html_files = entry_pages + product_files
linked_products = set()
broken_links = []
missing_images = []
link_pattern = re.compile(r'href="([^"]+)"')
img_pattern = re.compile(r'src="([^"]+)"')
for name in html_files:
    path = root / name
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    for href in link_pattern.findall(text):
        if href.startswith('http') or href.startswith('tel:') or href.startswith('mailto:') or href.startswith('#'):
            continue
        target = href.split('#', 1)[0].split('?', 1)[0]
        if target.startswith('product-'):
            linked_products.add(target)
        if target and not (root / target).exists():
            broken_links.append((name, target))
    for src in img_pattern.findall(text):
        if src.startswith('http') or src.startswith('data:'):
            continue
        src_path = src.split('?', 1)[0]
        if src_path and not (root / src_path).exists():
            missing_images.append((name, src))

# Content-hygiene keyword scan for obvious non-product documents in referenced image paths/alt text.
# This is not a substitute for manual visual review, but it adds a guardrail for invoices/quotes/receipts.
risk_keywords = ['報價', '估價', '訂單', '發票', '收據', '出貨', '客戶', '電話', '地址', 'quotation', 'invoice', 'receipt']
risky_image_refs = []
for name in html_files:
    path = root / name
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    for m in re.finditer(r'<(?:img|button)[^>]+(?:src|data-image)="([^"]+)"[^>]*>', text, flags=re.I):
        tag = m.group(0).lower()
        src = m.group(1)
        if '/products/' in src and any(k.lower() in tag for k in risk_keywords):
            risky_image_refs.append((name, src))

unlinked_products = sorted(product_set - linked_products)
products_html = (root / 'products.html').read_text(encoding='utf-8', errors='ignore')
count_matches = re.findall(r'(\d+) 個商品頁', products_html)
products_page_declared = int(count_matches[0]) if count_matches else None
status = 'PASS' if not (
    missing_in_index
    or missing_product_files
    or broken_links
    or missing_images
    or risky_image_refs
    or unlinked_products
    or (products_page_declared is not None and products_page_declared != len(product_files))
) else 'CHECK'

lines = []
lines.append('# SITE SYNC AUDIT')
lines.append('')
lines.append(f'- 狀態：**{status}**')
lines.append(f'- 商品頁總數：**{len(product_files)}**')
lines.append(f'- 搜尋索引總數：**{len(arr)}**')
lines.append(f'- products.html 顯示總數：**{products_page_declared if products_page_declared is not None else "未找到"}**')
lines.append('')

def add_section(title, items):
    lines.append(f'## {title}')
    if not items:
        lines.append('- 無')
    else:
        for item in items:
            if isinstance(item, tuple):
                lines.append(f'- `{item[0]}` → `{item[1]}`')
            else:
                lines.append(f'- `{item}`')
    lines.append('')

add_section('商品頁未收錄到搜尋索引', missing_in_index)
add_section('搜尋索引指向不存在的商品頁', missing_product_files)
add_section('商品頁未被入口／分類頁連到', unlinked_products)
add_section('站內連結指向不存在檔案', broken_links)
add_section('HTML 引用但找不到的圖片', missing_images)
add_section('HTML 商品圖引用疑似非商品照片', risky_image_refs)

lines.append('## 分類頁商品連結摘要')
for name in category_files:
    text = (root / name).read_text(encoding='utf-8', errors='ignore')
    count = len(set(re.findall(r'href="(product-[^"]+\.html)"', text)))
    lines.append(f'- `{name}`：{count} 個商品頁連結')
lines.append('')

out_path = root / 'SITE_SYNC_AUDIT_v7_21_23.md'
out_path.write_text('\n'.join(lines), encoding='utf-8')
print(out_path)
