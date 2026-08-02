const menuBtn = document.querySelector('.menu-btn');
const nav = document.querySelector('.nav');
menuBtn?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', String(open));
});
nav?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));
const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();


// v5.9 product image gallery
const productMainImage = document.getElementById('productMainImage');
document.querySelectorAll('.product-thumb').forEach((button) => {
  button.addEventListener('click', () => {
    if (!productMainImage) return;
    productMainImage.src = button.dataset.image || productMainImage.src;
    productMainImage.alt = button.dataset.alt || productMainImage.alt;
    document.querySelectorAll('.product-thumb').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
  });
});


// v7.0 technical article search and category filter
const knowledgeSearch = document.getElementById('knowledgeSearch');
const knowledgeCards = Array.from(document.querySelectorAll('.knowledge-article-card'));
const knowledgeEmpty = document.getElementById('knowledgeEmpty');
let knowledgeFilter = 'all';
function filterKnowledge(){
  const q = (knowledgeSearch?.value || '').trim().toLowerCase();
  let visible = 0;
  knowledgeCards.forEach(card => {
    const category = card.dataset.category || '';
    const text = ((card.dataset.search || '') + ' ' + card.textContent).toLowerCase();
    const show = (knowledgeFilter === 'all' || category === knowledgeFilter) && (!q || text.includes(q));
    card.hidden = !show;
    if(show) visible += 1;
  });
  if(knowledgeEmpty) knowledgeEmpty.hidden = visible !== 0;
}
knowledgeSearch?.addEventListener('input', filterKnowledge);
document.querySelectorAll('.knowledge-categories button').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.knowledge-categories button').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    knowledgeFilter = button.dataset.filter || 'all';
    filterKnowledge();
  });
});
