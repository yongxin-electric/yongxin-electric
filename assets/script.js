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
