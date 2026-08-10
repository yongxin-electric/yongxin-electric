(() => {
  const input = document.getElementById('productSearch');
  const results = document.getElementById('productSearchResults');
  const status = document.getElementById('productSearchStatus');
  const empty = document.getElementById('productSearchEmpty');
  const clearButton = document.getElementById('productSearchClear');
  const examples = document.querySelectorAll('[data-product-search-example]');
  const index = Array.isArray(window.YONGXIN_PRODUCT_INDEX) ? window.YONGXIN_PRODUCT_INDEX : [];
  if (!input || !results || !status) return;

  const normalize = (value) => String(value || '')
    .normalize('NFKC')
    .toLowerCase()
    .replace(/([\u3400-\u9fff])([a-z0-9])/g, '$1 $2')
    .replace(/([a-z0-9])([\u3400-\u9fff])/g, '$1 $2')
    .replace(/[，。；：、,;:|]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const compact = (value) => normalize(value).replace(/[\s\-‐‑–—_\/／\\.·~～()（）\[\]【】]+/g, '');

  const prepared = index.map((item) => ({
    ...item,
    _search: normalize(item.search),
    _compact: compact(item.search),
    _model: normalize(item.model),
    _modelCompact: compact(item.model),
    _title: normalize(item.title),
    _brand: normalize(item.brand),
    _type: normalize(item.type)
  }));

  const escapeHtml = (value) => String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  const tokenize = (query) => {
    const normalized = normalize(query);
    if (!normalized) return [];
    return normalized.split(' ').filter(Boolean);
  };

  function scoreItem(item, query, tokens) {
    const q = normalize(query);
    const qc = compact(query);
    const tokenMatches = tokens.every((token) => {
      const tc = compact(token);
      return item._search.includes(token) || (tc && item._compact.includes(tc));
    });
    const wholeMatch = (q && item._search.includes(q)) || (qc && item._compact.includes(qc));
    if (!tokenMatches && !wholeMatch) return -1;

    let score = 0;
    if (qc && item._modelCompact === qc) score += 1200;
    else if (qc && item._modelCompact.startsWith(qc)) score += 800;
    else if (qc && item._modelCompact.includes(qc)) score += 600;
    if (q && item._title.includes(q)) score += 350;
    if (q && item._brand.includes(q)) score += 250;
    if (q && item._type.includes(q)) score += 180;
    if (wholeMatch) score += 160;
    tokens.forEach((token) => {
      const tc = compact(token);
      if (item._model.includes(token) || (tc && item._modelCompact.includes(tc))) score += 100;
      if (item._brand.includes(token)) score += 60;
      if (item._type.includes(token)) score += 40;
    });
    return score;
  }

  function renderResult(item) {
    const specs = (item.specs || []).slice(0, 4).map(([label, value]) =>
      `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`
    ).join('');
    const image = item.image
      ? `<img loading="lazy" src="${escapeHtml(item.image)}" alt="${escapeHtml(item.title)}"/>`
      : '<span class="product-search-placeholder">◇</span>';
    return `<a class="product-search-result" href="${escapeHtml(item.href)}">
      <div class="product-search-result-image">${image}</div>
      <div class="product-search-result-body">
        <span class="product-search-result-brand">${escapeHtml(item.brand)}</span>
        <h3>${escapeHtml(item.model)}</h3>
        <p>${escapeHtml(item.type)}</p>
        ${specs ? `<dl>${specs}</dl>` : ''}
        <span class="product-search-result-action">查看商品規格 <b>→</b></span>
      </div>
    </a>`;
  }

  function updateUrl(query) {
    const url = new URL(window.location.href);
    if (query) url.searchParams.set('q', query);
    else url.searchParams.delete('q');
    history.replaceState(null, '', url.pathname + url.search + url.hash);
  }

  function runSearch({updateHistory = true} = {}) {
    const query = input.value.trim();
    if (clearButton) clearButton.hidden = !query;
    if (updateHistory) updateUrl(query);

    if (!query) {
      results.innerHTML = '';
      results.hidden = true;
      if (empty) empty.hidden = true;
      status.textContent = `目前收錄 ${prepared.length} 個商品頁。輸入品牌、型號、系列或規格關鍵字開始搜尋。`;
      return;
    }

    const tokens = tokenize(query);
    const matched = prepared
      .map((item) => ({item, score: scoreItem(item, query, tokens)}))
      .filter(({score}) => score >= 0)
      .sort((a, b) => b.score - a.score || a.item.model.localeCompare(b.item.model, 'zh-Hant'));

    const maxVisible = 60;
    const visible = matched.slice(0, maxVisible);
    results.innerHTML = visible.map(({item}) => renderResult(item)).join('');
    results.hidden = visible.length === 0;
    if (empty) empty.hidden = matched.length !== 0;
    status.textContent = matched.length
      ? `找到 ${matched.length} 個相關商品${matched.length > maxVisible ? `，目前顯示前 ${maxVisible} 個` : ''}。`
      : `沒有找到「${query}」的相關商品。`;
  }

  input.addEventListener('input', () => runSearch());
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && input.value) {
      input.value = '';
      runSearch();
      input.focus();
    }
  });

  clearButton?.addEventListener('click', () => {
    input.value = '';
    runSearch();
    input.focus();
  });

  examples.forEach((button) => button.addEventListener('click', () => {
    input.value = button.dataset.productSearchExample || button.textContent.trim();
    runSearch();
    input.focus();
    document.getElementById('product-search')?.scrollIntoView({behavior: 'smooth', block: 'start'});
  }));

  const initial = new URLSearchParams(window.location.search).get('q');
  if (initial) input.value = initial;
  runSearch({updateHistory: false});
})();
