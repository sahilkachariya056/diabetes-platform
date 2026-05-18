/* prediction.js — Handles form, API call, results rendering */

document.addEventListener('DOMContentLoaded', () => {

  const form          = document.getElementById('predForm');
  const predictBtn    = document.getElementById('predictBtn');
  const fillDemo      = document.getElementById('fillDemo');
  const placeholder   = document.getElementById('placeholder');
  const loadingSpinner= document.getElementById('loadingSpinner');
  const resultsContent= document.getElementById('resultsContent');

  /* ── Demo data (realistic high-risk patient) ── */
  const DEMO = {
    Pregnancies: 5,
    Glucose: 162,
    BloodPressure: 88,
    SkinThickness: 35,
    Insulin: 185,
    BMI: 33.6,
    DiabetesPedigreeFunction: 0.627,
    Age: 52,
  };

  const DEMO_LOW = {
    Pregnancies: 1,
    Glucose: 94,
    BloodPressure: 68,
    SkinThickness: 22,
    Insulin: 45,
    BMI: 22.1,
    DiabetesPedigreeFunction: 0.167,
    Age: 28,
  };

  let demoToggle = true;

  if (fillDemo) {
    fillDemo.addEventListener('click', () => {
      const data = demoToggle ? DEMO : DEMO_LOW;
      Object.entries(data).forEach(([key, val]) => {
        const el = document.getElementById(key);
        if (el) el.value = val;
      });
      fillDemo.innerHTML = demoToggle
        ? '<i class="bi bi-magic"></i> Demo Low'
        : '<i class="bi bi-magic"></i> Demo';
      demoToggle = !demoToggle;
    });
  }

  /* ── Form validation ── */
  function validateForm() {
    let valid = true;
    form.querySelectorAll('input[required]').forEach(input => {
      const val = parseFloat(input.value);
      const min = parseFloat(input.min);
      const max = parseFloat(input.max);
      const ok  = !isNaN(val) && val >= (isNaN(min) ? -Infinity : min) && val <= (isNaN(max) ? Infinity : max);
      input.classList.toggle('invalid', !ok);
      if (!ok) valid = false;
    });
    return valid;
  }

  /* ── Show / hide result panels ── */
  function showState(state) {
    placeholder.classList.add('hidden');
    loadingSpinner.classList.add('hidden');
    resultsContent.classList.add('hidden');
    if (state === 'loading') loadingSpinner.classList.remove('hidden');
    else if (state === 'results') resultsContent.classList.remove('hidden');
    else placeholder.classList.remove('hidden');
  }

  /* ── Animate gauge ── */
  function animateGauge(pct) {
    const arc       = document.getElementById('gaugeArc');
    const gaugeText = document.getElementById('gaugeText');
    if (!arc) return;

    const total  = 204; // full arc dasharray
    const offset = total - (total * pct / 100);
    const color  = pct < 30 ? '#27AE60' : pct < 60 ? '#F39C12' : '#E74C3C';

    arc.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1), stroke .5s';
    arc.setAttribute('stroke', color);
    arc.setAttribute('stroke-dashoffset', offset);

    // Animate number
    let current = 0;
    const step = pct / 60;
    const timer = setInterval(() => {
      current = Math.min(current + step, pct);
      if (gaugeText) gaugeText.textContent = Math.round(current) + '%';
      if (current >= pct) clearInterval(timer);
    }, 16);
  }

  /* ── Render results ── */
  function renderResults(data) {
    // Risk badge
    const badge = document.getElementById('riskBadge');
    badge.textContent = `${data.risk_icon} ${data.risk_level} Risk`;
    badge.style.background = data.risk_color + '22';
    badge.style.color = data.risk_color;

    // Gauge
    animateGauge(data.risk_percentage);

    // Health score
    const hs = document.getElementById('healthScore');
    hs.textContent = data.health_score + '/100';
    const fill = document.getElementById('hsFill');
    setTimeout(() => { fill.style.width = data.health_score + '%'; }, 200);

    // Model tag
    document.getElementById('modelTag').textContent =
      `Powered by ${data.model_name} · Confidence: ${data.confidence}%`;

    // Top factors
    const fl = document.getElementById('factorsList');
    fl.innerHTML = '';
    (data.top_factors || []).forEach(f => {
      fl.innerHTML += `
        <div class="factor-item">
          <span class="factor-name">${f.name}</span>
          <div class="factor-bar-track">
            <div class="factor-bar-fill" style="width:0%" data-w="${f.importance}%"></div>
          </div>
          <span class="factor-pct">${f.importance}%</span>
        </div>`;
    });
    // Animate bars after DOM insert
    setTimeout(() => {
      fl.querySelectorAll('.factor-bar-fill').forEach(bar => {
        bar.style.width = bar.dataset.w;
      });
    }, 200);

    // Recommendations
    const rl = document.getElementById('recsList');
    rl.innerHTML = '';
    (data.recommendations || []).forEach(r => {
      rl.innerHTML += `
        <div class="rec-item" style="--rec-color:${r.color}">
          <div class="rec-icon">${r.icon}</div>
          <div class="rec-body">
            <span class="rec-cat">${r.category}</span>
            <strong>${r.title}</strong>
            <p>${r.advice}</p>
          </div>
        </div>`;
    });

    showState('results');

    // Scroll results into view on mobile
    if (window.innerWidth < 900) {
      document.getElementById('resultsContent').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  /* ── Form submit ── */
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!validateForm()) {
        alert('Please fill in all fields with valid values.');
        return;
      }

      const inputs = {};
      form.querySelectorAll('input').forEach(inp => {
        inputs[inp.name] = parseFloat(inp.value);
      });

      showState('loading');
      predictBtn.disabled = true;
      predictBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Analyzing…';

      try {
        const res  = await fetch('/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(inputs),
        });
        const data = await res.json();

        if (data.error) throw new Error(data.error);
        renderResults(data);

      } catch (err) {
        showState('placeholder');
        alert('Prediction error: ' + err.message);
      } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = '<i class="bi bi-cpu"></i> Analyze Risk Now';
      }
    });
  }

  /* Reset */
  const resetBtn = document.getElementById('resetBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      form.querySelectorAll('input').forEach(i => i.classList.remove('invalid'));
      showState('placeholder');
      demoToggle = true;
      if (fillDemo) fillDemo.innerHTML = '<i class="bi bi-magic"></i> Demo';
    });
  }

});
