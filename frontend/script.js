const chat = document.getElementById('chat');
const input = document.getElementById('msg');
const sendBtn = document.getElementById('send');
const voiceBtn = document.getElementById('voice-btn');
const ttsToggle = document.getElementById('tts-toggle');
const listeningIndicator = document.getElementById('listening-indicator');
const voiceStatus = document.getElementById('voice-status');
const ttsStatus = document.getElementById('tts-status');

// Text-to-Speech and Speech Recognition Configuration
let ttsEnabled = false;
let isListening = false;
const synth = window.speechSynthesis;
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

// Configure Speech Recognition
recognition.continuous = false;
recognition.interimResults = true;
recognition.lang = 'en-US';

// J.A.R.V.I.S Response Database (Enhanced)
const responses = {
  greetings: {
    keywords: ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
    responses: [
      'J.A.R.V.I.S: Good day, sir. Systems fully operational.',
      'J.A.R.V.I.S: At your service, Boss. What can I do for you?',
      'J.A.R.V.I.S: Hello. How may I be of assistance?',
      'J.A.R.V.I.S: Greetings. Standing by for commands.'
    ]
  },
  help: {
    keywords: ['help', 'what can you do', 'commands', 'assist', 'capabilities', 'features'],
    responses: [
      'J.A.R.V.I.S: I can assist with:\n• Information queries\n• Task management\n• System status reports\n• Voice commands\n• General assistance',
      'J.A.R.V.I.S: I am programmed to help with various tasks. Simply ask away, sir.',
      'J.A.R.V.I.S: My capabilities include voice recognition, text processing, and intelligent response generation.'
    ]
  },
  status: {
    keywords: ['status', 'how are you', 'system check', 'diagnostics', 'condition'],
    responses: [
      'J.A.R.V.I.S: All systems operational, Boss. Ready for duty.',
      'J.A.R.V.I.S: Running at peak efficiency. What do you require?',
      'J.A.R.V.I.S: Systems nominal. All functions optimal.'
    ]
  },
  voice: {
    keywords: ['voice', 'microphone', 'listen', 'speak', 'voice command', 'speech'],
    responses: [
      'J.A.R.V.I.S: Voice recognition system active. Please speak clearly.',
      'J.A.R.V.I.S: Microphone engaged and listening for your commands, sir.'
    ]
  },
  tts: {
    keywords: ['speaker', 'audio', 'sound', 'text to speech', 'speak response', 'voice output'],
    responses: [
      'J.A.R.V.I.S: Text-to-speech system engaged. All responses will be vocalized.',
      'J.A.R.V.I.S: Audio output enabled. I shall now speak my responses.'
    ]
  },
  time: {
    keywords: ['time', 'what time', 'current time', 'hour', 'minute'],
    responses: [
      `J.A.R.V.I.S: The current time is ${new Date().toLocaleTimeString()}, sir.`,
      `J.A.R.V.I.S: It is currently ${new Date().toLocaleTimeString()}.`
    ]
  },
  default: {
    responses: [
      'J.A.R.V.I.S: Processing that request, sir. Fascinating.',
      'J.A.R.V.I.S: Acknowledged. Working on it now.',
      'J.A.R.V.I.S: Understood, Boss. Computing response.',
      'J.A.R.V.I.S: Very well. Analyzing your query.',
      'J.A.R.V.I.S: Indeed, sir. That is quite interesting.',
      'J.A.R.V.I.S: Noted. Processing your request.'
    ]
  }
};

// Get random response from array
function getRandomResponse(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Find matching category
function getJarvisResponse(userInput) {
  const input = userInput.toLowerCase();
  
  for (const [key, data] of Object.entries(responses)) {
    if (key === 'default') continue;
    if (data.keywords.some(keyword => input.includes(keyword))) {
      return getRandomResponse(data.responses);
    }
  }
  
  return getRandomResponse(responses.default.responses);
}

// Text-to-Speech Function
function speakResponse(text) {
  if (!ttsEnabled) return;
  
  // Cancel any ongoing speech
  synth.cancel();
  
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  utterance.lang = 'en-US';
  
  synth.speak(utterance);
}

// Add message to chat
function add(text, who) {
  const d = document.createElement('div');
  d.className = 'msg ' + who;
  d.innerText = text;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}

// Voice Input Handler
function startVoiceInput() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    add('J.A.R.V.I.S: Voice recognition not supported on this device.', 'ai');
    return;
  }
  
  isListening = true;
  voiceBtn.style.background = '#0f0';
  voiceStatus.textContent = '● ACTIVE';
  voiceStatus.className = 'on';
  listeningIndicator.classList.remove('listening-hidden');
  
  recognition.start();
}

recognition.onstart = () => {
  isListening = true;
};

recognition.onresult = (event) => {
  let transcript = '';
  
  for (let i = event.resultIndex; i < event.results.length; i++) {
    transcript += event.results[i][0].transcript;
  }
  
  if (event.results[event.results.length - 1].isFinal) {
    input.value = transcript;
    isListening = false;
    voiceBtn.style.background = '';
    voiceStatus.textContent = '○ LOCKED';
    voiceStatus.className = 'off';
    listeningIndicator.classList.add('listening-hidden');
    sendBtn.click();
  }
};

recognition.onerror = (event) => {
  add(`J.A.R.V.I.S: Error with voice input - ${event.error}`, 'ai');
  isListening = false;
  voiceBtn.style.background = '';
  voiceStatus.textContent = '○ LOCKED';
  voiceStatus.className = 'off';
  listeningIndicator.classList.add('listening-hidden');
};

recognition.onend = () => {
  isListening = false;
  voiceBtn.style.background = '';
  voiceStatus.textContent = '○ LOCKED';
  voiceStatus.className = 'off';
  listeningIndicator.classList.add('listening-hidden');
};

// Toggle Text-to-Speech
ttsToggle.onclick = () => {
  ttsEnabled = !ttsEnabled;
  ttsToggle.style.opacity = ttsEnabled ? '1' : '0.5';
  ttsStatus.textContent = ttsEnabled ? '● ACTIVE' : '○ LOCKED';
  ttsStatus.className = ttsEnabled ? 'on' : 'off';
  add(`J.A.R.V.I.S: Text-to-speech ${ttsEnabled ? 'enabled' : 'disabled'}, sir.`, 'ai');
};

// Voice Button Handler
voiceBtn.onclick = () => {
  if (!isListening) {
    startVoiceInput();
  }
};

// Handle send button click
sendBtn.onclick = () => {
  const t = input.value.trim();
  if (!t) return;
  
  add('YOU: ' + t, 'user');
  input.value = '';
  add('J.A.R.V.I.S: Processing...', 'ai');
  
  // Simulate processing delay
  setTimeout(() => {
    const response = getJarvisResponse(t);
    chat.lastChild.innerText = response;
    speakResponse(response);
  }, 800);
};

// Allow Enter key to send
input.onkeypress = (e) => {
  if (e.key === 'Enter') {
    sendBtn.click();
  }
};

// Initial greeting
add('J.A.R.V.I.S: Systems online. How may I assist you, Boss?', 'ai');
