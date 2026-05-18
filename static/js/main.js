/* main.js — Shared across all pages */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Navbar scroll shadow ── */
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 10);
    }, { passive: true });
  }

  /* ── Hamburger / mobile drawer ── */
  const hamburger    = document.getElementById('hamburger');
  const mobileDrawer = document.getElementById('mobileDrawer');
  const overlay      = document.getElementById('drawerOverlay');

  function openDrawer() {
    mobileDrawer.classList.add('open');
    overlay.style.display = 'block';
    requestAnimationFrame(() => overlay.classList.add('show'));
    hamburger.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    mobileDrawer.classList.remove('open');
    overlay.classList.remove('show');
    setTimeout(() => { overlay.style.display = 'none'; }, 250);
    hamburger.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (hamburger) {
    hamburger.addEventListener('click', () => {
      mobileDrawer.classList.contains('open') ? closeDrawer() : openDrawer();
    });
  }
  if (overlay) overlay.addEventListener('click', closeDrawer);

  /* Animate hamburger spans */
  const style = document.createElement('style');
  style.textContent = `
    .hamburger.open span:nth-child(1){transform:rotate(45deg) translate(5px,5px)}
    .hamburger.open span:nth-child(2){opacity:0}
    .hamburger.open span:nth-child(3){transform:rotate(-45deg) translate(5px,-5px)}
  `;
  document.head.appendChild(style);

  /* ── Intersection observer for animate-in ── */
  const animItems = document.querySelectorAll('.animate-in');
  if (animItems.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.animationPlayState = 'running';
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.15 });
    animItems.forEach(el => {
      el.style.animationPlayState = 'paused';
      io.observe(el);
    });
  }

});
