async function fetchDesigns() {
  const res = await fetch('/designs');
  const designs = await res.json();
  const tbody = document.querySelector('#designs-table tbody');
  tbody.innerHTML = '';

  designs.forEach((d) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${d.id}</td>
      <td>${d.slug}</td>
      <td>${d.title || ''}</td>
      <td>${d.status}</td>
      <td>
        <button data-copy-title="${d.title || ''}">Copy title</button>
        <button data-copy-tags="${(d.tags || []).join(', ')}">Copy tags</button>
        <button data-status="ready" data-id="${d.id}">Mark ready</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('button[data-copy-title]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      await navigator.clipboard.writeText(e.target.dataset.copyTitle || '');
      alert('Title copied');
    });
  });

  tbody.querySelectorAll('button[data-copy-tags]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      await navigator.clipboard.writeText(e.target.dataset.copyTags || '');
      alert('Tags copied');
    });
  });

  tbody.querySelectorAll('button[data-status]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.dataset.id;
      const status = e.target.dataset.status;
      await fetch(`/designs/${id}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      fetchDesigns();
    });
  });
}

fetchDesigns();
