// Top navigation menüü rendering
(function() {
  function renderTopNav() {
    const mount = document.getElementById('top-nav-mount');
    if (!mount || typeof NAV_CATEGORIES === 'undefined') {
      setTimeout(renderTopNav, 100);
      return;
    }

    // Root detection: strip '../' if at root level
    const cleanPath = window.location.pathname.replace(/\/[^/]+\.html$/, '/');
    const depth = cleanPath.split('/').filter(Boolean).length;
    const isRoot = depth <= 1;

    const nav = document.createElement('nav');
    nav.className = 'top-nav';
    nav.setAttribute('aria-label', 'Peamenüü');

    NAV_CATEGORIES.forEach(cat => {
      const item = document.createElement('div');
      item.className = 'top-nav__item';

      const trigger = document.createElement('button');
      trigger.className = 'top-nav__trigger';
      trigger.textContent = cat.name;
      trigger.setAttribute('aria-haspopup', 'true');
      item.appendChild(trigger);

      const dropdown = document.createElement('div');
      dropdown.className = 'top-nav__dropdown';
      cat.cards.forEach(card => {
        const a = document.createElement('a');
        a.className = 'top-nav__link';
        a.href = isRoot ? card.href.replace('../', '') : card.href;
        a.textContent = card.name;
        dropdown.appendChild(a);
      });
      item.appendChild(dropdown);
      nav.appendChild(item);
    });

    mount.appendChild(nav);
  }

  setTimeout(renderTopNav, 0);
})();
