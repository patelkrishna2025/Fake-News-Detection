document.addEventListener('DOMContentLoaded', async function () {
  const res = await fetch('/api/stats');
  const data = await res.json();

  new Chart(document.getElementById('fakeWordsChart'), {
    type: 'bar',
    data: {
      labels: data.top_fake_words.map(w => w[0]),
      datasets: [{ label: 'Frequency', data: data.top_fake_words.map(w => w[1]), backgroundColor: '#dc3545' }]
    },
    options: { indexAxis: 'y', plugins: { legend: { display: false } } }
  });

  new Chart(document.getElementById('realWordsChart'), {
    type: 'bar',
    data: {
      labels: data.top_real_words.map(w => w[0]),
      datasets: [{ label: 'Frequency', data: data.top_real_words.map(w => w[1]), backgroundColor: '#198754' }]
    },
    options: { indexAxis: 'y', plugins: { legend: { display: false } } }
  });

  new Chart(document.getElementById('distChart'), {
    type: 'pie',
    data: {
      labels: ['Real', 'Fake'],
      datasets: [{ data: [data.real_count, data.fake_count], backgroundColor: ['#198754', '#dc3545'] }]
    }
  });

  const tbody = document.querySelector('#metricsTable tbody');
  const m = data.model_metrics || {};
  const rows = [
    ['Accuracy', m.accuracy], ['Precision', m.precision], ['Recall', m.recall],
    ['F1 Score', m.f1_score], ['ROC AUC', m.roc_auc]
  ];
  tbody.innerHTML = rows.map(r => `<tr><td>${r[0]}</td><td><b>${r[1] ?? '-'}</b></td></tr>`).join('');
});
