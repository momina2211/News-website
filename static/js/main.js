/**
 * NewsHub — main.js
 * Features: dark mode, mobile menu, reading progress, share buttons
 */

// ─── Dark / Light Mode ──────────────────────────────────────────────────────
const htmlRoot = document.getElementById('html-root');
const themeToggle = document.getElementById('theme-toggle');

function applyTheme(theme) {
  if (theme === 'dark') {
    htmlRoot.classList.add('dark');
  } else {
    htmlRoot.classList.remove('dark');
  }
  localStorage.setItem('theme', theme);
}

// Init theme from localStorage or system preference
(function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) {
    applyTheme(saved);
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    applyTheme('dark');
  }
})();

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = htmlRoot.classList.contains('dark') ? 'dark' : 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });
}

// ─── Mobile Menu Toggle ──────────────────────────────────────────────────────
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const hamburgerIcon = document.getElementById('hamburger-icon');
const closeIcon = document.getElementById('close-icon');

if (mobileMenuBtn && mobileMenu) {
  mobileMenuBtn.addEventListener('click', () => {
    const isOpen = !mobileMenu.classList.contains('hidden');
    mobileMenu.classList.toggle('hidden');
    hamburgerIcon.classList.toggle('hidden');
    closeIcon.classList.toggle('hidden');
    mobileMenuBtn.setAttribute('aria-expanded', String(!isOpen));
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!mobileMenuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.add('hidden');
      hamburgerIcon.classList.remove('hidden');
      closeIcon.classList.add('hidden');
    }
  });
}

// ─── Reading Progress Bar ────────────────────────────────────────────────────
const progressBar = document.getElementById('reading-bar');
const articleBody = document.getElementById('article-body');

if (progressBar && articleBody) {
  function updateProgress() {
    const rect = articleBody.getBoundingClientRect();
    const total = articleBody.offsetHeight - window.innerHeight;
    if (total <= 0) {
      progressBar.style.width = '100%';
      return;
    }
    const progress = Math.min(100, Math.max(0, (-rect.top / total) * 100));
    progressBar.style.width = progress.toFixed(1) + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
}

// ─── Share Article Buttons ───────────────────────────────────────────────────
function shareOn(platform) {
  const shareEl = document.getElementById('share-buttons');
  if (!shareEl) return;
  const url = encodeURIComponent(shareEl.dataset.url || window.location.href);
  const title = encodeURIComponent(shareEl.dataset.title || document.title);

  const urls = {
    twitter: `https://twitter.com/intent/tweet?url=${url}&text=${title}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
  };

  if (urls[platform]) {
    window.open(urls[platform], '_blank', 'width=600,height=400,noopener,noreferrer');
  }
}

function copyLink() {
  const shareEl = document.getElementById('share-buttons');
  const url = (shareEl && shareEl.dataset.url) || window.location.href;
  navigator.clipboard.writeText(url).then(() => {
    showToast('Link copied to clipboard! 🔗');
  }).catch(() => {
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = url;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showToast('Link copied! 🔗');
  });
}

// ─── Toast Notification ──────────────────────────────────────────────────────
function showToast(message, duration = 3000) {
  const existing = document.getElementById('toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'toast-notification';
  toast.textContent = message;
  toast.className = [
    'fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-sm font-medium',
    'px-5 py-3 rounded-full shadow-xl z-50 transition-all duration-300 opacity-0 scale-95',
  ].join(' ');
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.replace('opacity-0', 'opacity-100');
    toast.classList.replace('scale-95', 'scale-100');
  });

  setTimeout(() => {
    toast.classList.replace('opacity-100', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─── Auto-dismiss flash messages ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const messages = document.getElementById('messages');
  if (messages) {
    setTimeout(() => {
      messages.style.transition = 'opacity 0.5s';
      messages.style.opacity = '0';
      setTimeout(() => messages.remove(), 500);
    }, 5000);
  }
});

// ─── HTMX: scroll to comments on load ───────────────────────────────────────
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target.id === 'comments-wrapper') {
    // Comments just loaded — nothing extra needed
  }
});

