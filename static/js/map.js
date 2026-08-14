// static/js/map.js — Leaflet.js Interactive GeoJSON Weather Risk Map Controller

const WeatherMap = {
  indiaMap: null,
  worldMap: null,
  fullMap: null,
  currentView: 'india',
  currentData: [],
  currentGeoJSON: null,
  activeFilter: 'ALL',
  markersGroup: null,
  geojsonLayer: null,
  baseLayers: {},
  radarLayer: null,

  // ── Initialize Mini Maps (Dashboard) ──────────────────────────
  initMiniMaps() {
    this.initIndiaMiniMap();
    this.initWorldMiniMap();
  },

  initIndiaMiniMap() {
    const el = document.getElementById('india-mini-map');
    if (!el || this.indiaMap) return;
    this.indiaMap = L.map('india-mini-map', {
      center: [22.5937, 78.9629],
      zoom: 4,
      zoomControl: false,
      attributionControl: false,
      scrollWheelZoom: false,
    });
    this.addTileLayer(this.indiaMap);
    this.loadIndiaMapData(this.indiaMap);
  },

  initWorldMiniMap() {
    const el = document.getElementById('world-mini-map');
    if (!el || this.worldMap) return;
    this.worldMap = L.map('world-mini-map', {
      center: [20, 0],
      zoom: 2,
      zoomControl: false,
      attributionControl: false,
      scrollWheelZoom: false,
    });
    this.addTileLayer(this.worldMap);
    this.loadWorldMapData(this.worldMap);
  },

  // ── Full Map Page ──────────────────────────────────────────────
  initFullMap() {
    const el = document.getElementById('full-map');
    if (!el || this.fullMap) return;

    const params = new URLSearchParams(window.location.search);
    const initView = params.get('view') === 'world' ? 'world' : 'india';
    this.currentView = initView;

    this.fullMap = L.map('full-map', {
      center: initView === 'world' ? [20, 0] : [22.5937, 78.9629],
      zoom: initView === 'world' ? 3 : 5,
      zoomControl: false,
      attributionControl: true,
    });

    // Basemaps
    const darkTile = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    });
    const satTile = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles © Esri',
      maxZoom: 18,
    });

    darkTile.addTo(this.fullMap);
    this.baseLayers = { "Dark Canvas": darkTile, "Satellite": satTile };

    // Layers Group
    this.markersGroup = L.layerGroup().addTo(this.fullMap);

    // Zoom controls
    L.control.zoom({ position: 'bottomright' }).addTo(this.fullMap);

    if (initView === 'india') {
      document.getElementById('view-india')?.classList.add('active');
      document.getElementById('view-world')?.classList.remove('active');
      this.loadIndiaMapData(this.fullMap, true);
    } else {
      document.getElementById('view-world')?.classList.add('active');
      document.getElementById('view-india')?.classList.remove('active');
      this.loadWorldMapData(this.fullMap, true);
    }

    setTimeout(() => {
      if (this.fullMap) this.fullMap.invalidateSize();
    }, 200);

    // View toggle buttons
    document.getElementById('view-india')?.addEventListener('click', () => {
      this.switchMapView('india');
    });
    document.getElementById('view-world')?.addEventListener('click', () => {
      this.switchMapView('world');
    });

    // Refresh button
    document.getElementById('map-refresh')?.addEventListener('click', () => {
      this.switchMapView(this.currentView, true);
    });

    // Reset view button
    document.getElementById('map-reset')?.addEventListener('click', () => {
      if (this.currentView === 'india') {
        this.fullMap.flyTo([22.5937, 78.9629], 5, { duration: 1.2 });
      } else {
        this.fullMap.flyTo([20, 0], 3, { duration: 1.2 });
      }
    });

    // Layer Toggle Button (Satellite / Dark)
    document.getElementById('map-toggle-satellite')?.addEventListener('click', (e) => {
      if (this.fullMap.hasLayer(darkTile)) {
        this.fullMap.removeLayer(darkTile);
        this.fullMap.addLayer(satTile);
        e.currentTarget.classList.add('active');
      } else {
        this.fullMap.removeLayer(satTile);
        this.fullMap.addLayer(darkTile);
        e.currentTarget.classList.remove('active');
      }
    });

    // Risk Filter Pills
    document.querySelectorAll('#risk-filters .filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#risk-filters .filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.activeFilter = btn.dataset.filter;
        this.renderMapMarkers(this.fullMap, this.currentData, this.currentView === 'world' ? 'city' : 'state');
        if (this.currentGeoJSON && this.currentView === 'india') {
          this.renderGeoJSONChoropleth(this.fullMap, this.currentGeoJSON);
        }
      });
    });

    // Map Search Input
    const searchInput = document.getElementById('map-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', e => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
          this.renderMapMarkers(this.fullMap, this.currentData, this.currentView === 'world' ? 'city' : 'state');
          return;
        }
        const filtered = this.currentData.filter(item => item.name.toLowerCase().includes(query) || (item.country && item.country.toLowerCase().includes(query)));
        this.renderMapMarkers(this.fullMap, filtered, this.currentView === 'world' ? 'city' : 'state');
        if (filtered.length > 0) {
          this.fullMap.flyTo([filtered[0].lat, filtered[0].lon], 7, { duration: 1.2 });
        }
      });
    }
  },

  switchMapView(view, forceRefresh = false) {
    if (!this.fullMap) return;
    this.currentView = view;

    document.getElementById('view-india')?.classList.toggle('active', view === 'india');
    document.getElementById('view-world')?.classList.toggle('active', view === 'world');

    if (view === 'india') {
      this.fullMap.flyTo([22.5937, 78.9629], 5, { duration: 1.2 });
      this.loadIndiaMapData(this.fullMap, true);
    } else {
      if (this.geojsonLayer) {
        this.fullMap.removeLayer(this.geojsonLayer);
        this.geojsonLayer = null;
      }
      this.fullMap.flyTo([20, 0], 3, { duration: 1.2 });
      this.loadWorldMapData(this.fullMap, true);
    }
  },

  // ── Tile Layer ─────────────────────────────────────────────────
  addTileLayer(map) {
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);
  },

  // ── India Map Data (with GeoJSON Boundary Layer) ───────────────
  async loadIndiaMapData(map, showInfo = false) {
    const infoEl = document.getElementById('map-loading-info');
    if (infoEl) infoEl.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i> Fetching India state GeoJSON risks…';
    try {
      const res = await fetch('/api/map/india');
      const data = await res.json();
      
      const states = data.states || (Array.isArray(data) ? data : []);
      this.currentData = states;
      this.currentGeoJSON = data.geojson || null;
      this.updateCounts(this.currentData);

      if (map === this.fullMap && this.currentGeoJSON) {
        this.renderGeoJSONChoropleth(map, this.currentGeoJSON);
      }

      this.renderMapMarkers(map, this.currentData, 'state');
      if (infoEl) infoEl.innerHTML = `<i class="fa-solid fa-check text-success"></i> ${this.currentData.length} states GeoJSON monitored`;
    } catch (e) {
      if (infoEl) infoEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-warning"></i> Map update failed';
      console.error('India map error:', e);
    }
  },

  // ── Render High-Accuracy GeoJSON State Boundary Layer ─────────
  renderGeoJSONChoropleth(map, geojson) {
    if (this.geojsonLayer) {
      map.removeLayer(this.geojsonLayer);
    }

    const styleFeature = (feature) => {
      const props = feature.properties || {};
      const riskLevel = props.risk_level || 'GREEN';
      const isFiltered = this.activeFilter !== 'ALL' && riskLevel !== this.activeFilter;
      
      const riskColor = props.risk_color || '#00C853';

      return {
        fillColor: riskColor,
        weight: 2.5,
        opacity: 0.9,
        color: '#ffffff',
        dashArray: '2',
        fillOpacity: isFiltered ? 0.05 : 0.65
      };
    };

    const onEachFeature = (feature, layer) => {
      const p = feature.properties || {};
      const riskColor = p.risk_color || '#00C853';

      const tooltipContent = `
        <div class="state-tooltip">
          <strong>${p.name || 'State'}</strong> (${p.risk_label || 'SAFE'})<br/>
          <span>Max: ${p.temp_max ?? '--'}°C | Condition: ${p.condition || 'Clear'}</span>
        </div>`;
      
      layer.bindTooltip(tooltipContent, { sticky: true, className: 'ws-state-tooltip' });

      layer.on({
        mouseover: (e) => {
          const l = e.target;
          l.setStyle({
            weight: 4,
            color: '#00f2fe',
            fillOpacity: 0.75
          });
          l.bringToFront();
        },
        mouseout: (e) => {
          this.geojsonLayer.resetStyle(e.target);
        },
        click: (e) => {
          map.fitBounds(e.target.getBounds());
          layer.openPopup();
        }
      });

      const popupHTML = this.buildPopupHTML(p, 'state');
      layer.bindPopup(popupHTML, { maxWidth: 300, className: 'ws-popup-wrapper' });
    };

    this.geojsonLayer = L.geoJSON(geojson, {
      style: styleFeature,
      onEachFeature: onEachFeature
    }).addTo(map);
  },

  // ── World Map Data ─────────────────────────────────────────────
  async loadWorldMapData(map, showInfo = false) {
    const infoEl = document.getElementById('map-loading-info');
    if (infoEl) infoEl.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i> Fetching world city risks…';
    try {
      const res = await fetch('/api/map/world');
      const data = await res.json();
      this.currentData = data.cities || [];
      this.updateCounts(this.currentData);
      this.renderMapMarkers(map, this.currentData, 'city');
      if (infoEl) infoEl.innerHTML = `<i class="fa-solid fa-check text-success"></i> ${this.currentData.length} global cities loaded`;
    } catch (e) {
      if (infoEl) infoEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-warning"></i> World map error';
      console.error('World map error:', e);
    }
  },

  updateCounts(items) {
    const list = Array.isArray(items) ? items : [];
    const cntAll = document.getElementById('cnt-all');
    const cntRed = document.getElementById('cnt-red');
    const cntOrange = document.getElementById('cnt-orange');
    const cntYellow = document.getElementById('cnt-yellow');
    const cntGreen = document.getElementById('cnt-green');

    if (!cntAll) return;
    cntAll.textContent = list.length;
    if (cntRed) cntRed.textContent = list.filter(i => i && i.risk_level === 'RED').length;
    if (cntOrange) cntOrange.textContent = list.filter(i => i && i.risk_level === 'ORANGE').length;
    if (cntYellow) cntYellow.textContent = list.filter(i => i && i.risk_level === 'YELLOW').length;
    if (cntGreen) cntGreen.textContent = list.filter(i => i && i.risk_level === 'GREEN').length;
  },

  // ── Render Custom HTML Markers ──────────────────────────────────
  renderMapMarkers(map, items, type) {
    if (map !== this.fullMap) {
      map.eachLayer(layer => {
        if (layer instanceof L.CircleMarker || layer instanceof L.Marker) map.removeLayer(layer);
      });
      items.forEach(item => {
        const color = item.risk_color || '#00C853';
        L.circleMarker([item.lat, item.lon], {
          radius: 6, fillColor: color, color: color, weight: 1, fillOpacity: 0.7
        }).addTo(map);
      });
      return;
    }

    if (!this.markersGroup) return;
    this.markersGroup.clearLayers();

    const filtered = this.activeFilter === 'ALL'
      ? items
      : items.filter(i => i.risk_level === this.activeFilter);

    filtered.forEach(item => {
      const level = (item.risk_level || 'GREEN').toLowerCase();
      const riskColor = item.risk_color || '#00C853';
      const iconSign = item.icon || '☀️';
      const tempStr = (item.temp_max !== '--' && item.temp_max !== undefined) ? `${item.temp_max}°C` : '--';

      const pinHtml = `
        <div class="custom-map-pin ${level}" style="border-left: 3.5px solid ${riskColor}; box-shadow: 0 4px 15px ${riskColor}44;">
          <span class="pin-sign">${iconSign}</span>
          <span class="pin-name">${item.name}</span>
          <span class="pin-temp-pill" style="background:${riskColor}; color:#ffffff;">${tempStr}</span>
        </div>`;

      const icon = L.divIcon({
        className: 'ws-custom-div-icon',
        html: pinHtml,
        iconSize: [140, 32],
        iconAnchor: [70, 16],
      });

      const marker = L.marker([item.lat, item.lon], { icon: icon });
      const popupHTML = this.buildPopupHTML(item, type);
      marker.bindPopup(popupHTML, { maxWidth: 300, className: 'ws-popup-wrapper' });
      this.markersGroup.addLayer(marker);
    });
  },

  buildPopupHTML(item, type) {
    const riskColor = item.risk_color || '#00C853';
    const location = type === 'city'
      ? `${item.name}, ${item.country || ''}`
      : `${item.name}${item.coastal ? ' (Coastal Region)' : ''}`;
    return `
      <div class="ws-popup">
        <div class="ws-popup-header">
          <div class="ws-popup-title">${item.icon || '<i class="fa-solid fa-cloud"></i>'} ${location}</div>
          <span class="popup-risk" style="background:${riskColor}22;color:${riskColor};border:1px solid ${riskColor}44">
            ${item.risk_emoji || ''} ${item.risk_label || 'SAFE'}
          </span>
        </div>
        <div class="ws-popup-grid">
          <div class="popup-stat"><div class="popup-stat-label">Max / Min Temp</div><div class="popup-stat-val">${item.temp_max ?? '--'}° / ${item.temp_min ?? '--'}°C</div></div>
          <div class="popup-stat"><div class="popup-stat-label">Condition</div><div class="popup-stat-val">${item.condition || 'Clear'}</div></div>
          <div class="popup-stat"><div class="popup-stat-label">Wind Speed</div><div class="popup-stat-val">${item.wind ?? '--'} km/h</div></div>
          <div class="popup-stat"><div class="popup-stat-label">Rainfall</div><div class="popup-stat-val">${item.rain ?? '--'} mm</div></div>
        </div>
        <p style="color:${riskColor};font-size:.75rem;margin-bottom:.8rem;font-weight:600">${item.description || ''}</p>
        <a href="/forecast?city=${encodeURIComponent(item.name)}" class="btn-popup-cta">View 15-Day Detailed Forecast <i class="fa-solid fa-arrow-right"></i></a>
      </div>`;
  },

  // ── Tsunami Zone Map (Coastal Page) ────────────────────────────
  initTsunamiMap() {
    const el = document.getElementById('tsunami-map');
    if (!el) return;

    if (this.tsunamiMapInstance) {
      this.tsunamiMapInstance.remove();
      this.tsunamiMapInstance = null;
    }

    const tmap = L.map('tsunami-map', {
      center: [16.5, 80.5],
      zoom: 4,
      zoomControl: false,
      attributionControl: false,
    });
    this.tsunamiMapInstance = tmap;
    this.addTileLayer(tmap);

    const zones = [
      { name: 'Andaman & Nicobar Islands', lat: 11.74, lon: 92.66, risk: 'DANGER',  level: 'red',    color: '#FF2D2D', sign: '🔴 RED — VERY HIGH' },
      { name: 'Tamil Nadu Coast',           lat: 11.12, lon: 78.66, risk: 'WARNING', level: 'orange', color: '#FF8C00', sign: '🟠 ORANGE — HIGH' },
      { name: 'Andhra Pradesh Coast',       lat: 15.91, lon: 79.74, risk: 'WARNING', level: 'orange', color: '#FF8C00', sign: '🟠 ORANGE — HIGH' },
      { name: 'Odisha Coast',               lat: 20.95, lon: 85.09, risk: 'WARNING', level: 'orange', color: '#FF8C00', sign: '🟠 ORANGE — HIGH' },
      { name: 'West Bengal Coast',          lat: 22.99, lon: 87.86, risk: 'WARNING', level: 'orange', color: '#FF8C00', sign: '🟠 ORANGE — HIGH' },
      { name: 'Kerala Coast',               lat: 10.85, lon: 76.27, risk: 'CAUTION', level: 'yellow', color: '#FFD700', sign: '🟡 YELLOW — MODERATE' },
      { name: 'Maharashtra Coast',          lat: 19.75, lon: 75.71, risk: 'CAUTION', level: 'yellow', color: '#FFD700', sign: '🟡 YELLOW — MODERATE' },
      { name: 'Gujarat Coast',              lat: 22.26, lon: 71.19, risk: 'CAUTION', level: 'yellow', color: '#FFD700', sign: '🟡 YELLOW — MODERATE' },
      { name: 'Karnataka Coast',            lat: 15.32, lon: 74.50, risk: 'SAFE',    level: 'green',  color: '#00C853', sign: '🟢 GREEN — SAFE' },
      { name: 'Goa Coast',                  lat: 15.30, lon: 74.12, risk: 'SAFE',    level: 'green',  color: '#00C853', sign: '🟢 GREEN — SAFE' },
      { name: 'Lakshadweep Islands',        lat: 10.57, lon: 72.64, risk: 'SAFE',    level: 'green',  color: '#00C853', sign: '🟢 GREEN — SAFE' },
    ];

    zones.forEach(z => {
      // Outer translucent hazard ring
      L.circleMarker([z.lat, z.lon], {
        radius: z.level === 'red' ? 24 : z.level === 'orange' ? 18 : z.level === 'yellow' ? 14 : 10,
        fillColor: z.color,
        color: z.color,
        weight: 1.5,
        fillOpacity: 0.25,
      }).addTo(tmap);

      // Color Pin Marker
      const pinHtml = `<div class="tsunami-color-pin ${z.level}">${z.sign} | ${z.name}</div>`;
      const pinIcon = L.divIcon({
        className: 'ws-custom-div-icon',
        html: pinHtml,
        iconSize: [160, 28],
        iconAnchor: [80, 14]
      });

      L.marker([z.lat, z.lon], { icon: pinIcon })
        .bindPopup(`
          <div class="ws-popup">
            <h4><i class="fa-solid fa-water" style="color:#06b6d4"></i> ${z.name}</h4>
            <div style="margin-top:0.4rem; padding:0.3rem 0.6rem; border-radius:6px; background:${z.color}22; color:${z.color}; border:1px solid ${z.color}44; font-weight:700; font-size:0.8rem">
              Tsunami Hazard Level: ${z.risk} (${z.level.toUpperCase()} SIGN)
            </div>
            <p style="font-size:0.8rem; color:#aaa; margin-top:0.5rem">
              INCOIS Tsunami Early Warning Monitoring Center Active
            </p>
          </div>
        `)
        .addTo(tmap);
    });
  },
};

// Auto-init based on active tab
document.addEventListener('DOMContentLoaded', () => {
  const tab = window.ACTIVE_TAB || 'dashboard';
  if (tab === 'map' || document.getElementById('full-map')) {
    WeatherMap.initFullMap();
  }
  if (document.getElementById('tsunami-map')) {
    setTimeout(() => WeatherMap.initTsunamiMap(), 300);
  }
});
