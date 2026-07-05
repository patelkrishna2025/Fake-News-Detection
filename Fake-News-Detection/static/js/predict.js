document.getElementById('predictForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const title = document.getElementById('title').value;
  const article = document.getElementById('article').value;
  const btn = document.getElementById('analyzeBtn');
  const resultArea = document.getElementById('resultArea');

  if (!article.trim()) return;

  const originalBtnHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';

  try {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('article', article);

    const res = await fetch('/predict', { method: 'POST', body: formData });
    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    const isFake = data.prediction === 'Fake';

    document.getElementById('resultLabel').innerHTML =
      isFake
        ? '<i class="fa-solid fa-triangle-exclamation text-danger me-2"></i>Prediction: FAKE NEWS'
        : '<i class="fa-solid fa-circle-check text-success me-2"></i>Prediction: REAL NEWS';

    const badge = document.getElementById('confidenceBadge');
    badge.className = 'badge fs-6 ' + (isFake ? 'bg-danger' : 'bg-success');
    badge.textContent = data.confidence + '% confidence';

    document.getElementById('realBar').style.width = data.real_probability + '%';
    document.getElementById('realBar').textContent = data.real_probability + '%';
    document.getElementById('fakeBar').style.width = data.fake_probability + '%';
    document.getElementById('fakeBar').textContent = data.fake_probability + '%';

    document.getElementById('procTime').textContent = data.processing_time_ms + ' ms';
    document.getElementById('modelUsed').textContent = data.model_used;
    document.getElementById('reportLink').href = '/report/' + data.id;

    const kwContainer = document.getElementById('keywordList');
    kwContainer.innerHTML = '';
    (data.keywords || []).forEach(kw => {
      const span = document.createElement('span');
      span.className = 'keyword-chip ' + (kw.leans === 'Fake' ? 'fake' : 'real');
      span.textContent = `${kw.word} (${kw.leans})`;
      kwContainer.appendChild(span);
    });
    if ((data.keywords || []).length === 0) {
      kwContainer.innerHTML = '<span class="text-muted">No strong indicator words found.</span>';
    }

    resultArea.classList.remove('d-none');
    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    alert('Something went wrong: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalBtnHtml;
  }
});
