const menuBtn = document.querySelector('.menu-btn');
const nav = document.querySelector('.nav');
menuBtn?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', String(open));
});
nav?.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => nav.classList.remove('open')));
const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

function activateProductThumb(gallery, button) {
  const mainImage = gallery.querySelector('#productMainImage, #mainProductImage, .product-main-image img');
  if (!mainImage || !button) return;
  const nextImage = button.dataset.image || button.querySelector('img')?.getAttribute('src');
  if (!nextImage) return;
  mainImage.src = nextImage;
  const nextAlt = button.dataset.alt || button.querySelector('img')?.getAttribute('alt') || mainImage.alt;
  if (nextAlt) mainImage.alt = nextAlt;
  gallery.querySelectorAll('.product-thumb').forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
}

function bindProductGalleries() {
  document.querySelectorAll('.product-gallery').forEach((gallery) => {
    gallery.querySelectorAll('.product-thumb').forEach((button) => {
      if (button.dataset.galleryBound === 'true') return;
      button.dataset.galleryBound = 'true';
      button.setAttribute('type', 'button');
      ['click', 'touchend'].forEach((eventName) => {
        button.addEventListener(eventName, (event) => {
          event.preventDefault();
          activateProductThumb(gallery, button);
        }, { passive: false });
      });
    });
  });
}

function ensureThumbLabels() {
  document.querySelectorAll('.product-thumbnails').forEach((wrap) => {
    wrap.querySelectorAll('.product-thumb').forEach((button, index) => {
      let span = button.querySelector('span');
      if (span && span.textContent.trim()) return;
      const img = button.querySelector('img');
      let label = button.dataset.label || "";
      const raw = (button.dataset.alt || img?.getAttribute('alt') || "").replace(/縮圖/g, "").trim();
      if (!label) {
        const patterns = [
          "正面斜角","正面仰角","正面側角","正面近照","正面","側面銘牌","側面斜角","左側面","右側面","側面","背面端子","背面斜角","背面結構","背面","內部結構","端子面","銘牌","尺寸圖","主圖"
        ];
        label = patterns.find((item) => raw.includes(item)) || "";
      }
      if (!label) {
        const photoMatch = raw.match(/照片\s*\d+/);
        if (photoMatch) label = photoMatch[0];
      }
      if (!label) label = index === 0 ? "主圖" : `照片 ${index + 1}`;
      if (!span) {
        span = document.createElement('span');
        button.appendChild(span);
      }
      span.textContent = label;
      button.dataset.label = label;
    });
  });
}

ensureThumbLabels();

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bindProductGalleries);
} else {
  bindProductGalleries();
}

const knowledgeSearch = document.getElementById('knowledgeSearch');
const knowledgeCards = Array.from(document.querySelectorAll('.knowledge-article-card'));
const knowledgeEmpty = document.getElementById('knowledgeEmpty');
let knowledgeFilter = 'all';
function filterKnowledge() {
  const q = (knowledgeSearch?.value || '').trim().toLowerCase();
  let visible = 0;
  knowledgeCards.forEach((card) => {
    const category = card.dataset.category || '';
    const text = ((card.dataset.search || '') + ' ' + card.textContent).toLowerCase();
    const show = (knowledgeFilter === 'all' || category === knowledgeFilter) && (!q || text.includes(q));
    card.hidden = !show;
    if (show) visible += 1;
  });
  if (knowledgeEmpty) knowledgeEmpty.hidden = visible !== 0;
}
knowledgeSearch?.addEventListener('input', filterKnowledge);
document.querySelectorAll('.knowledge-categories button').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.knowledge-categories button').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    knowledgeFilter = button.dataset.filter || 'all';
    filterKnowledge();
  });
});
