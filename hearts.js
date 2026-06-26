const container = document.getElementById('hearts-bg');
const SYMBOLS = ['❤️', '🩷', '💕', '💗', '💖', '💝'];
const COUNT = 18;

function spawnHeart() {
  const el = document.createElement('span');
  el.className = 'heart';
  el.textContent = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
  el.style.left = Math.random() * 100 + 'vw';
  const duration = 8 + Math.random() * 10;
  const delay = Math.random() * 12;
  el.style.animationDuration = duration + 's';
  el.style.animationDelay = delay + 's';
  el.style.fontSize = (1 + Math.random() * 1.2) + 'rem';
  container.appendChild(el);
  setTimeout(() => el.remove(), (duration + delay) * 1000);
}

for (let i = 0; i < COUNT; i++) spawnHeart();
setInterval(spawnHeart, 1800);

// Animate "reasons" list items on scroll
const items = document.querySelectorAll('.reasons-list li');
const observer = new IntersectionObserver(
  (entries) => entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('visible'), i * 120);
      observer.unobserve(e.target);
    }
  }),
  { threshold: 0.2 }
);
items.forEach(item => observer.observe(item));
