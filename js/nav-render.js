// Sidebar menüü rendering
(function() {
  function renderNavSidebar() {
    const navContainer = document.getElementById('nav-sidebar');
    if (!navContainer || typeof NAV_CATEGORIES === 'undefined') {
      setTimeout(renderNavSidebar, 100);
      return;
    }

    const sidebar = document.createElement('div');
    sidebar.className = 'nav-sidebar';

    // Categories
    NAV_CATEGORIES.forEach((cat, catIdx) => {
      const catDiv = document.createElement('div');
      catDiv.className = 'nav-category';

      const catHeader = document.createElement('div');
      catHeader.className = 'nav-category-header';
      catHeader.innerHTML = `${cat.name}`;
      catHeader.addEventListener('click', () => {
        const items = catDiv.querySelector('.nav-items');
        items.classList.toggle('open');
      });
      catDiv.appendChild(catHeader);

      const itemsDiv = document.createElement('div');
      itemsDiv.className = 'nav-items';
      cat.cards.forEach(card => {
        const item = document.createElement('a');
        item.className = 'nav-item';
        item.href = card.href;
        item.textContent = card.name;
        itemsDiv.appendChild(item);
      });
      catDiv.appendChild(itemsDiv);

      sidebar.appendChild(catDiv);
    });

    navContainer.appendChild(sidebar);
  }

  // Try immediately
  setTimeout(renderNavSidebar, 0);
})();
