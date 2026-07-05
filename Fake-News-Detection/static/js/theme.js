(function () {
  const root = document.documentElement;
  const btn = document.getElementById('themeToggle');

  function apply(theme) {
    root.setAttribute('data-bs-theme', theme);
    if (btn) {
      btn.innerHTML = theme === 'dark'
        ? '<i class="fa-solid fa-sun"></i>'
        : '<i class="fa-solid fa-moon"></i>';
    }
  }

  const saved = (typeof window.__theme !== 'undefined') ? window.__theme : 'light';
  apply(saved);

  if (btn) {
    btn.addEventListener('click', function () {
      const current = root.getAttribute('data-bs-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      apply(next);
      window.__theme = next;
    });
  }
})();
