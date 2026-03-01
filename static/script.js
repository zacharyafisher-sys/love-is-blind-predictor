'use strict';

function syncVal(input, badgeId) {
  document.getElementById(badgeId).textContent = input.value;
}

function getFormData() {
  const fields = [
    'p1_age','p1_emotional','p1_communication','p1_commitment',
    'p2_age','p2_emotional','p2_communication','p2_commitment',
    'physical_attraction','shared_values','conflict_frequency',
    'conflict_resolution','family_approval','emotional_connection',
    'lifestyle_compat','altar_pressure'
  ];

  const data = {};
  for (const f of fields) {
    const el = document.getElementById(f);
    if (!el || el.value === '') return null;
    data[f] = el.value;
  }
  return data;
}

function showError(msg) {
  const el = document.getElementById('error-msg');
  el.textContent = msg;
  el.classList.remove('hidden');
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideError() {
  document.getElementById('error-msg').classList.add('hidden');
}

function renderResult(result) {
  const panel = document.getElementById('result-panel');
  const glow  = document.getElementById('result-glow');
  const names = document.getElementById('result-names');
  const verdict = document.getElementById('result-verdict');
  const bar   = document.getElementById('result-prob-bar');
  const prob  = document.getElementById('result-prob-text');
  const conf  = document.getElementById('result-confidence');
  const insights = document.getElementById('result-insights');

  const p1Name = document.getElementById('p1_name').value.trim() || 'Person 1';
  const p2Name = document.getElementById('p2_name').value.trim() || 'Person 2';
  const isYes = result.prediction;
  const pct = result.marriage_probability;

  // Names
  names.textContent = `${p1Name}  &  ${p2Name}`;

  // Glow
  glow.className = 'result-glow ' + (isYes ? 'yes-glow' : 'no-glow');

  // Verdict
  if (isYes) {
    verdict.innerHTML = `<span class="verdict-yes">They say I Do ♡</span>`;
  } else {
    verdict.innerHTML = `<span class="verdict-no">They say I Don't</span>`;
  }

  // Bar
  bar.className = 'result-prob-bar ' + (isYes ? 'yes-bar' : 'no-bar');
  prob.textContent = `${pct}% chance of marriage`;
  setTimeout(() => { bar.style.width = `${pct}%`; }, 80);

  // Confidence
  conf.textContent = `Confidence: ${result.confidence}`;

  // Insights
  insights.innerHTML = '';
  result.insights.forEach((insight, i) => {
    const [type, text] = insight;
    const div = document.createElement('div');
    div.className = `insight ${type}`;
    div.style.animationDelay = `${0.1 + i * 0.08}s`;
    div.innerHTML = `
      <span class="insight-icon">${type === 'strength' ? '✓' : '!'}</span>
      <span>${text}</span>
    `;
    insights.appendChild(div);
  });

  // Show panel
  panel.classList.remove('hidden');
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetForm() {
  document.getElementById('result-panel').classList.add('hidden');
  document.getElementById('prediction-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.getElementById('prediction-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();

  const data = getFormData();
  if (!data) {
    showError('Please fill in the age fields for both people before predicting.');
    return;
  }

  const btn = document.getElementById('submit-btn');
  btn.classList.add('loading');

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const json = await res.json();
    if (!res.ok || json.error) {
      showError(json.error || 'Prediction failed. Please check your inputs.');
      return;
    }

    renderResult(json);
  } catch (err) {
    showError('Could not connect to the Oracle. Is the server running?');
  } finally {
    btn.classList.remove('loading');
  }
});
