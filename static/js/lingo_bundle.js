// static/js/lingo_bundle.js — Integrated LingoSurvive Micro-Learning & Country Survival Suite

const LingoApp = {
  activeTab: 'survival-game',
  streakDays: 3,
  dailyGoalSeconds: 900, // 15 minutes
  elapsedSeconds: 320,
  timerInterval: null,
  isTimerRunning: false,
  
  // ── Survival Scenarios Data ──────────────────────────────────────
  countries: [
    {
      id: 'japan',
      name: 'Tokyo, Japan 🇯🇵',
      scenario: 'Typhoon Warning Alert',
      npc: 'Kenji (Station Manager)',
      dialogue: '避難指示が出ました。暴風雨に備えて地下街へ移動してください！',
      translation: 'An evacuation order has been issued. Please move to the underground mall for shelter!',
      options: [
        { text: 'どこが一番安全ですか？ (Where is the safest place?)', correct: true, feedback: 'Perfect! Kenji points you towards the underground shelter entrance.' },
        { text: 'タクシーを呼んでください (Call me a taxi)', correct: false, feedback: 'Taxis are suspended during extreme typhoon alerts!' },
        { text: 'ラーメンを食べたいです (I want to eat ramen)', correct: false, feedback: 'Not the right time for food during an emergency alert!' }
      ]
    },
    {
      id: 'france',
      name: 'Paris, France 🇫🇷',
      scenario: 'Heatwave Alert (Canicule)',
      npc: 'Sophie (Park Ranger)',
      dialogue: 'Attention, il fait 42°C! Buvez beaucoup d’eau et restez à l’ombre.',
      translation: 'Warning, it is 42°C! Drink plenty of water and stay in the shade.',
      options: [
        { text: 'Où est la fontaine d’eau la plus proche? (Where is the nearest water fountain?)', correct: true, feedback: 'Excellent! Sophie points to the cooling mist station.' },
        { text: 'Je veux courir un marathon (I want to run a marathon)', correct: false, feedback: 'Danger! Exercising in 42°C heat causes heatstroke.' }
      ]
    },
    {
      id: 'spain',
      name: 'Valencia, Spain 🇪🇸',
      scenario: 'Coastal Flash Flood (Gota Fría)',
      npc: 'Carlos (Lifeguard)',
      dialogue: '¡Alerta roja por oleaje y riadas! Aléjese de la playa de inmediato.',
      translation: 'Red alert for high waves and flash floods! Move away from the beach immediately.',
      options: [
        { text: '¡Comprendido! Subo a la zona alta (Understood! Heading to high ground)', correct: true, feedback: 'Safe move! You quickly ascend above the water level.' },
        { text: 'Voy a nadar un poco (I am going to swim)', correct: false, feedback: 'Rip tides and floodwaters are lethal!' }
      ]
    }
  ],

  // ── Signboard Decoder Items ─────────────────────────────────────
  signboards: [
    {
      symbol: '津波避難場所 🌊',
      foreignText: 'TSUNAMI EVACUATION SITE',
      location: 'Sendai Coastal Road',
      decoded: 'DESIGNATED HIGH-GROUND TSUNAMI REFUGE AREA — ELEVATION 25M'
    },
    {
      symbol: '熱中症警戒アラート ☀️',
      foreignText: 'HEATSTROKE SEVERE ALERT',
      location: 'Kyoto Central Plaza',
      decoded: 'EXTREME HEAT WARNING — SEEK HYDRATION & AIR CONDITIONING'
    },
    {
      symbol: 'Abris d’Urgence 🚨',
      foreignText: 'EMERGENCY SHELTER',
      location: 'Nice Promenade',
      decoded: 'COMMUNAL STORM RESCUE STATION & MEDICAL AID'
    }
  ],

  init() {
    this.initTimer();
    this.renderSurvivalGame();
    this.renderDecoder();
    this.renderPuzzles();
    this.bindEvents();
  },

  // ── 15-Min Daily Micro-Learning Timer ───────────────────────────
  initTimer() {
    this.updateTimerDisplay();
    const btnStart = document.getElementById('lingo-timer-toggle');
    if (btnStart) {
      btnStart.addEventListener('click', () => this.toggleTimer());
    }
  },

  toggleTimer() {
    if (this.isTimerRunning) {
      clearInterval(this.timerInterval);
      this.isTimerRunning = false;
      document.getElementById('lingo-timer-toggle').innerHTML = '<i class="fa-solid fa-play"></i> Resume 15-Min Session';
    } else {
      this.isTimerRunning = true;
      document.getElementById('lingo-timer-toggle').innerHTML = '<i class="fa-solid fa-pause"></i> Pause Session';
      this.timerInterval = setInterval(() => {
        this.elapsedSeconds++;
        this.updateTimerDisplay();
        if (this.elapsedSeconds >= this.dailyGoalSeconds) {
          clearInterval(this.timerInterval);
          this.isTimerRunning = false;
          alert('🎉 Congratulations! You completed your 15-Minute Daily Survival Learning Goal!');
        }
      }, 1000);
    }
  },

  updateTimerDisplay() {
    const pct = Math.min(100, Math.round((this.elapsedSeconds / this.dailyGoalSeconds) * 100));
    const remSec = Math.max(0, this.dailyGoalSeconds - this.elapsedSeconds);
    const mins = Math.floor(remSec / 60);
    const secs = remSec % 60;
    const timeStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    const txtPct = document.getElementById('lingo-timer-pct');
    const txtRem = document.getElementById('lingo-timer-rem');
    const ring = document.getElementById('lingo-timer-ring');

    if (txtPct) txtPct.textContent = `${pct}%`;
    if (txtRem) txtRem.textContent = `${timeStr} remaining`;
    if (ring) {
      const circumference = 2 * Math.PI * 80;
      const offset = circumference - (pct / 100) * circumference;
      ring.style.strokeDashoffset = offset;
    }
  },

  // ── Country Survival Game ───────────────────────────────────────
  renderSurvivalGame() {
    const container = document.getElementById('lingo-survival-card');
    if (!container) return;

    let currentIdx = 0;
    const renderScene = (idx) => {
      const item = this.countries[idx];
      container.innerHTML = `
        <div class="survival-scene-box">
          <div class="survival-header">
            <span class="badge-pill bg-accent">${item.name}</span>
            <span class="badge-pill bg-warning">${item.scenario}</span>
          </div>
          <div class="npc-chat-bubble">
            <div class="npc-avatar">👤 ${item.npc}</div>
            <p class="npc-quote">"${item.dialogue}"</p>
            <p class="npc-subtext"><i class="fa-solid fa-language"></i> Translation: ${item.translation}</p>
          </div>
          <div class="survival-options">
            <h4 style="font-size:0.9rem;color:#aaa;margin-bottom:0.6rem">Select your response:</h4>
            ${item.options.map((opt, oIdx) => `
              <button class="btn-survival-opt" data-correct="${opt.correct}" data-feedback="${opt.feedback}">
                ${opt.text}
              </button>
            `).join('')}
          </div>
          <div id="survival-feedback" class="survival-feedback-box" style="display:none"></div>
          <div style="margin-top:1rem;display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:0.8rem;color:#888">Scenario ${idx + 1} of ${this.countries.length}</span>
            <button id="btn-next-scenario" class="btn-primary-sm" style="display:none">Next Scenario <i class="fa-solid fa-arrow-right"></i></button>
          </div>
        </div>
      `;

      container.querySelectorAll('.btn-survival-opt').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const isCorrect = btn.dataset.correct === 'true';
          const feedback = btn.dataset.feedback;
          const fbBox = container.querySelector('#survival-feedback');
          const nextBtn = container.querySelector('#btn-next-scenario');

          btn.style.borderColor = isCorrect ? 'var(--success)' : 'var(--risk-red)';
          btn.style.background = isCorrect ? 'rgba(0, 200, 83, 0.15)' : 'rgba(255, 45, 45, 0.15)';
          fbBox.style.display = 'block';
          fbBox.style.color = isCorrect ? '#00C853' : '#FF2D2D';
          fbBox.innerHTML = `<strong>${isCorrect ? '✅ SUCCESS' : '❌ INCORRECT'}</strong>: ${feedback}`;
          
          if (isCorrect) {
            nextBtn.style.display = 'inline-block';
            this.elapsedSeconds += 60; // Bonus time credit
            this.updateTimerDisplay();
          }
        });
      });

      const nextBtn = container.querySelector('#btn-next-scenario');
      if (nextBtn) {
        nextBtn.addEventListener('click', () => {
          currentIdx = (currentIdx + 1) % this.countries.length;
          renderScene(currentIdx);
        });
      }
    };

    renderScene(0);
  },

  // ── Neural Signboard Decoder ───────────────────────────────────
  renderDecoder() {
    const card = document.getElementById('lingo-decoder-card');
    if (!card) return;

    let currentIdx = 0;
    const render = () => {
      const item = this.signboards[currentIdx];
      card.innerHTML = `
        <div class="decoder-box">
          <div class="decoder-symbol-display">${item.symbol}</div>
          <div class="decoder-meta">
            <span class="badge-pill bg-purple">${item.location}</span>
            <span class="badge-pill bg-dark">${item.foreignText}</span>
          </div>
          <div class="decoder-output-screen" id="decoder-screen">
            <i class="fa-solid fa-microchip fa-spin"></i> Neural AI Scanner Ready...
          </div>
          <div style="margin-top:1rem;display:flex;gap:0.75rem">
            <button id="btn-run-decoder" class="btn-primary" style="flex:1"><i class="fa-solid fa-wand-magic-sparkles"></i> Decode Signboard</button>
            <button id="btn-next-sign" class="btn-secondary"><i class="fa-solid fa-forward"></i> Next Sign</button>
          </div>
        </div>
      `;

      card.querySelector('#btn-run-decoder').addEventListener('click', () => {
        const screen = card.querySelector('#decoder-screen');
        screen.innerHTML = `<span style="color:var(--accent-blue)"><i class="fa-solid fa-spinner fa-spin"></i> Scanning OCR & Weather Neural Dictionary...</span>`;
        setTimeout(() => {
          screen.innerHTML = `<div style="color:var(--success)"><i class="fa-solid fa-circle-check"></i> <strong>DECODED:</strong><br/>"${item.decoded}"</div>`;
          this.elapsedSeconds += 45;
          this.updateTimerDisplay();
        }, 1200);
      });

      card.querySelector('#btn-next-sign').addEventListener('click', () => {
        currentIdx = (currentIdx + 1) % this.signboards.length;
        render();
      });
    };

    render();
  },

  // ── Word & Weather Puzzles ──────────────────────────────────────
  renderPuzzles() {
    const card = document.getElementById('lingo-puzzle-card');
    if (!card) return;

    card.innerHTML = `
      <div class="puzzle-box">
        <h4 style="color:#fff;margin-bottom:0.5rem"><i class="fa-solid fa-puzzle-piece" style="color:var(--accent-cyan)"></i> Emergency Weather Term Match</h4>
        <p style="font-size:0.85rem;color:#aaa;margin-bottom:1rem">Drag or click to match foreign storm terms with safety actions:</p>
        <div class="puzzle-grid">
          <div class="puzzle-chip" data-match="tsunami">避難場所 (Evacuation)</div>
          <div class="puzzle-chip" data-match="heat">Canicule (Heatwave)</div>
          <div class="puzzle-chip" data-match="rain">Gota Fría (Heavy Rain)</div>
        </div>
        <div id="puzzle-status" style="margin-top:1rem;font-size:0.85rem;color:var(--accent-cyan)">
          Tap terms to solve puzzles and unlock passport badges!
        </div>
      </div>
    `;

    card.querySelectorAll('.puzzle-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        chip.style.background = 'var(--accent-gradient)';
        chip.style.color = '#fff';
        document.getElementById('puzzle-status').innerHTML = `✨ Matched term <strong>${chip.textContent}</strong>! +30 Sec Goal Credit!`;
        this.elapsedSeconds += 30;
        this.updateTimerDisplay();
      });
    });
  },

  bindEvents() {
    // Secondary tab switcher inside Slide 6
    document.querySelectorAll('.lingo-subtab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.lingo-subtab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const target = btn.dataset.subtab;
        document.querySelectorAll('.lingo-subtab-content').forEach(c => c.style.display = 'none');
        const active = document.getElementById(`lingo-subtab-${target}`);
        if (active) active.style.display = 'block';
      });
    });
  }
};

window.LingoApp = LingoApp;

document.addEventListener('DOMContentLoaded', () => {
  LingoApp.init();
});
