document.querySelectorAll('.delete-btn').forEach(btn => {
  btn.addEventListener('click', async function () {
    const id = this.dataset.id;
    if (!confirm('Delete prediction #' + id + '?')) return;

    const res = await fetch('/admin/delete/' + id, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'deleted') {
      document.getElementById('row-' + id).remove();
    }
  });
});
