document.getElementById('searchBtn').addEventListener('click', async function () {
  const keyword = document.getElementById('searchKeyword').value;
  const date = document.getElementById('searchDate').value;
  const type = document.getElementById('searchType').value;

  const params = new URLSearchParams({ keyword, date, type });
  const res = await fetch('/api/history?' + params.toString());
  const rows = await res.json();

  const tbody = document.getElementById('historyBody');
  if (rows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No results found.</td></tr>';
    return;
  }

  tbody.innerHTML = rows.map(r => `
    <tr>
      <td>${r.id}</td>
      <td>${(r.title || r.article_text).slice(0, 50)}...</td>
      <td><span class="badge ${r.prediction === 'Fake' ? 'bg-danger' : 'bg-success'}">${r.prediction}</span></td>
      <td>${r.confidence}%</td>
      <td>${r.created_at}</td>
      <td><a href="/report/${r.id}" target="_blank"><i class="fa-solid fa-file-pdf text-danger"></i></a></td>
    </tr>
  `).join('');
});
