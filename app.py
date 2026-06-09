#Cyphra Core Backend - Implements highly secure user authentication, file-backed identity clusters, and optimized regular expression intent parsing boundaries.
import os
import re
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Cryptographically sound session protection
app.secret_key = os.environ.get("CYPHRA_SECRET_KEY", "b3af9281cda1426ea9e1e55d5bb26cf4042617a2ee34")

# Strict workspace path derivations relative to module root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(BASE_DIR, 'rules.json')
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

def initialize_user_cluster():
    #Ensures the identity storage exists and handles permission errors gracefully.
    if not os.path.exists(USERS_FILE):
        try:
            # Ensure directory exists (useful for some deployment volumes)
            os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
            
            default_identity = {
                "somanshch875@gmail.com": {
                    "name": "Somansh Chauhan",
                    "password": generate_password_hash("password123")
                }
            }
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_identity, f, indent=4)
            app.logger.info("Identity persistence layer initialized successfully.")
        except PermissionError:
            app.logger.error("Critical: No write permissions for users.json. Check deployment environment.")
        except Exception as e:
            app.logger.error(f"Unexpected error during identity initialization: {e}")

initialize_user_cluster()

def load_authenticated_users():
    #Safely ingests persistent identity data records with validation.
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        app.logger.error(f"Failed to read identity configuration stream: {e}")
    return {}

def save_authenticated_users(user_data_matrix):
    #Commits updated authentication states directly to private storage maps.
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data_matrix, f, indent=4)
        return True
    except Exception as e:
        app.logger.error(f"Failed to write identity configuration state: {e}")
        return False

def load_conversational_rules():
    #Ingests intent mapping with a fallback to prevent pipeline crashes.
    try:
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        app.logger.error(f"Error streaming active conversational rules: {e}")
    return {"intents": []}

# Global cache for compiled intents to avoid disk I/O on every request
COMPILED_PIPELINE = []

def compile_optimized_intent_matrix():
    #Pre-compiles regex patterns for performance and validates intent structure.
    raw_rules = load_conversational_rules()
    
    if not raw_rules.get("intents"):
        app.logger.error("CRITICAL: No intents found in rules.json. Chatbot will be unresponsive.")
        return []

    compiled_intents_pipeline = []
    
    for intent_block in raw_rules.get("intents", []):
        pattern_regex_list = []
        for text_pattern in intent_block.get("text", []):
            if text_pattern.strip():
                # Rigid word boundaries to prevent false positives
                regex_bound = re.compile(rf"\b{re.escape(text_pattern.lower().strip())}\b", re.IGNORECASE)
                pattern_regex_list.append(regex_bound)
                
        compiled_intents_pipeline.append({
            "intent": intent_block.get("intent"),
            "patterns": pattern_regex_list,
            "responses": intent_block.get("responses", []),
            "suggestions": intent_block.get("suggestions", [])
        })
    
    global COMPILED_PIPELINE
    COMPILED_PIPELINE = compiled_intents_pipeline
    return COMPILED_PIPELINE

@app.route('/')
def index():
    #Renders primary modern interface layout canvas context.
    return render_template('index.html')

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    #Validates inputs and provisions a unique user credentials node inside storage.
    try:
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'}), 400
            
        if not email or not password or not name:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400
            
        user_matrix = load_authenticated_users()
        if email in user_matrix:
            return jsonify({'success': False, 'message': 'Email already registered.'}), 409
            
        user_matrix[email] = {
            'name': name,
            'password': generate_password_hash(password)
        }
        
        if save_authenticated_users(user_matrix):
            session['user'] = email
            session['user_name'] = name
            return jsonify({'success': True, 'name': name}), 201
        return jsonify({'success': False, 'message': 'Failed to save user.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user_matrix = load_authenticated_users()
        if email in user_matrix and check_password_hash(user_matrix[email]['password'], password):
            session['user'] = email
            session['user_name'] = user_matrix[email]['name']
            return jsonify({'success': True, 'name': user_matrix[email]['name']}), 200
            
        return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200

@app.route('/api/auth/status', methods=['GET'])
def status():
    if 'user' in session:
        return jsonify({'logged_in': True, 'name': session.get('user_name', '')}), 200
    return jsonify({'logged_in': False}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message or len(user_message) > 500:
            return jsonify({'bot_response': {'text': 'Empty message.'}}), 400

        user_input_lower = user_message.lower()
        # Quick temporal checks
        if 'time' in user_input_lower:
            res_text = f"The current time is: {datetime.now().strftime('%I:%M %p')}"
            return jsonify({'bot_response': {'text': res_text, 'carousel': []}, 'suggestions': ["Features"]}), 200
        elif 'date' in user_input_lower:
            res_text = f"Today's date is: {datetime.now().strftime('%B %d, %Y')}"
            return jsonify({'bot_response': {'text': res_text, 'carousel': []}, 'suggestions': ["Features"]}), 200
        

        matched_intent = None
        
        for intent_node in COMPILED_PIPELINE:
            if intent_node['intent'] == 'fallback': continue
            if any(pattern.search(user_message) for pattern in intent_node['patterns']):
                matched_intent = intent_node
                break
        
        if not matched_intent:
            matched_intent = next((i for i in COMPILED_PIPELINE if i['intent'] == 'fallback'), None)

        if matched_intent and matched_intent['responses']:
            selected_res = random.choice(matched_intent['responses'])
        else:
            selected_res = "I'm not sure how to help with that."

        # Standardize response for script.js
        if isinstance(selected_res, str):
            bot_response = {'text': selected_res, 'carousel': []}
        else:
            bot_response = {
                'text': selected_res.get('text', ''),
                'carousel': selected_res.get('carousel', [])
            }

        return jsonify({
            'user_message': user_message,
            'bot_response': bot_response,
            'suggestions': matched_intent.get('suggestions', []) if matched_intent else [],
            'timestamp': datetime.now().isoformat()
        }), 200
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON Structure Error: Your rules.json has a syntax error: {e}")
        return jsonify({'bot_response': {'text': 'System configuration error: Malformed rules.', 'carousel': []}}), 500
    except KeyError as e:
        app.logger.error(f"Data Schema Error: Missing expected key in rules.json: {e}")
        return jsonify({'bot_response': {'text': 'I encountered a data alignment issue.', 'carousel': []}}), 500
    except Exception as e:
        app.logger.exception("Uncaught exception in chat route")
        # In production, we hide the raw 'e' and show a friendly message
        # Change back to f'DEBUG: {e}' only during active dev
        return jsonify({
            'bot_response': {'text': 'I encountered a temporary glitch. Please try again in a moment.', 'carousel': []},
            'suggestions': []
        }), 500

if __name__ == '__main__':
    compile_optimized_intent_matrix()
    app.run(debug=True)
