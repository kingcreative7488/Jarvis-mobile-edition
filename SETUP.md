# J.A.R.V.I.S Mobile Edition - Setup Guide

## Quick Start (Frontend Only)

### Option 1: Direct Browser Access
1. Clone the repository:
   ```bash
   git clone https://github.com/kingcreative7488/Jarvis-mobile-edition.git
   ```

2. Navigate to the frontend directory:
   ```bash
   cd Jarvis-mobile-edition/frontend
   ```

3. Open `index.html` in your web browser:
   - Double-click the file, or
   - Right-click → Open With → Your browser

4. Start interacting with J.A.R.V.I.S!

### Option 2: Local Web Server
For better security (required for some features):

**Using Python 3:**
```bash
cd Jarvis-mobile-edition/frontend
python -m http.server 8000
```
Visit: `http://localhost:8000`

**Using Python 2:**
```bash
cd Jarvis-mobile-edition/frontend
python -m SimpleHTTPServer 8000
```

**Using Node.js (http-server):**
```bash
npm install -g http-server
cd Jarvis-mobile-edition/frontend
http-server -p 8000
```

**Using PHP:**
```bash
cd Jarvis-mobile-edition/frontend
php -S localhost:8000
```

---

## Full Setup (With Backend API)

### Prerequisites
- Node.js (v14.0.0 or higher)
- npm (comes with Node.js)
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kingcreative7488/Jarvis-mobile-edition.git
   cd Jarvis-mobile-edition
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   npm install
   ```

3. **Start the Backend Server**
   ```bash
   npm start
   ```
   
   You should see:
   ```
   J.A.R.V.I.S Server running on port 5000
   Visit http://localhost:5000 to access the interface
   ```

4. **Open in Browser**
   - Visit `http://localhost:5000`
   - The frontend will be served automatically

### Development Mode (with auto-reload)

Install nodemon for development:
```bash
npm install -g nodemon
```

Start the server with:
```bash
npm run dev
```

The server will automatically restart when you make changes.

---

## Voice Recognition Setup

### Enable Voice Input
1. Use a **Chromium-based browser** (Chrome, Edge, Opera)
2. Click the 🎤 microphone button
3. Grant microphone permissions when prompted
4. Speak clearly into your microphone

### Browser Permissions
- **Chrome/Edge**: Permission dialog appears on first use
- **Firefox**: Not supported (Web Speech API limitation)
- **Safari**: Limited support

### Microphone Troubleshooting
- Check that your microphone is working
- Verify browser microphone permissions in settings
- Allow HTTPS (required for production)
- Test microphone in other applications first

---

## Text-to-Speech Setup

### Enable Audio Output
1. Click the 🔊 speaker button to toggle TTS
2. Status indicator should change to "● ACTIVE"
3. Responses will now be spoken aloud

### Audio Settings
- Adjust system volume before use
- Check browser audio settings
- Supported on Chrome, Firefox, Safari, Edge

### Customizing Voice
Edit `frontend/script.js` in the `speakResponse()` function:
```javascript
utterance.rate = 1.0;    // Speed: 0.1-10 (1.0 = normal)
utterance.pitch = 1.0;   // Pitch: 0-2 (1.0 = normal)
utterance.volume = 1.0;  // Volume: 0-1 (1.0 = maximum)
utterance.lang = 'en-US'; // Language (en-US, en-GB, etc.)
```

---

## Project Structure

```
Jarvis-mobile-edition/
│
├── frontend/                 # Frontend application
│   ├── index.html           # Main HTML file
│   ├── script.js            # Voice & chat logic
│   └── style.css            # Styling & animations
│
├── backend/                 # Backend server (optional)
│   ├── server.js            # Express API
│   ├── package.json         # Dependencies
│   └── node_modules/        # Installed packages
│
├── README.md                # Main documentation
├── SETUP.md                 # This file
└── .gitignore              # Git ignore rules
```

---

## Environment Configuration

### Backend Configuration
Set custom port (default: 5000):
```bash
PORT=3000 npm start
```

### Frontend Configuration
Modify `frontend/script.js` to change:
- Response database
- Voice recognition language
- TTS voice settings
- Chat styling

---

## Testing Features

### Test Text Chat
1. Type a greeting: "Hello"
2. Try help command: "What can you do?"
3. Ask for time: "What time is it?"

### Test Voice Input (Chrome/Edge only)
1. Click 🎤 microphone button
2. Say: "Hello J.A.R.V.I.S"
3. Watch transcript appear in input field

### Test Text-to-Speech
1. Enable TTS by clicking 🔊 speaker
2. Send any message
3. Listen to J.A.R.V.I.S speak the response

---

## Troubleshooting

### Issue: Voice button doesn't work
**Solution:**
- Use Chrome, Edge, or Opera (Firefox doesn't support Web Speech API)
- Check browser console for errors (F12)
- Verify microphone is connected and working
- Check browser permissions for microphone access

### Issue: TTS doesn't produce sound
**Solution:**
- Check system volume is turned up
- Enable TTS by clicking the 🔊 button
- Check browser audio settings
- Try a different browser

### Issue: Backend won't start
**Solution:**
```bash
# Check if Node.js is installed
node --version

# Check if npm is installed
npm --version

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Try a different port
PORT=3000 npm start
```

### Issue: Can't connect to localhost:5000
**Solution:**
- Ensure backend server is running (`npm start`)
- Check if port 5000 is already in use
- Try port 3000 instead: `PORT=3000 npm start`
- Check firewall settings

### Issue: Blank page or no styling
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh browser (Ctrl+F5)
- Check console for JavaScript errors (F12)
- Verify all files are in correct directories

---

## Performance Tips

1. **Voice Recognition**: Works best with clear speech
2. **TTS Quality**: Varies by browser and system TTS engine
3. **Chat Speed**: 800ms processing delay simulates thinking
4. **Mobile**: Responsive design works on all screen sizes
5. **Memory**: Clear browser cache periodically

---

## Security Considerations

1. **Microphone Access**: Only requested when needed
2. **Data Privacy**: All processing happens locally (no server uploads in default setup)
3. **HTTPS**: Required for production microphone access
4. **CORS**: Backend handles cross-origin requests safely

---

## Advanced Customization

### Add Custom Responses
Edit `backend/server.js` or `frontend/script.js`:
```javascript
customCategory: {
  keywords: ['trigger1', 'trigger2'],
  responses: [
    'Custom response 1',
    'Custom response 2'
  ]
}
```

### Change Color Scheme
Edit `frontend/style.css`:
- Default cyan: `#0ff`
- Default black: `#000`
- Text shadows, borders, animations

### Modify API Endpoints
Edit `backend/server.js`:
- Add new POST/GET routes
- Implement database storage
- Add authentication
- Connect external APIs

---

## Deployment

### Deploy Frontend Only (to GitHub Pages)
1. Push to GitHub
2. Go to repository settings
3. Enable GitHub Pages for `main` or `gh-pages` branch

### Deploy Backend (to Heroku)
1. Install Heroku CLI
2. `heroku create your-app-name`
3. Add `Procfile`:
   ```
   web: node backend/server.js
   ```
4. `git push heroku main`

### Deploy Full Stack (Vercel, Railway, etc.)
Consult platform-specific deployment guides.

---

## Support & Resources

- **Web Speech API Docs**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **Speech Synthesis API**: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
- **Express.js Docs**: https://expressjs.com/
- **GitHub Issues**: Report bugs and feature requests

---

## Next Steps

1. ✅ Test all features locally
2. ✅ Customize response database
3. ✅ Add more voice commands
4. ✅ Deploy to production
5. ✅ Gather user feedback
6. ✅ Implement advanced features

---

**Happy coding! J.A.R.V.I.S awaits your commands.** 🤖
