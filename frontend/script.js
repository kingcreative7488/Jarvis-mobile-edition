// frontend/script.js
// J.A.R.V.I.S — minimal local assistant with speech recognition and TTS
(function(){
  const chat = document.getElementById('chat');
  const msgInput = document.getElementById('msg');
  const sendBtn = document.getElementById('send');
  const voiceBtn = document.getElementById('voice-btn');
  const ttsToggle = document.getElementById('tts-toggle');
  const listeningIndicator = document.getElementById('listening-indicator');
  const voiceStatus = document.getElementById('voice-status');
  const ttsStatus = document.getElementById('tts-status');

  let ttsEnabled = false;
  let recognition = null;

  // Initialize from localStorage
  function loadState(){
    try{
      const saved = JSON.parse(localStorage.getItem('jarvis_chat')||'{}');
      ttsEnabled = !!saved.ttsEnabled;
      if(saved.messages && Array.isArray(saved.messages)){
        saved.messages.forEach(m => addBubble(m.text, m.sender, false));
      }
    }catch(e){/*ignore*/}
    updateStatusUI();
  }

  function saveState(){
    const messages = Array.from(chat.querySelectorAll('.bubble')).map(b=>({
      text: b.textContent,
      sender: b.classList.contains('user')? 'user' : 'jarvis'
    }));
    localStorage.setItem('jarvis_chat', JSON.stringify({messages, ttsEnabled}));
  }

  function addBubble(text, sender='jarvis', save=true){
    const div = document.createElement('div');
    div.className = 'bubble ' + (sender==='user'? 'user' : 'jarvis');
    div.textContent = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    if(save) saveState();
  }

  function updateStatusUI(){
    voiceStatus.className = recognition && recognition._listening ? 'on' : (recognition? 'off' : 'off');
    voiceStatus.textContent = (recognition && recognition._listening) ? '● LISTENING' : '○ LOCKED';
    ttsStatus.className = ttsEnabled ? 'on' : 'off';
    ttsStatus.textContent = ttsEnabled ? '● ENABLED' : '○ LOCKED';
  }

  function speak(text){
    if(!('speechSynthesis' in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    // prefer a neutral voice
    const voices = speechSynthesis.getVoices();
    if(voices && voices.length) u.voice = voices.find(v=>/english|en-US/i.test(v.lang))||voices[0];
    u.pitch = 1; u.rate = 1;
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  }

  function processJarvis(input){
    const text = input.trim();
    if(!text) return;
    // Simple rule-based responses
    const lower = text.toLowerCase();
    let reply = "I\u2019m J.A.R.V.I.S — your mobile assistant. I heard: '"+text+"'.";
    if(/hello|hi|hey/.test(lower)) reply = 'Hello — how can I help you today?';
    else if(/time/.test(lower)) reply = 'The time is ' + new Date().toLocaleTimeString();
    else if(/date/.test(lower)) reply = 'Today is ' + new Date().toLocaleDateString();
    else if(/help|commands/.test(lower)) reply = "Try: 'time', 'date', 'hello', or ask me anything.";
    else if(/clear chat|clear/.test(lower)){
      chat.innerHTML = '';
      saveState();
      addBubble('Chat cleared.', 'jarvis');
      if(ttsEnabled) speak('Chat cleared');
      return;
    }
    addBubble(reply, 'jarvis');
    if(ttsEnabled) speak(reply);
  }

  function sendMessage(){
    const text = msgInput.value.trim();
    if(!text) return;
    addBubble(text, 'user');
    msgInput.value = '';
    processJarvis(text);
  }

  // Setup SpeechRecognition
  function setupRecognition(){
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if(!SR) return null;
    const r = new SR();
    r.lang = 'en-US';
    r.interimResults = false;
    r.maxAlternatives = 1;
    r._listening = false;
    r.onstart = ()=>{ r._listening = true; listeningIndicator.className = 'listening-visible'; updateStatusUI(); };
    r.onend = ()=>{ r._listening = false; listeningIndicator.className = 'listening-hidden'; updateStatusUI(); };
    r.onerror = (ev)=>{ console.warn('Speech recognition error', ev); r._listening=false; listeningIndicator.className='listening-hidden'; updateStatusUI(); };
    r.onresult = (ev)=>{
      const t = ev.results[0][0].transcript;
      msgInput.value = t;
      sendMessage();
    };
    return r;
  }

  // UI events
  sendBtn.addEventListener('click', sendMessage);
  msgInput.addEventListener('keydown', function(e){ if(e.key === 'Enter') sendMessage(); });

  voiceBtn.addEventListener('click', function(){
    if(!recognition){
      recognition = setupRecognition();
      if(!recognition){
        addBubble('Speech recognition not supported in this browser.', 'jarvis');
        return;
      }
    }
    if(recognition._listening){
      recognition.stop();
    }else{
      try{ recognition.start(); }catch(e){ console.warn(e); }
    }
    updateStatusUI();
  });

  ttsToggle.addEventListener('click', function(){ ttsEnabled = !ttsEnabled; updateStatusUI(); saveState(); if(ttsEnabled) addBubble('Text-to-speech enabled', 'jarvis'); });

  // expose a simple welcome message
  addBubble('J.A.R.V.I.S online. Type or press the microphone to speak.', 'jarvis');

  // initialize
  loadState();

})();
