
(() => {
  const input = document.getElementById('catalogSearch');
  const cards = Array.from(document.querySelectorAll('.catalog-card'));
  const filters = Array.from(document.querySelectorAll('.catalog-filter'));
  const count = document.getElementById('catalogResultCount');
  const empty = document.getElementById('catalogEmpty');
  let active = 'All Parts';

  function apply(){
    const q = (input?.value || '').trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const catOk = active === 'All Parts' || card.dataset.category === active;
      const qOk = !q || (card.dataset.search || '').includes(q);
      const show = catOk && qOk;
      card.hidden = !show;
      if(show) visible++;
    });
    if(count) count.textContent = `${visible} part${visible===1?'':'s'}`;
    if(empty) empty.hidden = visible !== 0;
  }

  input?.addEventListener('input', apply);
  filters.forEach(btn => btn.addEventListener('click', () => {
    filters.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    active = btn.dataset.filter;
    apply();
  }));
})();
