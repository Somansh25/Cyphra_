# Cyphra - Dynamic Conversational Architecture

Cyphra is a sophisticated, conversational platform engineered with a Python Flask backend and a reactive, frontend. It leverages a custom-built, compiled regular expression engine to deliver low-latency, context-aware responses driven by a modular JSON intelligence matrix, supported by secure cloud-based identity management.

## Tech Stack

- **Backend:** Python / Flask
- **Database:** MongoDB Atlas (Cloud Persistence)
- **Frontend:** Vanilla JavaScript (ES6+), CSS3 (Architectural Design System), HTML5
- **Authentication:** Werkzeug Security (PBKDF2 with SHA-256)
- **Intelligence:** Regex-based Intent Pipeline

## Features

-  **Intelligent Pattern Matching:** Utilizes compiled word-boundary regular expressions for high-precision intent detection.
-  **Dynamic View Orchestration:** A seamless interface that switches between landing, workspace, and help views without full page reloads.
-  **Enterprise Cloud Identity:** Integrated MongoDB Atlas support via `pymongo` for secure user registration, hashed credential storage, and real-time session validation.
-  **Adaptive UI Docking:** A unique chat interface that dynamically rebinds itself between a floating widget and a structural dashboard workspace.
-  **Rich Media Responses:** Support for multi-card carousels, suggestion chips, and real-time temporal queries (Time/Date).
-  **Modern Aesthetic:** A sleek "Corporate Architectural" design system using CSS variables, glassmorphism, and fluid animations.
-  **Security-First Design:** Implements XSS sanitization, CSRF protection concepts, and cryptographically secure session management.

## Project Structure

```
cyphra-chatbot/
├── app.py                 # Core Flask backend & API orchestration
├── rules.json             # Intent-response intelligence matrix (JSON)
├── requirements.txt       # Python environment dependencies
├── README.md              # Project documentation and deep-dive
├── .env                   # Environment variables
├── templates/
│   └── index.html         # Unified single-page application template
└── static/
    ├── css/
    │   └── style.css      # Architectural design system & UI styling
    ├── js/
    │   └── script.js      # Frontend state control & chat logic
    ├── audio/             # Interface notification soundscapes
    │   ├── error-sound.mp3
    │   ├── success-sound.mp3
    │   ├── info-sound.mp3 
    │   └── warning-sound.mp3
    └── images/            # Brand assets & UI iconography
        ├── favicon.png
        ├── logo.png       # Primary bot launcher icon
        └── logo1.png      # Navigation branding asset

```

##  Technical Deep-Dive

### Intent Processing Pipeline
Unlike simple keyword matching, Cyphra uses a **Compiled Pipeline**. On startup, the backend transforms the `rules.json` patterns into strict word-boundary regular expressions (`\bpattern\b`). This prevents false positives and ensures high-speed matching during the request lifecycle.

### Security Layer
- **Password Security:** Utilizes the Werkzeug security subsystem for salted hashing (Scrypt/PBKDF2) of user credentials.

### UI Architecture
The CSS framework uses a **Corporate Architectural Color System Matrix**, utilizing CSS variables for theme consistency. It features:
- Glassmorphism (`backdrop-filter`) for the navigation and modals.

##  Prerequisites

- Python 3.14+
- MongoDB Atlas Cluster (or local MongoDB instance)
- Modern Web Browser

##  Getting Started
Follow these steps to set up and run the Cyphra platform locally.

### 1. Clone the Repository
    ```bash
    git clone https://github.com/Somansh25/Cyphra_.git
    cd cyphra-chatbot
    ```

### 2. Set Up Python Virtual Environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # venv\Scripts\activate on Windows
    ```

### 3. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```

### 4. Configure Environment Variables
   Create a `.env` file in the root directory of your project. This file will store sensitive information and configuration settings.
   ```env
   CYPHRA_SECRET_KEY=your_very_long_and_secure_random_string
   MONGO_URI=mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority
   ```
   -   **`CYPHRA_SECRET_KEY`**: Replace `your_very_long_and_secure_random_string` with a strong, randomly generated key. This is crucial for session security. You can generate one using Python: `import os; os.urandom(24).hex()`.
   -   **`MONGO_URI`**: Obtain your MongoDB Atlas connection string. Ensure you replace `<username>`, `<password>`, `<cluster-name>`, and `<database-name>` with your actual MongoDB Atlas credentials and cluster details. The `cyphra-prod` database and `users` collection will be used by default.

### 5. Customize Conversational Intelligence
   Edit the `rules.json` file to define your chatbot's intents, patterns, and responses. This is where you configure the bot's conversational capabilities.

### 6. Run the Application
   Start the Flask development server:
    ```bash
    python app.py
    ```
   The application will typically run on `http://localhost:5000`.

### 7. Access Cyphra
   Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```
   You can now interact with the Cyphra chatbot, register new users, and explore its features.

##  Core Workflow

1. **Request:** The user sends a message via the **Unified Application Interface**.
2. **Processing:** The Flask `/chat` route intercepts the request, runs temporal checks (like time-based queries), and then iterates through the `COMPILED_PIPELINE`.
3. **Contextual Response:** If an intent matches, a random response is selected. The system supports both plain strings and complex objects containing carousels and suggestion chips.
4. **Real-time Feedback:** The frontend provides immediate visual feedback via typing indicators and audio-cued toast notifications.

##  Intelligence Configuration
The bot's "brain" is decentralized. You can define complex responses including text and carousels:
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

## Author

Created as a learning project for understanding chatbots, Flask, and web development basics.
**Somansh Chauhan** - [GitHub](https://github.com/Somansh25) | [LinkedIn](https://www.linkedin.com/in/somanshchauhan/)

---
**Cyphra** - Modernizing rule-based conversational interfaces.
