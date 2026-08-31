const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// Extended Response Database
const aiResponses = {
  greetings: {
    keywords: ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon'],
    responses: [
      'Good day, sir. Systems fully operational.',
      'At your service, Boss. What can I do for you?',
      'Hello. How may I be of assistance?'
    ]
  },
  help: {
    keywords: ['help', 'what can you do', 'commands', 'capabilities'],
    responses: [
      'I can assist with:\n• Information queries\n• Task management\n• System status reports\n• Voice recognition\n• General assistance',
      'I am programmed to help with various tasks. Simply ask away, sir.'
    ]
  },
  status: {
    keywords: ['status', 'system check', 'diagnostics'],
    responses: [
      'All systems operational, Boss. Ready for duty.',
      'Running at peak efficiency. What do you require?'
    ]
  },
  weather: {
    keywords: ['weather', 'temperature', 'forecast', 'rain', 'sunny'],
    responses: [
      'I regret that weather data access is currently restricted, sir.',
      'Weather information requires external API connectivity.'
    ]
  },
  time: {
    keywords: ['time', 'current time', 'hour'],
    responses: [
      `The current time is ${new Date().toLocaleTimeString()}, sir.`,
      `It is currently ${new Date().toLocaleTimeString()}.`
    ]
  },
  default: {
    responses: [
      'Processing that request, sir. Fascinating.',
      'Acknowledged. Working on it now.',
      'Understood, Boss. Computing response.',
      'Very well. Analyzing your query.'
    ]
  }
};

// Helper function to get random response
function getRandomResponse(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Helper function to match response
function getResponse(userInput) {
  const input = userInput.toLowerCase();
  
  for (const [key, data] of Object.entries(aiResponses)) {
    if (key === 'default') continue;
    if (data.keywords.some(keyword => input.includes(keyword))) {
      return getRandomResponse(data.responses);
    }
  }
  
  return getRandomResponse(aiResponses.default.responses);
}

// API Routes
app.post('/api/chat', (req, res) => {
  const { message } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'No message provided' });
  }
  
  const response = getResponse(message);
  
  res.json({
    success: true,
    userMessage: message,
    aiResponse: response,
    timestamp: new Date()
  });
});

app.post('/api/voice', (req, res) => {
  const { transcript } = req.body;
  
  if (!transcript) {
    return res.status(400).json({ error: 'No transcript provided' });
  }
  
  const response = getResponse(transcript);
  
  res.json({
    success: true,
    transcript: transcript,
    aiResponse: response,
    timestamp: new Date()
  });
});

app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    version: '1.0.0',
    features: ['text-chat', 'voice-input', 'text-to-speech'],
    timestamp: new Date()
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`J.A.R.V.I.S Server running on port ${PORT}`);
  console.log(`Visit http://localhost:${PORT} to access the interface`);
});
