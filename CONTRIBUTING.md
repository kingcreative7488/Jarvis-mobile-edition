# Contributing to J.A.R.V.I.S Mobile Edition

Thank you for your interest in contributing to J.A.R.V.I.S Mobile Edition! We welcome contributions from everyone. This guide will help you get started.

## Code of Conduct

Be respectful and constructive in all interactions with other contributors.

## How to Contribute

### 1. Fork the Repository
Click the "Fork" button on the GitHub repository page to create your own copy.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR-USERNAME/Jarvis-mobile-edition.git
cd Jarvis-mobile-edition
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/voice-improvements`
- `fix/chat-bug`
- `docs/api-documentation`

### 4. Make Your Changes

#### Frontend Changes
- Edit files in `frontend/` directory
- Test in multiple browsers (Chrome, Firefox, Safari, Edge)
- Ensure responsive design works on mobile
- Update documentation if needed

#### Backend Changes
- Edit files in `backend/` directory
- Test API endpoints with tools like Postman or cURL
- Ensure CORS headers are correct
- Document new endpoints in README

### 5. Test Your Changes

#### Frontend Testing
```bash
# Use a local web server
cd frontend
python -m http.server 8000
# Visit http://localhost:8000
```

#### Backend Testing
```bash
cd backend
npm install
npm start
# Visit http://localhost:5000
```

Test:
- [ ] Chat functionality works
- [ ] Voice input works (Chrome/Edge)
- [ ] Text-to-speech works
- [ ] All UI elements are responsive
- [ ] No console errors

### 6. Commit Your Changes
```bash
git add .
git commit -m "Add: Description of your changes"
```

Use clear commit messages:
- `Add: New feature description`
- `Fix: Bug fix description`
- `Docs: Documentation update`
- `Refactor: Code improvement`
- `Style: CSS/formatting changes`

### 7. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 8. Create a Pull Request
1. Go to the original repository on GitHub
2. Click "Compare & Pull Request"
3. Fill in the PR title and description
4. Describe what you changed and why
5. Reference any related issues with `#issue-number`

## Pull Request Guidelines

- **Title**: Clear and descriptive (e.g., "Add voice command support for volume control")
- **Description**: Explain the changes, why they were made, and any related issues
- **Tests**: Include evidence that you tested your changes
- **Documentation**: Update README or SETUP.md if behavior changes
- **Browser Testing**: Confirm it works on Chrome, Firefox, Safari, Edge
- **No Breaking Changes**: Ensure backward compatibility when possible

## Areas for Contribution

### High Priority
- [ ] Improve voice recognition accuracy
- [ ] Add more response categories
- [ ] Enhance TTS voice selection
- [ ] Database integration for conversation history
- [ ] User authentication system

### Medium Priority
- [ ] Multi-language support
- [ ] Additional animations
- [ ] Advanced NLP
- [ ] Mobile app version
- [ ] Dark/Light theme toggle

### Low Priority
- [ ] Code comments and documentation
- [ ] Performance optimization
- [ ] UI/UX improvements
- [ ] Browser compatibility testing

## Coding Standards

### JavaScript
```javascript
// Use descriptive variable names
const userMessage = input.value.trim();

// Comment complex logic
function processInput(text) {
  // Normalize and clean user input
  const cleaned = text.toLowerCase().trim();
  return cleaned;
}

// Use consistent indentation (2 spaces)
if (condition) {
  doSomething();
}
```

### CSS
```css
/* Use semantic class names */
.voice-btn-active {
  background: #0f0;
}

/* Group related styles */
.message {
  margin: 6px 0;
  padding: 6px;
  border-left: 2px solid #0ff;
}
```

### HTML
```html
<!-- Use semantic HTML -->
<button id="send" aria-label="Send message">SEND</button>

<!-- Proper indentation -->
<div class="container">
  <header>
    <h1>J.A.R.V.I.S</h1>
  </header>
</div>
```

## Commit Message Format

```
type: subject (50 chars or less)

Detailed description (72 chars per line)
- Bullet point 1
- Bullet point 2

Fixes #123
Related to #456
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Code refactoring
- `perf`: Performance
- `test`: Tests

## Documentation

When contributing:

1. **Update README.md** if adding new features
2. **Update SETUP.md** if changing installation/configuration
3. **Update CHANGELOG.md** with your changes
4. **Add inline comments** for complex code
5. **Document new API endpoints** with examples

## Reporting Issues

### Before Creating an Issue
- Search existing issues to avoid duplicates
- Check the README and SETUP.md for solutions
- Test in multiple browsers

### Issue Template
```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Browser: Chrome 120
- OS: Windows 11
- Backend: Yes/No
```

## Questions or Suggestions?

- Open a GitHub Discussion
- Create a GitHub Issue with the `question` label
- Check existing discussions first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make J.A.R.V.I.S Mobile Edition better. Thank you for helping! 🚀
