// static/js/charts.js — Chart.js Weather Visualization

const WeatherCharts = {
  chartInstance: null,
  forecastChartInstance: null,

  // ── Dashboard Chart ────────────────────────────────────────────
  render(data, canvasId, type = 'temp') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    if (this.chartInstance) { this.chartInstance.destroy(); this.chartInstance = null; }
    const daily = data.daily || [];
    this.chartInstance = this.buildChart(canvas, daily, type);
  },

  update(data, type) {
    if (!data?.daily) return;
    if (this.chartInstance) { this.chartInstance.destroy(); this.chartInstance = null; }
    const canvas = document.getElementById('weather-chart');
    if (canvas) this.chartInstance = this.buildChart(canvas, data.daily, type);
  },

  // ── Forecast Page Chart ────────────────────────────────────────
  renderForecastChart(data, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !data?.daily) return;
    if (this.forecastChartInstance) { this.forecastChartInstance.destroy(); this.forecastChartInstance = null; }
    const daily = data.daily.slice(0, 15);
    const labels = daily.map(d => d.month_day);

    this.forecastChartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Max Temp (°C)',
            data: daily.map(d => d.temp_max),
            backgroundColor: 'rgba(255,138,101,0.7)',
            borderColor: '#ff8a65',
            borderWidth: 2,
            borderRadius: 6,
            type: 'bar',
            yAxisID: 'yTemp',
          },
          {
            label: 'Min Temp (°C)',
            data: daily.map(d => d.temp_min),
            backgroundColor: 'rgba(6,182,212,0.5)',
            borderColor: '#06b6d4',
            borderWidth: 2,
            borderRadius: 6,
            type: 'bar',
            yAxisID: 'yTemp',
          },
          {
            label: 'Precipitation (mm)',
            data: daily.map(d => d.precipitation),
            backgroundColor: 'rgba(79,142,247,0.5)',
            borderColor: '#4f8ef7',
            borderWidth: 2,
            fill: true,
            type: 'line',
            tension: 0.4,
            yAxisID: 'yRain',
            pointRadius: 4,
            pointBackgroundColor: '#4f8ef7',
          },
          {
            label: 'Rain Prob (%)',
            data: daily.map(d => d.precip_prob),
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139,92,246,0.1)',
            borderWidth: 2,
            fill: false,
            type: 'line',
            tension: 0.4,
            yAxisID: 'yProb',
            borderDash: [5, 5],
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            labels: { color: '#8b9cc8', font: { family: 'Inter', size: 11 }, padding: 15 },
          },
          tooltip: {
            backgroundColor: 'rgba(13,20,38,0.95)',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            titleColor: '#f0f4ff',
            bodyColor: '#8b9cc8',
            padding: 10,
            titleFont: { family: 'Inter', weight: '600' },
          },
        },
        scales: {
          x: {
            ticks: { color: '#8b9cc8', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          yTemp: {
            type: 'linear', position: 'left',
            ticks: { color: '#ff8a65', font: { size: 10 }, callback: v => `${v}°C` },
            grid: { color: 'rgba(255,255,255,0.04)' },
            title: { display: true, text: 'Temperature (°C)', color: '#ff8a65', font: { size: 10 } },
          },
          yRain: {
            type: 'linear', position: 'right',
            ticks: { color: '#4f8ef7', font: { size: 10 }, callback: v => `${v}mm` },
            grid: { drawOnChartArea: false },
            title: { display: true, text: 'Rain (mm)', color: '#4f8ef7', font: { size: 10 } },
          },
          yProb: {
            type: 'linear', position: 'right', display: false,
            min: 0, max: 100,
          },
        },
      },
    });
  },

  // ── Core Chart Builder ─────────────────────────────────────────
  buildChart(canvas, daily, type) {
    const labels = daily.slice(0,15).map(d => d.month_day);
    const riskColors = daily.slice(0,15).map(d => d.risk?.color || '#00C853');

    let datasets, yLabel, scales;

    if (type === 'temp') {
      datasets = [
        {
          label: 'Max Temp (°C)',
          data: daily.slice(0,15).map(d => d.temp_max),
          borderColor: '#ff8a65',
          backgroundColor: ctx => this.gradientFill(ctx, '#ff8a65', 0.4, 0.05),
          fill: true, tension: 0.4, pointRadius: 5,
          pointBackgroundColor: riskColors,
          pointBorderColor: '#fff',
          pointBorderWidth: 1.5,
        },
        {
          label: 'Min Temp (°C)',
          data: daily.slice(0,15).map(d => d.temp_min),
          borderColor: '#06b6d4',
          backgroundColor: ctx => this.gradientFill(ctx, '#06b6d4', 0.25, 0.02),
          fill: true, tension: 0.4, pointRadius: 5,
          pointBackgroundColor: riskColors,
          pointBorderColor: '#fff',
          pointBorderWidth: 1.5,
        },
        {
          label: 'Feels Like Max (°C)',
          data: daily.slice(0,15).map(d => d.feels_like_max),
          borderColor: '#FFD700',
          backgroundColor: 'transparent',
          fill: false, tension: 0.4, borderDash: [6, 4],
          pointRadius: 3,
        },
      ];
      yLabel = 'Temperature (°C)';
    } else if (type === 'rain') {
      datasets = [
        {
          label: 'Precipitation (mm)',
          data: daily.slice(0,15).map(d => d.precipitation),
          backgroundColor: ctx => this.gradientFill(ctx, '#4f8ef7', 0.6, 0.05),
          borderColor: '#4f8ef7',
          borderWidth: 2, borderRadius: 6,
          type: 'bar',
        },
        {
          label: 'Rain Probability (%)',
          data: daily.slice(0,15).map(d => d.precip_prob),
          borderColor: '#8b5cf6',
          backgroundColor: 'transparent',
          fill: false, tension: 0.4, type: 'line',
          pointRadius: 4, yAxisID: 'yRight',
        },
      ];
      yLabel = 'Precipitation (mm)';
    } else if (type === 'wind') {
      datasets = [
        {
          label: 'Max Wind Speed (km/h)',
          data: daily.slice(0,15).map(d => d.wind_speed),
          borderColor: '#14b8a6',
          backgroundColor: ctx => this.gradientFill(ctx, '#14b8a6', 0.4, 0.05),
          fill: true, tension: 0.4, pointRadius: 5,
          pointBackgroundColor: '#14b8a6',
        },
      ];
      yLabel = 'Wind Speed (km/h)';
    }

    const cfg = {
      type: type === 'rain' ? 'bar' : 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            labels: { color: '#8b9cc8', font: { family: 'Inter', size: 11 }, padding: 15, usePointStyle: true },
          },
          tooltip: {
            backgroundColor: 'rgba(13,20,38,0.95)',
            borderColor: 'rgba(79,142,247,0.3)',
            borderWidth: 1,
            titleColor: '#f0f4ff',
            bodyColor: '#8b9cc8',
            padding: 12,
            titleFont: { family: 'Inter', weight: '600', size: 12 },
            callbacks: {
              afterBody: (items) => {
                const idx = items[0]?.dataIndex;
                if (idx !== undefined && daily[idx]) {
                  const d = daily[idx];
                  const risk = d.risk || {};
                  return [``, `Risk: ${risk.emoji || ''} ${risk.label || 'SAFE'}`, `Advisory: ${risk.advisory || ''}`];
                }
                return [];
              },
            },
          },
        },
        scales: {
          x: {
            ticks: { color: '#8b9cc8', font: { family: 'Inter', size: 10 }, maxRotation: 45 },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: {
            ticks: { color: '#8b9cc8', font: { family: 'Inter', size: 10 } },
            grid: { color: 'rgba(255,255,255,0.06)' },
            title: { display: true, text: yLabel, color: '#8b9cc8', font: { size: 11 } },
          },
          ...(type === 'rain' ? {
            yRight: {
              type: 'linear', position: 'right', min: 0, max: 100,
              ticks: { color: '#8b5cf6', callback: v => `${v}%` },
              grid: { drawOnChartArea: false },
            }
          } : {}),
        },
      },
    };

    // Apply mixed type for rain
    if (type === 'rain') cfg.type = 'bar';
    return new Chart(canvas, cfg);
  },

  // ── Gradient Fill Helper ───────────────────────────────────────
  gradientFill(ctx, color, alphaTop, alphaBot) {
    const chart = ctx.chart;
    const { height } = chart;
    const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, height);
    const hex = color.replace('#', '');
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    gradient.addColorStop(0, `rgba(${r},${g},${b},${alphaTop})`);
    gradient.addColorStop(1, `rgba(${r},${g},${b},${alphaBot})`);
    return gradient;
  },
};

// Chart.js global defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = 'Inter, sans-serif';
  Chart.defaults.color = '#8b9cc8';
}
