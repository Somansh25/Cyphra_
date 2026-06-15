#Cyphra Core Backend - Implements highly secure user authentication, file-backed identity clusters, and optimized regular expression intent parsing boundaries.

# Imports for system, regex, JSON handling, random selection, and time
import os
import re
import json
from dotenv import load_dotenv
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
from pymongo import MongoClient 


"""# Application configuration and environment-based secret keys
app = Flask(__name__)
app.secret_key = os.environ.get("CYPHRA_SECRET_KEY", "b3af9281cda1426ea9e1e55d5bb26cf4042617a2ee34")

# File path definitions and database connection URI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#RULES_FILE = os.path.join(BASE_DIR, 'rules.json')
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://cyphra_admin:CHih3HTF-2am6Hm@cyphra-prod.hb4os4r.mongodb.net/cyphra-prod?appName=cyphra-prod")
"""
# Application configuration utilizing strict environment injection
app = Flask(__name__)
load_dotenv()
# Retrieve secrets without fallback strings to prevent leaking credentials in source control
CYPHRA_SECRET = os.environ.get("CYPHRA_SECRET_KEY")
MONGO_URI_ENV = os.environ.get("MONGO_URI")

# Halt application execution if the execution environment is insecure
if not CYPHRA_SECRET or not MONGO_URI_ENV:
    raise RuntimeError(
        "CRITICAL CONFIGURATION ERROR: Both 'CYPHRA_SECRET_KEY' and 'MONGO_URI' "
        "environment variables must be set before launching this server."
    )

app.secret_key = CYPHRA_SECRET
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MONGO_URI = MONGO_URI_ENV

# Initialize database collection reference
users_collection = None
intents_collection = None
db_error = None

# Connect to MongoDB cluster with SSL certificate verification
try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client['cyphra-prod']
    users_collection = db['users']
    intents_collection = db['intents']
    print("MongoDB collections initialized successfully!")
    
    # AUTOMATIC ONE-TIME SEEDER: Pushes rules.json to MongoDB if database is empty
    if intents_collection.count_documents({}) == 0:
        print("Intents collection is empty. Migrating rules.json to MongoDB...")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        RULES_FILE = os.path.join(BASE_DIR, 'rules.json')
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Insert each intent dictionary as a separate document
                if "intents" in data and data["intents"]:
                    intents_collection.insert_many(data["intents"])
                    print(f"Successfully migrated {len(data['intents'])} intents to MongoDB!")
except Exception as e:
    db_error = str(e)
    app.logger.error(f"Critical Database Connectivity Interruption: {e}")
    
import threading

# Initialize a thread lock to control pipeline regeneration safety across concurrent requests
PIPELINE_LOCK = threading.Lock()

# Global cache for compiled intent regex patterns to improve response speed
COMPILED_PIPELINE = []

# Load chatbot intent and response rules from the MongoDB database
def load_conversational_rules():
    try:
        if intents_collection is not None:
            # Fetch all documents from the intents collection, excluding the MongoDB internal _id field
            intents_cursor = intents_collection.find({}, {"_id": 0})
            intents_list = list(intents_cursor)
            return {"intents": intents_list}
    except Exception as e:
        app.logger.error(f"Error streaming active conversational rules from MongoDB: {e}")
    return {"intents": []}

# Pre-compile intent regex patterns with word boundaries to optimize matching
def compile_optimized_intent_matrix():
    global COMPILED_PIPELINE
    COMPILED_PIPELINE = []
    raw_records = []

    # 1. Attempt to grab rules from cloud MongoDB via your loader
    try:
        raw_rules = load_conversational_rules()
        if raw_rules and raw_rules.get("intents"):
            raw_records = raw_rules.get("intents")
    except Exception as e:
        app.logger.warning(f"Cloud intelligence pipeline delayed or unreachable ({e}). Failing over...")

    # 2. Local Fallback Cache: If MongoDB took too long or failed, read from your local rules.json
    if not raw_records:
        try:
            local_path = os.path.join(BASE_DIR, 'rules.json')
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                    raw_records = local_data.get('intents', [])
                app.logger.info("Successfully fallback-loaded intent matrix out of local storage rules.json.")
        except Exception as local_err:
            app.logger.error(f"Failed to read local intent fallback data matrix: {local_err}")

    # Exit cleanly if completely empty across both data providers
    if not raw_records:
        app.logger.error("CRITICAL: No intents found in MongoDB or local rules.json. Chatbot will be unresponsive.")
        return []

    compiled_intents_pipeline = []
    
    # Loop through the records and compile patterns
    for intent_block in raw_records:
        pattern_regex_list = []
        for text_pattern in intent_block.get("text", []):
            if text_pattern.strip():
                # Uses word boundaries \b to ensure exact keyword matching
                regex_bound = re.compile(rf"\b{re.escape(text_pattern.lower().strip())}\b", re.IGNORECASE)
                pattern_regex_list.append(regex_bound)
                
        compiled_intents_pipeline.append({
            "intent": intent_block.get("intent"),
            "patterns": pattern_regex_list,
            "responses": intent_block.get("responses", []),
            "suggestions": intent_block.get("suggestions", [])
        })
    
    COMPILED_PIPELINE = compiled_intents_pipeline
    return COMPILED_PIPELINE

# Entry point route serving the unified application orchestrator
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to handle new user registration and password hashing
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        if users_collection is None:
            return jsonify({'success': False, 'message': 'Database connection not established.'}), 503
        
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        # Enforce length along with essential structural complexity requirements
        if (len(password) < 8 or 
            not any(char.isupper() for char in password) or 
            not any(char.isdigit() for char in password)):
            return jsonify({
                'success': False, 
                'message': 'Password complexity invalid. Ensure it is at least 8 characters long, '
                           'and contains both an uppercase character and a number.'
            }), 400
            
        if not email or not password or not name:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400
            
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already registered.'}), 409
            
        new_user_document = {
            'email': email,
            'name': name,
            'password': generate_password_hash(password)
        }
        users_collection.insert_one(new_user_document)
        
        session['user'] = email
        session['user_name'] = name
        return jsonify({'success': True, 'name': name}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Endpoint to verify user credentials and establish a session
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        if users_collection is None:
            return jsonify({'success': False, 'message': 'Database connection not established.'}), 503
        
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user_record = users_collection.find_one({'email': email})
        
        if user_record and check_password_hash(user_record['password'], password):
            session['user'] = email
            session['user_name'] = user_record['name']
            return jsonify({'success': True, 'name': user_record['name']}), 200
            
        return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Endpoint to clear the user session on logout
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200

# Endpoint to check the current authentication status of the user
@app.route('/api/auth/status', methods=['GET'])
def status():
    if 'user' in session:
        return jsonify({'logged_in': True, 'name': session.get('user_name', '')}), 200
    return jsonify({'logged_in': False}), 200

# Primary chat processing endpoint for message intent matching and response generation
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message or len(user_message) > 500:
            return jsonify({'bot_response': {'text': 'Empty message.'}}), 400
        
        # Resilience check with a double-checked locking mechanism for multi-threaded safety
        if not COMPILED_PIPELINE:
            with PIPELINE_LOCK:
                # Confirm the state did not alter while acquiring the thread lock barrier
                if not COMPILED_PIPELINE:
                    app.logger.info("Intent pipeline empty at runtime. Thread-safely compiling matrix...")
                    compile_optimized_intent_matrix()
        
        user_input_lower = user_message.lower()

        # Use explicit word boundaries (\b) to prevent mid-word substring matching
        if re.search(r'\btime\b', user_input_lower):
            res_text = f"The current time is: {datetime.now().strftime('%I:%M %p')}"
            return jsonify({'bot_response': {'text': res_text, 'carousel': []}, 'suggestions': ["Features"]}), 200

        elif re.search(r'\bdate\b', user_input_lower):
            res_text = f"Today's date is: {datetime.now().strftime('%B %d, %Y')}"
            return jsonify({'bot_response': {'text': res_text, 'carousel': []}, 'suggestions': ["Features"]}), 200        

        matched_intent = None
        
        # Iterate through compiled pipeline to find a matching regex pattern
        for intent_node in COMPILED_PIPELINE:
            if intent_node['intent'] == 'fallback': continue
            if any(pattern.search(user_message) for pattern in intent_node['patterns']):
                matched_intent = intent_node
                break
        
        # Fall back to default response if no specific intent matches
        if not matched_intent:
            matched_intent = next((i for i in COMPILED_PIPELINE if i['intent'] == 'fallback'), None)

        if matched_intent and matched_intent['responses']:
            selected_res = random.choice(matched_intent['responses'])
        else:
            selected_res = "I'm not sure how to help with that."

        # Format the response object for consistency in the frontend
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
    except Exception as e:
        app.logger.exception(f"Uncaught exception in chat pipeline processing: {e}")
        return jsonify({
            'bot_response': {
                'text': 'I encountered a temporary glitch. Please try again in a moment.', 
                'carousel': []
            },
            'suggestions': []
        }), 500

# Run pre-compilation of intents before starting the web server
#compile_optimized_intent_matrix()

if __name__ == '__main__':
    app.run(debug=True)
