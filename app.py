#Cyphra Core Backend - Implements highly secure user authentication, file-backed identity clusters, and optimized regular expression intent parsing boundaries.

# Imports for system, regex, JSON handling, random selection, and time
import os
import re
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
from pymongo import MongoClient 

# Application configuration and environment-based secret keys
app = Flask(__name__)
app.secret_key = os.environ.get("CYPHRA_SECRET_KEY", "b3af9281cda1426ea9e1e55d5bb26cf4042617a2ee34")

# File path definitions and database connection URI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#RULES_FILE = os.path.join(BASE_DIR, 'rules.json')
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://cyphra_admin:CHih3HTF-2am6Hm@cyphra-prod.hb4os4r.mongodb.net/cyphra-prod?appName=cyphra-prod")

# Initialize database collection reference
users_collection = None
intents_collection = None
db_error = None

# Connect to MongoDB cluster with SSL certificate verification
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
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
    
# Placeholder for user cluster initialization
def initialize_user_cluster():
    pass

# Retrieve all users from the database for the application's identity matrix
def load_authenticated_users():
    user_matrix = {}
    try:
        for user in users_collection.find():
            user_matrix[user['email']] = {
                'name': user['name'],
                'password': user['password']
            }
    except Exception as e:
        app.logger.error(f"Failed to fetch identity maps from cloud database: {e}")
    return user_matrix

# Update or insert user records into the persistent database storage
def save_authenticated_users(user_data_matrix):
    try:
        for email, details in user_data_matrix.items():
            users_collection.update_one(
                {'email': email},
                {
                    '$set': {
                        'name': details['name'],
                        'password': details['password']
                    }
                },
                upsert=True 
            )
        return True
    except Exception as e:
        app.logger.error(f"Failed to sync identity updates to cloud database: {e}")
        return False

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

# Global cache for compiled intent regex patterns to improve response speed
COMPILED_PIPELINE = []

# Pre-compile intent regex patterns with word boundaries to optimize matching
def compile_optimized_intent_matrix():
    raw_rules = load_conversational_rules()
    
    if not raw_rules.get("intents"):
        app.logger.error("CRITICAL: No intents found in MongoDB. Chatbot will be unresponsive.")
        return []

    compiled_intents_pipeline = []
    
    for intent_block in raw_rules.get("intents", []):
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
    
    global COMPILED_PIPELINE
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
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'}), 400
            
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
        
        # Resilience check for serverless environments
        global COMPILED_PIPELINE
        if not COMPILED_PIPELINE:
            app.logger.info("Intent pipeline empty at runtime. Re-attempting database compilation...")
            compile_optimized_intent_matrix()
        
        user_input_lower = user_message.lower()
        # Returns current time if query mentions 'time'
        if 'time' in user_input_lower:
            res_text = f"The current time is: {datetime.now().strftime('%I:%M %p')}"
            return jsonify({'bot_response': {'text': res_text, 'carousel': []}, 'suggestions': ["Features"]}), 200
        # Returns current date if query mentions 'date'
        elif 'date' in user_input_lower:
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
compile_optimized_intent_matrix()

if __name__ == '__main__':
    app.run(debug=True)
