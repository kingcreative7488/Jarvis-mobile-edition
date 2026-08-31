# J.A.R.V.I.S Mobile Edition

A futuristic AI assistant interface with voice input, text-to-speech, and an immersive cyberpunk design inspired by Marvel's J.A.R.V.I.S.

## Features

### ✨ Core Features
- **Interactive Chat Interface** - Real-time conversation with intelligent response system
- **Voice Input** - Speak your commands using Web Speech API
- **Text-to-Speech** - Listen to J.A.R.V.I.S responses with TTS
- **System Status Dashboard** - Monitor AI Core, Network, Voice, TTS, and Memory states
- **Animated Core Visualization** - Spinning rings and pulsing center element
- **Mobile Responsive** - Fully optimized for mobile and desktop devices

### 🎙️ Voice Recognition
- Real-time speech-to-text conversion
- Supports continuous listening
- Visual feedback with listening indicator
- Error handling for unsupported browsers

### 🔊 Text-to-Speech
- Natural speech synthesis for AI responses
- Toggle button to enable/disable
- Customizable voice parameters (rate, pitch, volume)
- Interrupts previous speech for rapid interactions

### 🤖 AI Response System
- Intelligent keyword matching
- Multiple response categories:
  - Greetings
  - Help & Commands
  - System Status
  - Voice Commands
  - Time Queries
  - Default/General Responses
- Randomized responses for natural interaction

## Tech Stack

### Frontend
- **HTML5** - Semantic structure with accessibility features
- **CSS3** - Cyberpunk styling with animations
- **JavaScript (Vanilla)** - Web Speech API, Speech Synthesis API
- **No Dependencies** - Pure frontend solution

### Backend (Optional)
- **Node.js** - Runtime environment
- **Express.js** - Web framework
- **CORS** - Cross-origin resource sharing
- **Body-Parser** - JSON middleware

## Installation

### Frontend Only
1. Clone the repository:
```bash
git clone https://github.com/kingcreative7488/Jarvis-mobile-edition.git
cd Jarvis-mobile-edition
```

2. Open `frontend/index.html` in your browser

### With Backend Server
1. Install dependencies:
```bash
cd backend
npm install
```

2. Start the server:
```bash
npm start
```

3. Visit `http://localhost:5000` in your browser

## Usage

### Text Input
1. Type your message in the input field
2. Click "SEND" or press Enter
3. J.A.R.V.I.S will respond with appropriate reply

### Voice Input
1. Click the 🎤 microphone button
2. Speak your command clearly
3. Listen for the "LISTENING..." indicator
4. Your speech will be converted to text and sent automatically

### Text-to-Speech
1. Click the 🔊 speaker button to enable/disable
2. When enabled, J.A.R.V.I.S will speak all responses
3. Status indicator shows TTS is ACTIVE

## API Endpoints (Backend)

### POST /api/chat
Send a text message to J.A.R.V.I.S
```json
{
  "message": "Hello, J.A.R.V.I.S"
}
```

Response:
```json
{
  "success": true,
  "userMessage": "Hello, J.A.R.V.I.S",
  "aiResponse": "J.A.R.V.I.S: Good day, sir. Systems fully operational.",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### POST /api/voice
Send voice transcript
```json
{
  "transcript": "What time is it"
}
```

### GET /api/status
Check server and feature status
```json
{
  "status": "online",
  "version": "1.0.0",
  "features": ["text-chat", "voice-input", "text-to-speech"],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Response Categories

J.A.R.V.I.S recognizes the following command categories:

| Category | Keywords | Example |
|----------|----------|---------|
| **Greetings** | hello, hi, hey, greetings | "Hello J.A.R.V.I.S" |
| **Help** | help, what can you do, commands | "What can you do?" |
| **Status** | status, system check, diagnostics | "System status" |
| **Voice** | voice, microphone, speak | "Enable voice" |
| **TTS** | speaker, audio, text to speech | "Enable text to speech" |
| **Time** | time, what time, current time | "What time is it?" |

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| **Chat** | ✅ | ✅ | ✅ | ✅ |
| **Voice Input** | ✅ | ❌ | ❌ | ✅ |
| **Text-to-Speech** | ✅ | ✅ | ✅ | ✅ |

## Customization

### Add New Response Category
Edit `frontend/script.js`:
```javascript
const responses = {
  yourCategory: {
    keywords: ['keyword1', 'keyword2'],
    responses: [
      'J.A.R.V.I.S: Response one.',
      'J.A.R.V.I.S: Response two.'
    ]
  }
};
```

### Customize Styling
Modify `frontend/style.css` to change colors, fonts, and animations

### Change Voice Parameters
In `frontend/script.js`, adjust:
```javascript
utterance.rate = 1.0;    // Speed (0.1-10)
utterance.pitch = 1.0;   // Pitch (0-2)
utterance.volume = 1.0;  // Volume (0-1)
```

## Project Structure

```
Jarvis-mobile-edition/
├── frontend/
│   ├── index.html       # Main interface
│   ├── script.js        # Voice & chat logic
│   └── style.css        # Styling & animations
├── backend/
│   ├── server.js        # Express API
│   └── package.json     # Dependencies
└── README.md
```

## Future Enhancements

- [ ] Machine learning response generation
- [ ] User conversation history storage
- [ ] Custom voice parameters UI
- [ ] Multi-language support
- [ ] Database integration for context retention
- [ ] Advanced NLP for better understanding
- [ ] Mobile app with React Native
- [ ] Advanced animations and visual effects

## Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by Marvel's J.A.R.V.I.S from Iron Man
- Built with Web Speech API and Speech Synthesis API
- Cyberpunk design philosophy

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**J.A.R.V.I.S**: "At your service, Boss. Systems fully operational."
