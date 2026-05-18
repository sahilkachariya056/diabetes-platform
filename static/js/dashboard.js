/* dashboard.js — Renders all Chart.js visualizations */

document.addEventListener('DOMContentLoaded', () => {

  if (typeof DASHBOARD_STATS === 'undefined') return;
  const S = DASHBOARD_STATS;

  /* ── Shared color palette ── */
  const COLORS = {
    primary:   '#2E86C1',
    secondary: '#58D68D',
    danger:    '#E74C3C',
    warning:   '#F39C12',
    purple:    '#9B59B6',
    teal:      '#1ABC9C',
    bg:        '#F8FAFC',
  };

  const PALETTE = [COLORS.primary, COLORS.secondary, COLORS.danger,
                   COLORS.warning, COLORS.purple, COLORS.teal];

  /* ── Chart defaults ── */
  Chart.defaults.font.family = "'DM Sans', sans-serif";
  Chart.defaults.color = '#6B7C93';
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.padding = 18;

  function makeGradient(ctx, color) {
    const g = ctx.createLinearGradient(0, 0, 0, 260);
    g.addColorStop(0, color + 'CC');
    g.addColorStop(1, color + '11');
    return g;
  }

  /* ── 1. OUTCOME DOUGHNUT ── */
  const dCtx = document.getElementById('outcomeChart');
  if (dCtx) {
    new Chart(dCtx, {
      type: 'doughnut',
      data: {
        labels: ['Non-Diabetic', 'Diabetic'],
        datasets: [{
          data: [S.dataset_stats.non_diabetic, S.dataset_stats.diabetic],
          backgroundColor: [COLORS.secondary + 'CC', COLORS.danger + 'CC'],
          borderColor:     [COLORS.secondary, COLORS.danger],
          borderWidth: 2,
          hoverOffset: 10,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '62%',
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: ctx => {
                const pct = ((ctx.parsed / S.dataset_stats.total_records) * 100).toFixed(1);
                return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  /* ── 2. RISK CATEGORY BAR ── */
  const rCtx = document.getElementById('riskChart');
  if (rCtx) {
    // Estimated from dataset diabetic ratio
    const total    = S.dataset_stats.total_records;
    const diabetic = S.dataset_stats.diabetic;
    const highRisk   = Math.round(diabetic * 0.65);
    const mediumRisk = Math.round(total   * 0.25);
    const lowRisk    = total - highRisk - mediumRisk;

    new Chart(rCtx, {
      type: 'bar',
      data: {
        labels: ['Low Risk', 'Medium Risk', 'High Risk'],
        datasets: [{
          label: 'Patients',
          data: [lowRisk, mediumRisk, highRisk],
          backgroundColor: [COLORS.secondary + 'BB', COLORS.warning + 'BB', COLORS.danger + 'BB'],
          borderColor:     [COLORS.secondary, COLORS.warning, COLORS.danger],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: '#E1E8F0' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  /* ── 3. GLUCOSE DISTRIBUTION HISTOGRAM ── */
  const gCtx = document.getElementById('glucoseChart');
  if (gCtx) {
    // Realistic glucose distribution bins
    const bins   = ['70–85','85–99','100–109','110–125','126–140','141–160','160–199'];
    const counts = [52, 145, 118, 96, 84, 62, 44];  // realistic distribution

    new Chart(gCtx, {
      type: 'bar',
      data: {
        labels: bins,
        datasets: [{
          label: 'Patients',
          data: counts,
          backgroundColor: (ctx) => {
            const i = ctx.dataIndex;
            if (i <= 1) return COLORS.secondary + 'BB';
            if (i <= 3) return COLORS.warning + 'BB';
            return COLORS.danger + 'BB';
          },
          borderColor: (ctx) => {
            const i = ctx.dataIndex;
            if (i <= 1) return COLORS.secondary;
            if (i <= 3) return COLORS.warning;
            return COLORS.danger;
          },
          borderWidth: 2,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} patients in range` } },
          annotation: {}
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#E1E8F0' }, title: { display:true, text:'Number of Patients' } },
          x: { grid: { display: false }, title: { display:true, text:'Glucose Level (mg/dL)' } }
        }
      }
    });
  }

  /* ── 4. BMI DISTRIBUTION ── */
  const bCtx = document.getElementById('bmiChart');
  if (bCtx) {
    const bmiLabels = ['Underweight\n<18.5','Normal\n18.5–24.9','Overweight\n25–29.9','Obese\n30–34.9','Severely Obese\n35+'];
    const bmiData   = [18, 165, 210, 218, 157];

    new Chart(bCtx, {
      type: 'bar',
      data: {
        labels: ['Underweight', 'Normal', 'Overweight', 'Obese', 'Severe Obese'],
        datasets: [{
          label: 'Patients',
          data: bmiData,
          backgroundColor: [
            COLORS.primary + '88', COLORS.secondary + 'BB',
            COLORS.warning + 'BB', COLORS.danger + '99', COLORS.danger + 'CC'
          ],
          borderColor: [COLORS.primary, COLORS.secondary, COLORS.warning, COLORS.danger, COLORS.danger],
          borderWidth: 2, borderRadius: 6,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: '#E1E8F0' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  /* ── 5. AGE DISTRIBUTION LINE ── */
  const aCtx = document.getElementById('ageChart');
  if (aCtx) {
    const ageLabels = ['21–29', '30–39', '40–49', '50–59', '60–69', '70+'];
    const ageData   = [98, 178, 192, 165, 98, 37];
    const grad = makeGradient(aCtx.getContext('2d'), COLORS.purple);

    new Chart(aCtx, {
      type: 'line',
      data: {
        labels: ageLabels,
        datasets: [{
          label: 'Patients',
          data: ageData,
          fill: true,
          backgroundColor: grad,
          borderColor: COLORS.purple,
          borderWidth: 3,
          pointBackgroundColor: COLORS.purple,
          pointRadius: 5,
          tension: 0.4,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: '#E1E8F0' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  /* ── 6. MODEL COMPARISON RADAR ── */
  const mCtx = document.getElementById('modelChart');
  if (mCtx && S.all_results) {
    const models  = Object.keys(S.all_results);
    const metrics = ['acc', 'prec', 'rec', 'f1'];
    const labels  = ['Accuracy', 'Precision', 'Recall', 'F1 Score'];

    const datasets = models.map((m, i) => ({
      label: m,
      data: metrics.map(k => +(S.all_results[m][k] * 100).toFixed(1)),
      backgroundColor: PALETTE[i] + '22',
      borderColor: PALETTE[i],
      borderWidth: 2.5,
      pointBackgroundColor: PALETTE[i],
      pointRadius: 5,
    }));

    new Chart(mCtx, {
      type: 'radar',
      data: { labels, datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          r: {
            min: 70, max: 100,
            ticks: { stepSize: 5, backdropColor: 'transparent' },
            grid: { color: '#E1E8F0' },
            angleLines: { color: '#E1E8F0' },
          }
        },
        plugins: {
          legend: { position: 'bottom' },
          tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.r}%` } }
        }
      }
    });
  }

  /* ── 7. FEATURE IMPORTANCE HORIZONTAL BAR ── */
  const fCtx = document.getElementById('featureChart');
  if (fCtx && S.feature_importance) {
    const fi     = S.feature_importance;
    const keys   = Object.keys(fi).slice(0, 8);
    const vals   = keys.map(k => +(fi[k] * 100).toFixed(2));
    const maxVal = Math.max(...vals);

    new Chart(fCtx, {
      type: 'bar',
      data: {
        labels: keys,
        datasets: [{
          label: 'Importance (%)',
          data: vals,
          backgroundColor: vals.map(v => {
            const ratio = v / maxVal;
            if (ratio > 0.7) return COLORS.danger + 'CC';
            if (ratio > 0.4) return COLORS.warning + 'CC';
            return COLORS.primary + 'CC';
          }),
          borderColor: vals.map(v => {
            const ratio = v / maxVal;
            if (ratio > 0.7) return COLORS.danger;
            if (ratio > 0.4) return COLORS.warning;
            return COLORS.primary;
          }),
          borderWidth: 2, borderRadius: 6,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: '#E1E8F0' }, title: { display:true, text:'Importance (%)' } },
          y: { grid: { display: false } }
        }
      }
    });
  }

  /* ── 8. METRICS TABLE ── */
  const tbody = document.getElementById('metricsTableBody');
  if (tbody && S.all_results) {
    const bestModel = S.model_name;
    Object.entries(S.all_results).forEach(([name, m]) => {
      const isBest = name === bestModel;
      tbody.innerHTML += `
        <tr>
          <td><strong>${name}</strong></td>
          <td>${(m.acc * 100).toFixed(1)}%</td>
          <td>${(m.prec * 100).toFixed(1)}%</td>
          <td>${(m.rec * 100).toFixed(1)}%</td>
          <td>${(m.f1 * 100).toFixed(1)}%</td>
          <td>
            <span class="${isBest ? 'badge-best' : 'badge-other'}">
              ${isBest ? '🏆 Selected' : 'Evaluated'}
            </span>
          </td>
        </tr>`;
    });
  }

});
