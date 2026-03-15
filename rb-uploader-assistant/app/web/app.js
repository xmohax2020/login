async function fetchDesigns() {
  const status = document.querySelector('#status-filter').value;
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  const res = await fetch(`/designs${query}`);
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
        <button data-copy-title="${d.title || ''}">نسخ العنوان</button>
        <button data-copy-tags="${(d.tags || []).join(', ')}">نسخ الوسوم</button>
        <button data-status="ready" data-id="${d.id}">ready</button>
        <button data-status="uploaded" data-id="${d.id}">uploaded</button>
        <button data-status="published" data-id="${d.id}">published</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll('button[data-copy-title]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      await navigator.clipboard.writeText(e.target.dataset.copyTitle || '');
      alert('تم نسخ العنوان');
    });
  });

  tbody.querySelectorAll('button[data-copy-tags]').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      await navigator.clipboard.writeText(e.target.dataset.copyTags || '');
      alert('تم نسخ الوسوم');
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

async function saveMetadata() {
  const id = document.querySelector('#design-id').value;
  const title = document.querySelector('#title').value;
  const description = document.querySelector('#description').value;
  const tags = document.querySelector('#tags').value.split(',').map(t => t.trim()).filter(Boolean);
  if (!id) return alert('أدخل Design ID');

  const res = await fetch(`/designs/${id}/metadata`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, description, tags }),
  });
  const data = await res.json();
  if (!res.ok) return alert(JSON.stringify(data));
  alert('تم حفظ metadata');
  fetchDesigns();
}

async function regenerateMetadata() {
  const id = document.querySelector('#design-id').value;
  const niche = document.querySelector('#regen-niche').value || 'general';
  if (!id) return alert('أدخل Design ID');
  const res = await fetch(`/designs/${id}/regenerate-metadata?niche=${encodeURIComponent(niche)}`, { method: 'POST' });
  const data = await res.json();
  if (!res.ok) return alert(JSON.stringify(data));
  document.querySelector('#title').value = data.generated.title;
  document.querySelector('#description').value = data.generated.description;
  document.querySelector('#tags').value = data.generated.tags.join(', ');
  alert('تمت إعادة التوليد');
  fetchDesigns();
}

async function loadLogs() {
  const res = await fetch('/audit-logs?limit=50');
  const logs = await res.json();
  document.querySelector('#logs').textContent = JSON.stringify(logs, null, 2);
}

document.querySelector('#refresh-btn').addEventListener('click', fetchDesigns);
document.querySelector('#status-filter').addEventListener('change', fetchDesigns);
document.querySelector('#save-meta-btn').addEventListener('click', saveMetadata);
document.querySelector('#regen-meta-btn').addEventListener('click', regenerateMetadata);
document.querySelector('#load-logs-btn').addEventListener('click', loadLogs);

fetchDesigns();
