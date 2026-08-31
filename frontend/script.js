const chat = document.getElementById('chat');
const input = document.getElementById('msg');
const sendBtn = document.getElementById('send');

// J.A.R.V.I.S Response Database
const responses = {
  greetings: {
    keywords: ['hello', 'hi', 'hey', 'greetings'],
    responses: [
      'J.A.R.V.I.S: Good day, sir. Systems fully operational.',
      'J.A.R.V.I.S: At your service, Boss. What can I do for you?',
      'J.A.R.V.I.S: Hello. How may I be of assistance?'
    ]
  },
  help: {
    keywords: ['help', 'what can you do', 'commands', 'assist'],
    responses: [
      'J.A.R.V.I.S: I can assist with:\n• Information queries\n• Task management\n• System status reports\n• General assistance',
      'J.A.R.V.I.S: I am programmed to help with various tasks. Simply ask away, sir.'
    ]
  },
  status: {
    keywords: ['status', 'how are you', 'system check'],
    responses: [
      'J.A.R.V.I.S: All systems operational, Boss. Ready for duty.',
      'J.A.R.V.I.S: Running at peak efficiency. What do you require?'
    ]
  },
  default: {
    responses: [
      'J.A.R.V.I.S: Processing that request, sir. Fascinating.',
      'J.A.R.V.I.S: Acknowledged. Working on it now.',
      'J.A.R.V.I.S: Understood, Boss. Computing response.',
      'J.A.R.V.I.S: Very well. Analyzing your query.',
      'J.A.R.V.I.S: Indeed, sir. That is quite interesting.'
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

// Add message to chat
function add(text, who) {
  const d = document.createElement('div');
  d.className = 'msg ' + who;
  d.innerText = text;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}

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
