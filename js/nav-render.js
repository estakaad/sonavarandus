// Sidebar menüü rendering
document.addEventListener('DOMContentLoaded', function() {
  const navContainer = document.getElementById('nav-sidebar');
  if (!navContainer) return;

  const sidebar = document.createElement('div');
  sidebar.className = 'nav-sidebar';

  // Logo/home button
  const logo = document.createElement('div');
  logo.className = 'nav-logo';
  logo.innerHTML = '<a href="../index.html">⬅ Keele peal</a>';
  sidebar.appendChild(logo);

  // Categories
  NAV_CATEGORIES.forEach((cat, catIdx) => {
    const catDiv = document.createElement('div');
    catDiv.className = 'nav-category';

    const catHeader = document.createElement('div');
    catHeader.className = 'nav-category-header';
    catHeader.innerHTML = `
      <span>${cat.name}</span>
      <span class="nav-toggle">▶</span>
    `;
    catHeader.addEventListener('click', () => {
      const items = catDiv.querySelector('.nav-items');
      const toggle = catHeader.querySelector('.nav-toggle');
      items.classList.toggle('open');
      toggle.classList.toggle('open');
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
});
