#  Cyphra Chatbot

A sophisticated rule-based chatbot built with Python Flask, HTML, CSS, and JavaScript. Cyphra utilizes pattern matching to deliver instant responses through a customizable, JSON-based intelligence engine.

## Features

-  **Intelligent Pattern Matching:** Case-insensitive substring matching for flexible conversations.
-  **Modern UI/UX:** Clean, gradient-based interface with smooth animations and responsive design.
-  Real-time chat interface
-  JSON-based rule configuration
-  Easy to customize and extend
-  No database required - JSON file-based

## Project Structure

```
cyphra-chatbot/
├── app.py                 # Flask backend application
├── rules.json             # Chatbot rules and responses
├── users.json             # Chatbot users
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # HTML template
└── static/
    ├── css/style.css         # CSS styling
    ├── js/script.js         # JavaScript for frontend
    ├── audio/
    |   ├── error-sound.mp3
    |   ├── success-sound.mp3
    |   ├── info-sound.mp3
    |   └── warning-sound.mp3
    └── images/
        ├── favicon.png
        ├── logo.png
        └── logo1.png

```

## Technical Deep-Dive

### Intent Processing Pipeline
Unlike simple keyword matching, Cyphra uses a **Compiled Pipeline**. On startup, the backend transforms the `rules.json` patterns into strict word-boundary regular expressions (`\bpattern\b`). This prevents false positives and ensures high-speed matching during the request lifecycle.

### Security Layer
- **XSS Sanitization:** The frontend uses programmatic DOM node creation and `textContent` binding to prevent cross-site scripting attacks from bot responses.
- **Session Protection:** Employs cryptographically sound secret keys for session cookie integrity.
- **Password Security:** Utilizes `PBKDF2` with SHA-256 iterations via `generate_password_hash`.

### UI Architecture
The CSS framework uses a **Corporate Architectural Color System Matrix**, utilizing CSS variables for theme consistency. It features:
- Glassmorphism (`backdrop-filter`) for the navigation and modals.
- Fluid viewport transitions and animations.
- A "Floating Widget" that can dynamically rebind its DOM parent to a "Dashboard Viewport" upon authentication.

## Installation & Setup

1. **Environment Setup:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # venv\Scripts\activate on Windows
    ```

2. **Dependencies:**
    ```bash
    pip install flask werkzeug
    ```

3. **Configuration:**
   The system will automatically initialize `users.json` with a default administrator account on first run.

4. **Execution:**
    ```bash
    python app.py
    ```

## Intelligence Configuration (rules.json)
The bot's "brain" is decentralized. You can define complex responses, including text and carousels:
```json
{
  "intent": "features",
  "text": ["what can you do", "features"],
  "responses": [
    {
      "text": "Cyphra offers...",
      "carousel": [
        {"title": "AI Engine", "description": "Contextual matching", "badge": "Core"}
      ]
    }
  ],
  "suggestions": ["Pricing", "Help"]
}
```

## Running the Chatbot

1. **Start the Flask application:**
   ```bash
   python app.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

3. **Start chatting!** Type your messages, and the chatbot will respond based on the predefined rules.

## How It Works

1. **Request:** User sends a message via the SPA interface.
2. **Processing:** The Flask `/chat` route intercepts the request, runs temporal checks (like time-based queries), and then iterates through the `COMPILED_PIPELINE`.
3. **Contextual Response:** If an intent matches, a random response is selected. If that response contains a `carousel`, it is rendered as a horizontal scrolling track in the UI.
4. **Dynamic UI:** Suggestion chips are automatically generated based on the matched intent to guide the user flow.

## Author

Created as a learning project for understanding chatbots, Flask, and web development basics.

---
**Cyphra** - Modernizing rule-based conversational interfaces.
