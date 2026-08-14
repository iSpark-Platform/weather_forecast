// static/js/app.js — WeatherSense AI Main Controller & Master Tab Engine

const WS = {
  currentCity: 'Mumbai',
  currentLat: null,
  currentLon: null,
  weatherData: null,
  chartInstance: null,
  currentChartType: 'temp',

  init() {
    this.startClock();
    this.initParticles();
    this.bindEvents();
    this.initTabSystem();
    this.initAccordionSystem();

    const activeTab = window.ACTIVE_TAB || 'dashboard';
    this.switchTab(activeTab, false);

    const initialCity = window.DEFAULT_CITY || 'Mumbai';
    this.loadWeatherForCity(initialCity);
    this.loadCoastalPreview();
    this.initCoastalPage();

    if (window.WeatherTutor) WeatherTutor.init();
  },

  // ── Clock ──────────────────────────────────────────────────────
  startClock() {
    const el = document.getElementById('nav-clock');
    if (!el) return;
    const tick = () => {
      const now = new Date();
      el.textContent = now.toLocaleTimeString('en-IN', { hour12: false });
    };
    tick();
    setInterval(tick, 1000);
  },

  // ── Particle Background ────────────────────────────────────────
  initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.4 + 0.1,
    }));

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(79,142,247,${p.alpha})`;
        ctx.fill();
      });
      requestAnimationFrame(animate);
    };
    animate();

    window.addEventListener('resize', () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    });
  },

  // ── Tab Engine ────────────────────────────────────────────────
  initTabSystem() {
    document.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        const tabId = btn.dataset.tab;
        this.switchTab(tabId, true);
      });
    });

    window.addEventListener('popstate', e => {
      const tab = e.state?.tab || 'dashboard';
      this.switchTab(tab, false);
    });

    this.initSlideControls();
  },

  slides: ['dashboard', 'hourly', 'analytics', 'forecast', 'map', 'coastal', 'tutor', 'survival', 'decoder'],

  initSlideControls() {
    // Next / Prev slide buttons
    const btnNext = document.getElementById('btn-next-slide');
    const btnPrev = document.getElementById('btn-prev-slide');

    if (btnNext) btnNext.addEventListener('click', () => this.nextSlide());
    if (btnPrev) btnPrev.addEventListener('click', () => this.prevSlide());

    // Keyboard Arrow navigation
    window.addEventListener('keydown', (e) => {
      // Ignore if typing inside input / textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        this.nextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        this.prevSlide();
      }
    });
  },

  nextSlide() {
    const activeTab = document.querySelector('[data-tab].active')?.dataset.tab || 'dashboard';
    const currentIdx = this.slides.indexOf(activeTab);
    const nextIdx = (currentIdx + 1) % this.slides.length;
    this.switchTab(this.slides[nextIdx], true);
  },

  prevSlide() {
    const activeTab = document.querySelector('[data-tab].active')?.dataset.tab || 'dashboard';
    const currentIdx = this.slides.indexOf(activeTab);
    const prevIdx = (currentIdx - 1 + this.slides.length) % this.slides.length;
    this.switchTab(this.slides[prevIdx], true);
  },

  switchTab(tabId, updateUrl = true) {
    if (!tabId) return;

    // Update buttons
    document.querySelectorAll('[data-tab]').forEach(btn => {
      if (btn.dataset.tab === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update view sections
    document.querySelectorAll('.tab-view').forEach(view => {
      if (view.id === `view-${tabId}`) {
        view.classList.add('active');
      } else {
        view.classList.remove('active');
      }
    });

    // Update Slide Pagination UI
    const currentIdx = this.slides.indexOf(tabId);
    const slideNumberEl = document.getElementById('slide-counter-num');
    if (slideNumberEl && currentIdx !== -1) {
      slideNumberEl.textContent = `Slide ${currentIdx + 1} / ${this.slides.length}`;
    }

    document.querySelectorAll('.slide-dot').forEach((dot, idx) => {
      dot.classList.toggle('active', idx === currentIdx);
    });

    if (updateUrl && window.history && window.history.pushState) {
      const newPath = tabId === 'dashboard' ? '/' : `/${tabId}`;
      window.history.pushState({ tab: tabId }, '', newPath);
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Auto-expand accordion cards in the target view tab
    const targetView = document.getElementById(`view-${tabId}`);
    if (targetView) {
      targetView.querySelectorAll('.accordion-card').forEach(card => {
        this.toggleAccordion(card, true);
      });
    }

    // Trigger tab-specific initialization & resize rendering
    if (tabId === 'dashboard' || tabId === 'live') {
      const currentCard = document.getElementById('current-weather-card');
      const statsCard = document.getElementById('quick-stats');
      if (currentCard) this.toggleAccordion(currentCard, true);
      if (statsCard) this.toggleAccordion(statsCard, true);
    } else if (tabId === 'hourly') {
      const card = document.getElementById('hourly-card');
      if (card) this.toggleAccordion(card, true);
      if (this.weatherData?.hourly) {
        this.renderHourlyStrip(this.weatherData.hourly, 'hourly-scroll');
      }
    } else if (tabId === 'analytics') {
      const card = document.getElementById('temp-chart-card');
      if (card) this.toggleAccordion(card, true);
      if (this.weatherData && window.WeatherCharts) {
        setTimeout(() => WeatherCharts.render(this.weatherData, 'weather-chart', this.currentChartType), 50);
      }
    } else if (tabId === 'forecast') {
      const card1 = document.getElementById('forecast-card');
      const card2 = document.getElementById('flood-risk-card');
      const card3 = document.querySelector('#view-forecast .chart-card');
      if (card1) this.toggleAccordion(card1, true);
      if (card2) this.toggleAccordion(card2, true);
      if (card3) this.toggleAccordion(card3, true);
      if (this.weatherData && window.WeatherCharts) {
        setTimeout(() => WeatherCharts.renderForecastChart(this.weatherData, 'forecast-chart'), 50);
      }
    } else if (tabId === 'coastal') {
      document.querySelectorAll('#view-coastal .accordion-card').forEach(c => this.toggleAccordion(c, true));
      this.initCoastalPage();
      if (window.WeatherMap) {
        setTimeout(() => WeatherMap.initTsunamiMap(), 100);
      }
    } else if (tabId === 'map') {
      if (window.WeatherMap) {
        if (!WeatherMap.fullMap) {
          WeatherMap.initFullMap();
        } else {
          WeatherMap.fullMap.invalidateSize();
          setTimeout(() => WeatherMap.fullMap.invalidateSize(), 150);
        }
      }
    } else if (tabId === 'tutor') {
      document.querySelectorAll('#view-tutor .accordion-card').forEach(c => this.toggleAccordion(c, true));
      if (window.WeatherTutor) WeatherTutor.init();
    } else if (tabId === 'survival') {
      document.querySelectorAll('#view-survival .accordion-card').forEach(c => this.toggleAccordion(c, true));
      if (window.LingoApp) {
        window.LingoApp.renderSurvivalGame();
      }
    } else if (tabId === 'decoder') {
      document.querySelectorAll('#view-decoder .accordion-card').forEach(c => this.toggleAccordion(c, true));
      if (window.LingoApp) {
        window.LingoApp.renderDecoder();
        window.LingoApp.renderPuzzles();
      }
    }
  },

  // ── Accordion Card System ─────────────────────────────────────
  initAccordionSystem() {
    document.addEventListener('click', (e) => {
      const header = e.target.closest('.accordion-card .card-header');
      if (!header) return;

      // Do not collapse if clicked inside interactive buttons inside header
      if (e.target.closest('button, a, input, select') && 
          !e.target.closest('.accordion-toggle-badge') && 
          !e.target.closest('.accordion-toggle-icon')) {
        return;
      }

      const card = header.closest('.accordion-card');
      if (card) {
        this.toggleAccordion(card);
      }
    });

    const btnExpandAll = document.getElementById('btn-expand-all');
    const btnCollapseAll = document.getElementById('btn-collapse-all');

    if (btnExpandAll) {
      btnExpandAll.addEventListener('click', () => this.setAllAccordions(true));
    }
    if (btnCollapseAll) {
      btnCollapseAll.addEventListener('click', () => this.setAllAccordions(false));
    }
  },

  toggleAccordion(card, forceState = null) {
    if (!card) return;
    const isCurrentlyCollapsed = card.classList.contains('collapsed');
    const shouldExpand = forceState !== null ? forceState : isCurrentlyCollapsed;
    
    if (shouldExpand) {
      card.classList.remove('collapsed');
      card.classList.add('expanded');

      // Trigger feature initialization when expanded
      const cardId = card.id;
      if (cardId === 'hourly-card' && this.weatherData?.hourly) {
        this.renderHourlyStrip(this.weatherData.hourly, 'hourly-scroll');
      } else if (cardId === 'temp-chart-card' && this.weatherData && window.WeatherCharts) {
        setTimeout(() => WeatherCharts.render(this.weatherData, 'weather-chart', this.currentChartType), 50);
      } else if (cardId === 'forecast-chart' && this.weatherData && window.WeatherCharts) {
        setTimeout(() => WeatherCharts.renderForecastChart(this.weatherData, 'forecast-chart'), 50);
      } else if (card.closest('#view-map') || cardId === 'full-map') {
        if (window.WeatherMap) {
          if (!WeatherMap.fullMap) WeatherMap.initFullMap();
          else setTimeout(() => WeatherMap.fullMap.invalidateSize(), 150);
        }
      } else if (cardId === 'tsunami-zones-card' || cardId === 'coastal-risk-main') {
        if (window.WeatherMap) setTimeout(() => WeatherMap.initTsunamiMap(), 100);
      } else if ((card.closest('#view-survival') || cardId === 'timer-hero-card') && window.LingoApp) {
        window.LingoApp.renderSurvivalGame();
      } else if ((card.closest('#view-decoder') || cardId === 'lingo-decoder-card') && window.LingoApp) {
        window.LingoApp.renderDecoder();
        window.LingoApp.renderPuzzles();
      }
    } else {
      card.classList.remove('expanded');
      card.classList.add('collapsed');
    }

    const badge = card.querySelector('.accordion-toggle-badge');
    if (badge) {
      const icon = badge.querySelector('.accordion-toggle-icon') || document.createElement('i');
      icon.className = 'fa-solid fa-chevron-down accordion-toggle-icon';
      if (card.classList.contains('collapsed')) {
        badge.innerHTML = `Click to Expand `;
        badge.appendChild(icon);
      } else {
        badge.innerHTML = ``;
        badge.appendChild(icon);
      }
    }
  },

  setAllAccordions(expand = true) {
    document.querySelectorAll('.accordion-card').forEach(card => {
      this.toggleAccordion(card, expand);
    });
  },

  // ── Event Bindings ─────────────────────────────────────────────
  bindEvents() {
    // Search
    const searchBtn = document.getElementById('btn-search');
    const cityInput = document.getElementById('city-input');
    if (searchBtn) searchBtn.addEventListener('click', () => this.handleSearch());
    if (cityInput) {
      cityInput.addEventListener('keydown', e => { if (e.key === 'Enter') this.handleSearch(); });
    }

    // Locate
    const locBtn = document.getElementById('btn-locate');
    if (locBtn) locBtn.addEventListener('click', () => this.useMyLocation());

    // Chart toggles
    document.querySelectorAll('[data-chart]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-chart]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentChartType = btn.dataset.chart;
        if (this.weatherData && window.WeatherCharts) {
          WeatherCharts.update(this.weatherData, this.currentChartType);
        }
      });
    });

    // Quick tutor
    const askBtn = document.getElementById('btn-quick-ask');
    if (askBtn) askBtn.addEventListener('click', () => this.quickAsk());
    const qi = document.getElementById('quick-question');
    if (qi) qi.addEventListener('keydown', e => { if (e.key === 'Enter') this.quickAsk(); });

    // Coastal city tabs
    document.querySelectorAll('.city-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.city-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.loadCoastalData(tab.dataset.city);
      });
    });
  },

  handleSearch() {
    const input = document.getElementById('city-input');
    if (!input) return;
    const city = input.value.trim();
    if (!city) return;
    this.currentCity = city;
    this.loadWeatherForCity(city);
    this.loadCoastalData(city);
  },

  useMyLocation() {
    if (!navigator.geolocation) {
      alert('Geolocation not supported by your browser.');
      return;
    }
    const btn = document.getElementById('btn-locate');
    if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    navigator.geolocation.getCurrentPosition(
      pos => {
        const { latitude: lat, longitude: lon } = pos.coords;
        this.currentLat = lat; this.currentLon = lon;
        if (btn) btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i>';
        this.loadWeatherByCoords(lat, lon);
      },
      err => {
        if (btn) btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i>';
        alert('Could not get your location: ' + err.message);
      }
    );
  },

  // ── Weather Loading ────────────────────────────────────────────
  async loadWeatherForCity(city) {
    this.currentCity = city;
    this.showCurrentLoading();
    try {
      const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
      if (!res.ok) throw new Error('Failed to fetch weather');
      const data = await res.json();
      this.weatherData = data;

      // Render Dashboard & Forecast components
      this.renderCurrentWeather(data);
      this.renderForecastStrip(data.daily);
      this.renderHourlyStrip(data.hourly, 'hourly-scroll');
      this.renderQuickStats(data);
      this.renderLocationHeader(data);
      this.renderRiskBanner(data.overall_risk);
      this.renderFloodRisk(data.flood_risk);
      this.renderForecastGrid(data.daily);

      if (window.WeatherCharts) {
        WeatherCharts.render(data, 'weather-chart', this.currentChartType);
        WeatherCharts.renderForecastChart(data, 'forecast-chart');
      }
      if (window.WeatherMap) WeatherMap.initMiniMaps();
    } catch (e) {
      console.error(e);
      this.showError('current-weather-body', 'Could not load weather. Try a different city.');
    }
  },

  async loadWeatherByCoords(lat, lon) {
    this.showCurrentLoading();
    try {
      const res = await fetch(`/api/weather/coords?lat=${lat}&lon=${lon}`);
      const data = await res.json();
      this.weatherData = data;
      this.renderCurrentWeather(data);
      this.renderForecastStrip(data.daily);
      this.renderHourlyStrip(data.hourly, 'hourly-scroll');
      this.renderQuickStats(data);
      this.renderLocationHeader(data);
      this.renderRiskBanner(data.overall_risk);
      this.renderFloodRisk(data.flood_risk);
      this.renderForecastGrid(data.daily);

      if (window.WeatherCharts) {
        WeatherCharts.render(data, 'weather-chart', this.currentChartType);
        WeatherCharts.renderForecastChart(data, 'forecast-chart');
      }
    } catch (e) { this.showError('current-weather-body', 'Could not load weather.'); }
  },

  // ── Render Current Weather ─────────────────────────────────────
  renderCurrentWeather(data) {
    const el = document.getElementById('current-weather-body');
    if (!el) return;
    const c = data.current || {};
    const loc = data.location || {};
    const risk = data.overall_risk || {};
    const today = data.daily?.[0] || {};

    const badge = document.getElementById('current-risk-badge');
    if (badge) {
      badge.innerHTML = `${risk.emoji || ''} ${risk.label || 'SAFE'}`;
      badge.className = `card-badge risk-${(risk.level||'green').toLowerCase()}`;
    }

    el.innerHTML = `
      <div class="current-weather-body">
        <div class="current-temp-block">
          <div class="current-icon">${c.icon || '<i class="fa-solid fa-cloud"></i>'}</div>
          <div class="current-temp">${c.temperature ?? '--'}°<small>C</small></div>
          <div class="current-condition">${c.condition || 'Unknown'}</div>
          <div class="current-location"><i class="fa-solid fa-location-dot" style="color:var(--accent-blue)"></i> ${loc.name || this.currentCity}${loc.country ? ', ' + loc.country : ''}</div>
        </div>
        <div class="current-details">
          <div class="detail-row"><span class="detail-icon"><i class="fa-solid fa-droplet" style="color:#38bdf8"></i></span><div><div class="detail-label">Humidity</div><div class="detail-value">${c.humidity ?? '--'}%</div></div></div>
          <div class="detail-row"><span class="detail-icon"><i class="fa-solid fa-wind" style="color:#14b8a6"></i></span><div><div class="detail-label">Wind</div><div class="detail-value">${c.wind_speed ?? '--'} km/h</div></div></div>
          <div class="detail-row"><span class="detail-icon"><i class="fa-solid fa-sun" style="color:#f59e0b"></i></span><div><div class="detail-label">UV Index</div><div class="detail-value">${c.uv_index ?? '--'}</div></div></div>
          <div class="detail-row"><span class="detail-icon"><i class="fa-solid fa-eye" style="color:#8b5cf6"></i></span><div><div class="detail-label">Visibility</div><div class="detail-value">${c.visibility ?? '--'} km</div></div></div>
          <div class="detail-row"><span class="detail-icon"><i class="fa-solid fa-gauge-high" style="color:#06b6d4"></i></span><div><div class="detail-label">Pressure</div><div class="detail-value">${c.pressure ?? '--'} hPa</div></div></div>
          <div class="detail-row"><span class="detail-icon"><i class="fa-solid fa-cloud" style="color:#cbd5e1"></i></span><div><div class="detail-label">Cloud Cover</div><div class="detail-value">${c.cloud_cover ?? '--'}%</div></div></div>
        </div>
      </div>`;

    document.getElementById('s-humidity').textContent = `${c.humidity ?? '--'}%`;
    document.getElementById('s-wind').textContent = `${c.wind_speed ?? '--'} km/h`;
    document.getElementById('s-uv').textContent = c.uv_index ?? '--';
    document.getElementById('s-feels').textContent = `${today.feels_like_max ?? '--'}°C`;
    document.getElementById('s-vis').textContent = `${c.visibility ?? '--'} km`;
    document.getElementById('s-pres').textContent = `${c.pressure ?? '--'} hPa`;
    document.getElementById('s-sunrise').textContent = today.sunrise ?? '--';
    document.getElementById('s-sunset').textContent = today.sunset ?? '--';
  },

  renderQuickStats(data) {},

  // ── Forecast Strip ──────────────────────────────────────────────
  renderForecastStrip(daily) {
    const el = document.getElementById('forecast-strip');
    if (!el || !daily) return;
    el.innerHTML = daily.slice(0, 15).map((d, i) => `
      <div class="forecast-day ${i === 0 ? 'today' : ''}" onclick="WS.switchTab('forecast')">
        <div class="fd-risk-bar" style="background:${d.risk?.color || '#00C853'}"></div>
        <div class="fd-day">${i === 0 ? 'TODAY' : d.day_name?.slice(0,3).toUpperCase()}</div>
        <div class="fd-date">${d.month_day}</div>
        <div class="fd-icon">${d.icon}</div>
        <div class="fd-temps">
          <span class="fd-high">${d.temp_max}°</span>
          <span style="color:#4a5a80">/</span>
          <span class="fd-low">${d.temp_min}°</span>
        </div>
        <div class="fd-cond">${d.condition}</div>
        <div class="fd-rain"><i class="fa-solid fa-droplet" style="color:#38bdf8"></i> ${d.precip_prob}%</div>
      </div>`).join('');
  },

  // ── Hourly Strip ───────────────────────────────────────────────
  renderHourlyStrip(hourly, containerId) {
    const el = document.getElementById(containerId);
    if (!el || !hourly) return;
    el.innerHTML = hourly.slice(0, 48).map(h => `
      <div class="hourly-card">
        <div class="hc-time">${h.hour}</div>
        <div class="hc-icon">${h.icon}</div>
        <div class="hc-temp">${h.temperature}°</div>
        <div class="hc-rain"><i class="fa-solid fa-droplet"></i> ${h.precip_prob}%</div>
        <div class="hc-wind"><i class="fa-solid fa-wind"></i> ${h.wind_speed}</div>
      </div>`).join('');
  },

  // ── Coastal Preview ────────────────────────────────────────────
  async loadCoastalPreview() {
    const el = document.getElementById('coastal-list');
    if (!el) return;
    const cities = ['Mumbai', 'Chennai', 'Kolkata', 'Visakhapatnam', 'Kochi'];
    const results = await Promise.allSettled(
      cities.map(c => fetch(`/api/coastal?city=${encodeURIComponent(c)}`).then(r => r.json()))
    );
    el.innerHTML = results.map((r, i) => {
      if (r.status !== 'fulfilled' || r.value.error) {
        return `<div class="coastal-city-row"><span class="cc-name">${cities[i]}</span><span class="cc-risk risk-green">SAFE</span></div>`;
      }
      const d = r.value;
      const risk = d.overall_risk || {};
      const today = d.daily?.[0] || {};
      return `<div class="coastal-city-row" onclick="WS.switchTab('coastal')">
        <div><div class="cc-name">${d.city?.name || cities[i]}</div><div class="cc-coast">${d.city?.coast || ''} Coast</div></div>
        <div class="cc-temp">${today.temp_max ?? '--'}°/${today.temp_min ?? '--'}°</div>
        <div class="cc-risk risk-${(risk.level||'green').toLowerCase()}">${risk.emoji || ''} ${risk.label || 'SAFE'}</div>
      </div>`;
    }).join('');
  },

  // ── Forecast Page Components ──────────────────────────────────
  renderLocationHeader(data) {
    const el = document.getElementById('location-header');
    if (!el) return;
    const loc = data.location || {};
    el.innerHTML = `
      <div class="loc-icon"><i class="fa-solid fa-location-dot" style="color:var(--accent-blue)"></i></div>
      <div>
        <div class="loc-name">${loc.name || this.currentCity}${loc.admin1 ? ', ' + loc.admin1 : ''}</div>
        <div class="loc-country">${loc.country || ''} • ${loc.timezone || ''}</div>
        <div class="loc-coords">Lat: ${(data.lat||0).toFixed(4)}° Lon: ${(data.lon||0).toFixed(4)}° • Elevation: ${data.elevation ?? '--'} m</div>
      </div>`;
  },

  renderRiskBanner(risk) {
    const el = document.getElementById('risk-banner');
    if (!el || !risk) return;
    el.style.display = 'block';
    el.style.background = risk.bg || 'rgba(0,200,83,0.1)';
    el.style.borderColor = risk.border || '#00C853';
    document.getElementById('banner-emoji').innerHTML = risk.emoji || '<i class="fa-solid fa-shield-halved"></i>';
    document.getElementById('banner-label').textContent = `15-Day Outlook: ${risk.label}`;
    document.getElementById('banner-label').style.color = risk.color || '#00C853';
    document.getElementById('banner-desc').textContent = risk.description || '';
  },

  renderFloodRisk(flood) {
    const el = document.getElementById('flood-risk-card');
    const body = document.getElementById('flood-risk-body');
    if (!el || !flood) return;
    el.style.display = 'block';
    el.style.borderLeft = `4px solid ${flood.color || '#00C853'}`;
    body.innerHTML = `
      <div style="color:${flood.color};font-weight:700;font-size:1rem;margin-bottom:.5rem">${flood.label}</div>
      <div class="flood-stats">
        <div class="flood-stat"><div class="flood-stat-val" style="color:${flood.color}">${flood.total_rain?.toFixed(0) ?? '--'} mm</div><div class="flood-stat-label">15-Day Total Rain</div></div>
        <div class="flood-stat"><div class="flood-stat-val" style="color:${flood.color}">${flood.max_daily?.toFixed(0) ?? '--'} mm</div><div class="flood-stat-label">Max Single Day</div></div>
        <div class="flood-stat"><div class="flood-stat-val" style="color:${flood.color}">${flood.heavy_days ?? '--'}</div><div class="flood-stat-label">Heavy Rain Days</div></div>
      </div>`;
  },

  renderForecastGrid(daily) {
    const el = document.getElementById('forecast-grid');
    if (!el || !daily) return;
    el.innerHTML = daily.slice(0, 15).map((d, i) => {
      const riskColor = d.risk?.color || '#00C853';
      const riskLevel = (d.risk?.level || 'green').toLowerCase();
      return `
        <div class="forecast-card" style="animation:fadeInUp .4s ease both ${i * 0.05}s">
          <div class="risk-top-bar" style="background:${riskColor}"></div>
          <div class="fc-day">${i === 0 ? 'TODAY' : d.day_name?.slice(0,3).toUpperCase()}</div>
          <div class="fc-date">${d.month_day}</div>
          <div class="fc-icon">${d.icon}</div>
          <div class="fc-temps">
            <span class="fc-high">${d.temp_max}°</span>
            <span style="color:#4a5a80">/</span>
            <span class="fc-low">${d.temp_min}°</span>
          </div>
          <div class="fc-cond">${d.condition}</div>
          <div class="fc-details">
            <span><i class="fa-solid fa-droplet"></i> ${d.precip_prob}%</span>
            <span><i class="fa-solid fa-wind"></i> ${d.wind_speed}</span>
            <span><i class="fa-solid fa-sun"></i> ${d.uv_index}</span>
          </div>
          <div class="fc-risk-badge risk-${riskLevel}">${d.risk?.emoji || ''} ${d.risk?.label || 'SAFE'}</div>
        </div>`;
    }).join('');
  },

  // ── Coastal Components ─────────────────────────────────────────
  initCoastalPage() {
    this.loadLiveAlerts();
    const firstTab = document.querySelector('.city-tab');
    if (firstTab) this.loadCoastalData(firstTab.dataset.city);
  },

  async loadCoastalData(cityName) {
    const mainCard = document.getElementById('coastal-risk-main');
    if (mainCard) mainCard.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
    try {
      const res = await fetch(`/api/coastal?city=${encodeURIComponent(cityName)}`);
      const data = await res.json();
      this.renderCoastalMain(data);
      this.renderThreatMatrix(data);
    } catch (e) {
      console.error(e);
    }
  },

  renderCoastalMain(data) {
    const el = document.getElementById('coastal-risk-main');
    if (!el) return;
    const risk = data.overall_risk || {};
    const city = data.city || {};
    const today = data.daily?.[0] || {};
    const alerts = today.alerts || [];
    el.innerHTML = `
      <div class="card-header">
        <h2><i class="fa-solid fa-water" style="color:var(--accent-cyan)"></i> ${city.name} — ${city.coast} Coast</h2>
        <span class="card-badge risk-${(risk.level||'green').toLowerCase()}">${risk.emoji} ${risk.label}</span>
      </div>
      <div style="display:flex;gap:2rem;align-items:center;flex-wrap:wrap">
        <div style="text-align:center">
          <div style="font-size:3rem">${today.icon || '<i class="fa-solid fa-cloud"></i>'}</div>
          <div style="font-size:2rem;font-weight:300">${today.temp_max ?? '--'}°<small style="font-size:1rem">C</small></div>
          <div style="font-size:.85rem;color:var(--text-secondary)">${today.condition || ''}</div>
        </div>
        <div style="flex:1">
          <div style="color:${risk.color};font-weight:700;font-size:1.1rem;margin-bottom:.5rem">${risk.description || ''}</div>
          <div style="font-size:.85rem;color:var(--text-secondary);margin-bottom:1rem">${risk.advisory || ''}</div>
          <div style="display:flex;gap:.5rem;flex-wrap:wrap">
            ${alerts.map(a => `<span style="padding:.25rem .7rem;border-radius:20px;font-size:.75rem;font-weight:700;background:rgba(255,45,45,.15);color:${a.level==='RED'?'#ff6b6b':'#ffab40'}">${a.icon} ${a.type}</span>`).join('')}
            ${alerts.length === 0 ? '<span style="color:var(--risk-green);font-size:.85rem"><i class="fa-solid fa-shield-halved"></i> No active coastal alerts</span>' : ''}
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem;min-width:200px">
          <div class="detail-row"><span><i class="fa-solid fa-wind" style="color:#14b8a6"></i></span><div><div class="detail-label">Wind</div><div class="detail-value">${today.wind_speed ?? '--'} km/h</div></div></div>
          <div class="detail-row"><span><i class="fa-solid fa-cloud-showers-heavy" style="color:#38bdf8"></i></span><div><div class="detail-label">Rain</div><div class="detail-value">${today.precipitation ?? '--'} mm</div></div></div>
          <div class="detail-row"><span><i class="fa-solid fa-droplet" style="color:#0284c7"></i></span><div><div class="detail-label">Rain Prob</div><div class="detail-value">${today.precip_prob ?? '--'}%</div></div></div>
          <div class="detail-row"><span><i class="fa-solid fa-sun" style="color:#ffb703"></i></span><div><div class="detail-label">Sunrise</div><div class="detail-value">${today.sunrise ?? '--'}</div></div></div>
        </div>
      </div>`;
  },

  renderThreatMatrix(data) {
    const tsunami = data.tsunami_risk || {};
    const cyclone = data.cyclone_risk || {};
    const flood = data.flood_risk || {};

    const setThreat = (id, color, text) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.style.borderColor = color;
      el.style.background = color + '15';
      el.querySelector('.threat-level').textContent = text;
      el.querySelector('.threat-level').style.color = color;
    };

    setThreat('threat-tsunami', tsunami.color || '#00C853', tsunami.label?.split('—')[0].trim() || 'Low Risk');
    setThreat('threat-cyclone', cyclone.risk === 'LOW' ? '#00C853' : (cyclone.risk === 'MODERATE' ? '#FFD700' : '#FF8C00'), cyclone.label || 'No Cyclone');
    setThreat('threat-flood', flood.color || '#00C853', flood.risk || 'LOW');
    setThreat('threat-storm', data.overall_risk?.level === 'RED' ? '#FF2D2D' : '#00C853', data.overall_risk?.level === 'RED' ? 'HIGH RISK' : 'LOW RISK');
  },

  async loadLiveAlerts() {
    try {
      const res = await fetch('/api/alerts/live');
      const data = await res.json();
      const ticker = document.getElementById('ticker-content');
      if (ticker) {
        const alerts = data.alerts || [];
        ticker.textContent = alerts.length
          ? alerts.map(a => a.title).join('  •  ')
          : 'No critical global alerts at this time. All monitoring systems normal.';
      }
    } catch (e) {
      const ticker = document.getElementById('ticker-content');
      if (ticker) ticker.textContent = 'Alert feed unavailable — Check IMD, INCOIS for official updates';
    }
  },

  // ── Quick Tutor Widget ──────────────────────────────────────────
  async quickAsk() {
    const input = document.getElementById('quick-question');
    const lang = document.getElementById('quick-lang-select')?.value || 'en';
    const q = input?.value?.trim();
    if (!q || !input) return;
    input.value = '';

    const msgs = document.getElementById('quick-messages');
    if (msgs) {
      msgs.innerHTML += `<div class="tutor-msg user"><span class="msg-avatar"><i class="fa-solid fa-user" style="color:var(--accent-blue)"></i></span><div class="msg-bubble">${this.escHtml(q)}</div></div>`;
      msgs.innerHTML += `<div class="tutor-msg bot" id="quick-typing"><span class="msg-avatar"><i class="fa-solid fa-robot" style="color:var(--accent-purple)"></i></span><div class="msg-bubble"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div></div>`;
      msgs.scrollTop = msgs.scrollHeight;
    }

    try {
      const res = await fetch('/api/tutor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, lang, city: this.currentCity }),
      });
      const data = await res.json();
      const typing = document.getElementById('quick-typing');
      if (typing) typing.outerHTML = `<div class="tutor-msg bot"><span class="msg-avatar"><i class="fa-solid fa-robot" style="color:var(--accent-purple)"></i></span><div class="msg-bubble" style="white-space:pre-wrap">${this.escHtml(data.answer || '')}</div></div>`;
      if (msgs) msgs.scrollTop = msgs.scrollHeight;
    } catch (e) {
      const typing = document.getElementById('quick-typing');
      if (typing) typing.outerHTML = `<div class="tutor-msg bot"><span class="msg-avatar"><i class="fa-solid fa-robot" style="color:var(--accent-purple)"></i></span><div class="msg-bubble">Sorry, I couldn't process that. Please try again.</div></div>`;
    }
  },

  // ── Helpers ────────────────────────────────────────────────────
  showCurrentLoading() {
    const el = document.getElementById('current-weather-body');
    if (el) el.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Fetching weather…</p></div>';
  },

  showError(containerId, msg) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = `<div style="padding:2rem;text-align:center;color:var(--risk-orange)">${msg}</div>`;
  },

  escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
  },
};

document.addEventListener('DOMContentLoaded', () => WS.init());
