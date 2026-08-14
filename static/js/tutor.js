// static/js/tutor.js — Multilingual AI Weather Tutor

const WeatherTutor = {
  currentLang: 'en',
  currentCity: '',
  messageCount: 0,
  isTyping: false,

  init() {
    this.bindEvents();
    this.initFromURL();
  },

  initFromURL() {
    const params = new URLSearchParams(window.location.search);
    const lang = params.get('lang') || 'en';
    const langSel = document.getElementById('tutor-lang');
    if (langSel) { langSel.value = lang; this.setLanguage(lang); }
  },

  bindEvents() {
    // Language select
    const langSel = document.getElementById('tutor-lang');
    if (langSel) langSel.addEventListener('change', e => this.setLanguage(e.target.value));

    // Apply settings button
    document.getElementById('btn-apply-settings')?.addEventListener('click', () => {
      this.applySettings();
    });

    // Send button
    document.getElementById('btn-send')?.addEventListener('click', () => this.sendMessage());

    // Enter key in textarea
    const ta = document.getElementById('chat-input');
    if (ta) {
      ta.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
      // Auto-resize
      ta.addEventListener('input', () => {
        ta.style.height = 'auto';
        ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
      });
    }

    // Clear chat
    document.getElementById('btn-clear-chat')?.addEventListener('click', () => this.clearChat());

    // Topic chips
    document.querySelectorAll('.topic-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const q = chip.dataset.q;
        const ta = document.getElementById('chat-input');
        if (ta) { ta.value = q; ta.dispatchEvent(new Event('input')); }
        this.sendMessage();
      });
    });

    // Language pill clicks
    document.querySelectorAll('.lang-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const code = pill.dataset.code;
        const langSel = document.getElementById('tutor-lang');
        if (langSel) { langSel.value = code; this.setLanguage(code); }
        // Highlight
        document.querySelectorAll('.lang-pill').forEach(p => p.style.background = '');
        pill.style.background = 'rgba(79,142,247,0.2)';
        pill.style.borderColor = 'var(--accent-blue)';
        pill.style.color = 'var(--accent-blue)';
      });
    });
  },

  setLanguage(lang) {
    this.currentLang = lang;
    const badge = document.getElementById('input-lang-badge');
    if (badge) {
      const code = lang.toUpperCase().slice(0, 5);
      badge.innerHTML = `<i class="fa-solid fa-language"></i> ${code}`;
    }
    const ta = document.getElementById('chat-input');
    if (ta) {
      const placeholders = {
        hi: 'मौसम के बारे में कोई भी सवाल पूछें…',
        ta: 'வானிலை பற்றி எதையும் கேளுங்கள்…',
        te: 'వాతావరణం గురించి ఏదైనా అడగండి…',
        kn: 'ಹವಾಮಾನದ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ…',
        ml: 'കാലാവസ്ഥയെക്കുറിച്ച് എന്തും ചോദിക്കൂ…',
        bn: 'আবহাওয়া সম্পর্কে যেকোনো প্রশ্ন করুন…',
        mr: 'हवामानाबद्दल काहीही विचारा…',
        gu: 'હવામાન વિશે કંઈ પણ પૂછો…',
        ar: 'اسأل أي شيء عن الطقس…',
        fr: 'Posez n\'importe quelle question météo…',
        es: 'Haz cualquier pregunta sobre el clima…',
        de: 'Stellen Sie eine Wetterfrage…',
        ja: '天気について何でも聞いてください…',
        'zh-cn': '询问任何天气问题…',
        ru: 'Задайте вопрос о погоде…',
      };
      ta.placeholder = placeholders[lang] || 'Ask a weather question in any language…';
    }
  },

  applySettings() {
    const lang = document.getElementById('tutor-lang')?.value || 'en';
    const city = document.getElementById('tutor-city')?.value?.trim() || '';
    this.setLanguage(lang);
    this.currentCity = city;

    // Show confirmation
    const btn = document.getElementById('btn-apply-settings');
    if (btn) { btn.innerHTML = '<i class="fa-solid fa-check"></i> Settings Applied!'; setTimeout(() => btn.innerHTML = '<i class="fa-solid fa-check"></i> Apply Settings', 2000); }

    // Add greeting message in new language
    this.addBotMessage(`Settings updated! I'll now respond in your selected language.${city ? ` Using weather context for ${city}.` : ''}`);
  },

  async sendMessage() {
    if (this.isTyping) return;
    const ta = document.getElementById('chat-input');
    const question = ta?.value?.trim();
    if (!question) return;

    ta.value = '';
    ta.style.height = 'auto';

    // Add user message
    this.addUserMessage(question);
    this.messageCount++;

    // Show typing indicator
    this.showTyping();

    try {
      const res = await fetch('/api/tutor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          lang: this.currentLang,
          city: this.currentCity,
        }),
      });
      const data = await res.json();
      this.hideTyping();

      if (data.error) {
        this.addBotMessage('Sorry, I encountered an error. Please try again.');
      } else {
        this.addBotMessage(data.answer, data.powered_by);
      }
    } catch (e) {
      this.hideTyping();
      this.addBotMessage('Connection error. Please check your internet and try again.');
    }
  },

  addUserMessage(text) {
    const msgs = document.getElementById('chat-messages');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = 'chat-msg user-msg';
    div.style.animation = 'msgFadeIn .3s ease';
    div.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-user" style="color:var(--accent-blue)"></i></div>
      <div class="msg-content">
        <div class="msg-bubble">${this.escHtml(text)}</div>
        <div class="msg-time">${this.getTime()}</div>
      </div>`;
    msgs.appendChild(div);
    this.scrollToBottom();
  },

  addBotMessage(text, source = '') {
    const msgs = document.getElementById('chat-messages');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = 'chat-msg bot-msg';
    div.style.animation = 'msgFadeIn .3s ease';
    // Format markdown-like text
    const formatted = this.formatText(text);
    div.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-robot" style="color:var(--accent-purple)"></i></div>
      <div class="msg-content">
        <div class="msg-bubble">${formatted}</div>
        <div class="msg-time">WeatherSense AI${source ? ' • ' + source : ''} • ${this.getTime()}</div>
      </div>`;
    msgs.appendChild(div);
    this.scrollToBottom();
  },

  showTyping() {
    this.isTyping = true;
    const msgs = document.getElementById('chat-messages');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = 'chat-msg bot-msg typing-indicator';
    div.id = 'typing-indicator';
    div.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-robot" style="color:var(--accent-purple)"></i></div>
      <div class="msg-content">
        <div class="msg-bubble">
          <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      </div>`;
    msgs.appendChild(div);
    this.scrollToBottom();
  },

  hideTyping() {
    this.isTyping = false;
    document.getElementById('typing-indicator')?.remove();
  },

  clearChat() {
    const msgs = document.getElementById('chat-messages');
    if (!msgs) return;
    msgs.innerHTML = `
      <div class="chat-msg bot-msg">
        <div class="msg-avatar"><i class="fa-solid fa-robot" style="color:var(--accent-purple)"></i></div>
        <div class="msg-content">
          <div class="msg-bubble">
            <strong>Chat cleared!</strong><br/><br/>
            I'm ready for your next weather question.<br/>
            Ask me anything about weather, climate, or safety!
          </div>
          <div class="msg-time">WeatherSense AI</div>
        </div>
      </div>`;
  },

  scrollToBottom() {
    const msgs = document.getElementById('chat-messages');
    if (msgs) setTimeout(() => msgs.scrollTop = msgs.scrollHeight, 50);
  },

  formatText(text) {
    return text
      // Bold: **text**
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Headers: # text
      .replace(/^### (.+)$/gm, '<h4 style="margin:.6rem 0 .3rem;color:var(--accent-blue)">$1</h4>')
      .replace(/^## (.+)$/gm, '<h3 style="margin:.6rem 0 .3rem;color:var(--accent-cyan)">$1</h3>')
      .replace(/^# (.+)$/gm, '<h3 style="margin:.6rem 0 .3rem;font-size:1rem">$1</h3>')
      // Tables: convert | table | to styled HTML
      .replace(/\|(.+)\|/g, (match) => {
        const cells = match.split('|').filter(c => c.trim() && !c.match(/^[-\s]+$/));
        if (!cells.length) return '';
        return '<div style="display:flex;gap:.5rem;margin:.2rem 0">' +
          cells.map(c => `<span style="background:rgba(255,255,255,.05);padding:.2rem .5rem;border-radius:4px;font-size:.8rem">${c.trim()}</span>`).join('') +
          '</div>';
      })
      // Bullet points
      .replace(/^[•·]\s+(.+)$/gm, '<div style="margin:.15rem 0;padding-left:.8rem;border-left:2px solid var(--accent-blue)">$1</div>')
      .replace(/^\*\s+(.+)$/gm, '<div style="margin:.15rem 0;padding-left:.8rem;border-left:2px solid var(--accent-blue)">$1</div>')
      // Newlines
      .replace(/\n{2,}/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  },

  escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  },

  getTime() {
    return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (window.PAGE === 'tutor') WeatherTutor.init();
});
