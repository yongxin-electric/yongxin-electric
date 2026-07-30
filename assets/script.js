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
