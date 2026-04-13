// Top navigation menüü rendering
(function() {
  function renderTopNav() {
    const mount = document.getElementById('top-nav-mount');
    if (!mount || typeof NAV_CATEGORIES === 'undefined') {
      setTimeout(renderTopNav, 100);
      return;
    }

    // Root detection: check if current directory matches a known module name.
    // Works both locally (localhost:8000) and on GitHub Pages (user.github.io/sonavarandus/).
    const moduleNames = NAV_CATEGORIES.flatMap(c => c.cards).map(card => {
      const m = card.href.match(/\.\.\/([^/]+)\//);
      return m ? m[1] : null;
    }).filter(Boolean);

    const pathDirs = window.location.pathname.split('/').filter(p => p && !p.endsWith('.html'));
    const currentDir = decodeURIComponent(pathDirs[pathDirs.length - 1] || '');
    const isRoot = !moduleNames.includes(currentDir);

    function resolveHref(href) {
      return isRoot ? href.replace('../', '') : href;
    }

    // ── Desktop nav ──────────────────────────────────────────
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
        a.href = resolveHref(card.href);
        a.textContent = card.name;
        dropdown.appendChild(a);
      });
      item.appendChild(dropdown);
      nav.appendChild(item);
    });

    const infoItem = document.createElement('a');
    infoItem.className = 'top-nav__trigger';
    infoItem.href = resolveHref('../info.html');
    infoItem.textContent = 'Info';
    infoItem.style.textDecoration = 'none';
    nav.appendChild(infoItem);

    mount.appendChild(nav);

    // ── Hamburger nupp ───────────────────────────────────────
    const header = document.querySelector('.app-header');
    if (header) {
      const hamburger = document.createElement('button');
      hamburger.className = 'nav-hamburger';
      hamburger.setAttribute('aria-label', 'Ava menüü');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.setAttribute('aria-controls', 'mobile-nav');
      hamburger.textContent = '☰';
      header.appendChild(hamburger);

      // ── Mobiilmenüü ─────────────────────────────────────────
      const mobileNav = document.createElement('nav');
      mobileNav.className = 'mobile-nav';
      mobileNav.id = 'mobile-nav';
      mobileNav.setAttribute('aria-label', 'Mobiilmenüü');
      mobileNav.setAttribute('aria-hidden', 'true');

      NAV_CATEGORIES.forEach(cat => {
        const catTitle = document.createElement('div');
        catTitle.className = 'mobile-nav__category';
        catTitle.textContent = cat.name;
        mobileNav.appendChild(catTitle);

        cat.cards.forEach(card => {
          const a = document.createElement('a');
          a.className = 'mobile-nav__link';
          a.href = resolveHref(card.href);
          a.textContent = card.name;
          mobileNav.appendChild(a);
        });
      });

      if (!window.location.pathname.endsWith('info.html')) {
        const infoLink = document.createElement('a');
        infoLink.className = 'mobile-nav__category mobile-nav__category--link';
        infoLink.href = resolveHref('../info.html');
        infoLink.textContent = 'Info';
        mobileNav.appendChild(infoLink);
      }

      document.body.appendChild(mobileNav);

      function openMenu() {
        mobileNav.classList.add('open');
        mobileNav.setAttribute('aria-hidden', 'false');
        hamburger.setAttribute('aria-expanded', 'true');
        hamburger.textContent = '✕';
      }

      function closeMenu() {
        mobileNav.classList.remove('open');
        mobileNav.setAttribute('aria-hidden', 'true');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.textContent = '☰';
      }

      hamburger.addEventListener('click', () => {
        mobileNav.classList.contains('open') ? closeMenu() : openMenu();
      });

      // Sulge menüü, kui link vajutatakse
      mobileNav.addEventListener('click', e => {
        if (e.target.tagName === 'A') closeMenu();
      });
    }

    // ── Mobiil: paneel sulgemisnupp ──────────────────────────
    document.querySelectorAll('.side-panel__inner').forEach(inner => {
      const closeDiv = document.createElement('div');
      closeDiv.className = 'side-panel-close';
      const btn = document.createElement('button');
      btn.textContent = '← Tagasi';
      btn.addEventListener('click', () => {
        const panel = inner.closest('.side-panel');
        if (panel) panel.classList.remove('open');
      });
      closeDiv.appendChild(btn);
      inner.prepend(closeDiv);
    });
  }

  setTimeout(renderTopNav, 0);

  // Mobiilis sulge kõik infokastid vaikimisi
  if (window.innerWidth <= 640) {
    document.querySelectorAll('.page-info-body').forEach(body => {
      body.style.display = 'none';
      const toggle = body.previousElementSibling?.querySelector('.page-info-toggle');
      if (toggle) toggle.textContent = '+';
    });
  }
})();
