document.addEventListener('DOMContentLoaded', async function () {
  const res = await fetch('/api/stats');
  const data = await res.json();

  new Chart(document.getElementById('pieChart'), {
    type: 'doughnut',
    data: {
      labels: ['Real', 'Fake'],
      datasets: [{ data: [data.real_count, data.fake_count], backgroundColor: ['#198754', '#dc3545'] }]
    },
    options: { plugins: { legend: { position: 'bottom' } } }
  });

  new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels: data.weekly_trend.map(d => d.date.slice(5)),
      datasets: [{
        label: 'Predictions per day',
        data: data.weekly_trend.map(d => d.count),
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79,70,229,0.15)',
        fill: true,
        tension: 0.35
      }]
    },
    options: { plugins: { legend: { display: false } } }
  });
});
