from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sqlite3
import requests
import json
import re
import random
import html
import time
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Security: Set secure headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Rate limiting (simple in-memory for demo)
request_counts = {}

def rate_limit(max_requests=20, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            request_counts[client_ip] = [req_time for req_time in request_counts.get(client_ip, []) 
                                       if current_time - req_time < window]
            
            # Check rate limit
            if len(request_counts.get(client_ip, [])) >= max_requests:
                return jsonify({'success': False, 'error': 'Rate limit exceeded. Please wait a minute.'}), 429
            
            # Add current request
            request_counts.setdefault(client_ip, []).append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(text):
    """Sanitize user input to prevent XSS and injection"""
    if not text:
        return ""
    # HTML escape and clean
    text = html.escape(text.strip())
    # Remove potentially harmful patterns
    text = re.sub(r'[<>"\';]', '', text)
    return text

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Configuration
HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'quiz_app.db')

class AIQuizGenerator:
    """AI-powered quiz generator using Hugging Face models"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
    def generate_quiz(self, notes, quiz_type='mcq', num_questions=5):
        """Generate quiz questions using AI or fallback"""
        
        if not self.api_key:
            print("No API key, using fallback generation")
            return self._generate_fallback_quiz(notes, quiz_type, num_questions)
        
        try:
            if quiz_type == 'mcq':
                return self._generate_mcq_with_ai(notes, num_questions)
            else:
                return self._generate_flashcards_with_ai(notes, num_questions)
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_fallback_quiz(notes, quiz_type, num_questions)
    
    def _generate_mcq_with_ai(self, notes, num_questions):
        """Generate MCQ using Hugging Face"""
        
        prompt = f"""Based on the following study notes, create {num_questions} multiple choice questions.

Study Notes:
{notes}

Please format each question exactly like this:
QUESTION: [Clear question text]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]
CORRECT: [A or B or C or D]
---

QUESTION:"""

        try:
            # Use text generation model
            api_url = "https://api-inference.huggingface.co/models/gpt2"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 600,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    parsed_questions = self._parse_mcq_response(generated_text)
                    if parsed_questions:
                        return parsed_questions
            elif response.status_code == 503:
                print("Model is loading, using fallback")
            else:
                print(f"API response: {response.status_code}, {response.text}")
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
        
        # Fallback if AI fails
        return self._generate_fallback_quiz(notes, 'mcq', num_questions)
    
    def _generate_flashcards_with_ai(self, notes, num_questions):
        """Generate flashcards using AI"""
        
        prompt = f"""Create {num_questions} study flashcards from this content:

Content:
{notes}

Format each flashcard exactly like this:
Q: [Question]
A: [Answer]
---

Q:"""

        try:
            api_url = "https://api-inference.huggingface.co/models/gpt2"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 400,
                    "temperature": 0.6,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    parsed_questions = self._parse_flashcard_response(generated_text)
                    if parsed_questions:
                        return parsed_questions
            
        except Exception as e:
            print(f"Flashcard generation error: {e}")
        
        return self._generate_fallback_quiz(notes, 'flashcard', num_questions)
    
    def _parse_mcq_response(self, text):
        """Parse AI-generated MCQ text"""
        questions = []
        
        # Split by question markers
        blocks = re.split(r'QUESTION:', text)
        
        for block in blocks:
            try:
                lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
                
                if len(lines) < 6:
                    continue
                
                question_text = lines[0].strip()
                options = []
                correct_answer = 0
                
                # Extract options A, B, C, D
                for line in lines[1:5]:
                    if re.match(r'^[A-D]\)', line):
                        option = re.sub(r'^[A-D]\)\s*', '', line).strip()
                        options.append(option)
                
                # Find correct answer
                correct_line = next((line for line in lines if 'CORRECT:' in line.upper()), '')
                if correct_line:
                    correct_letter = correct_line.upper().split('CORRECT:')[-1].strip()
                    if correct_letter in ['A', 'B', 'C', 'D']:
                        correct_answer = ord(correct_letter) - ord('A')
                
                if len(options) == 4 and question_text:
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'correct_answer': correct_answer,
                        'type': 'mcq'
                    })
                    
            except Exception as e:
                print(f"Error parsing MCQ block: {e}")
                continue
        
        return questions
    
    def _parse_flashcard_response(self, text):
        """Parse AI-generated flashcard text"""
        questions = []
        
        # Split by Q: markers
        parts = re.split(r'\bQ:', text)
        
        for part in parts:
            try:
                lines = [line.strip() for line in part.strip().split('\n') if line.strip()]
                
                if len(lines) < 2:
                    continue
                
                question_text = lines[0].strip()
                answer_line = next((line for line in lines if line.startswith('A:')), '')
                
                if answer_line:
                    answer = answer_line.replace('A:', '').strip()
                    
                    if question_text and answer:
                        questions.append({
                            'question': question_text,
                            'answer': answer,
                            'type': 'flashcard'
                        })
                        
            except Exception as e:
                print(f"Error parsing flashcard: {e}")
                continue
        
        return questions
    
    def _generate_fallback_quiz(self, notes, quiz_type, num_questions):
        """Fallback quiz generation when AI is not available"""
        
        # Split notes into meaningful chunks
        sentences = [s.strip() for s in notes.split('.') if s.strip() and len(s.split()) > 4]
        questions = []
        
        for i, sentence in enumerate(sentences[:num_questions]):
            words = sentence.split()
            
            if quiz_type == 'mcq':
                # Create fill-in-the-blank MCQ
                if len(words) > 6:
                    # Find important words (exclude common words)
                    skip_words = {'the', 'and', 'or', 'but', 'with', 'from', 'they', 'this', 'that', 'have', 'been', 'will', 'were', 'are', 'is', 'in', 'on', 'at', 'to', 'for', 'of', 'by', 'as'}
                    important_words = [w for w in words if len(w) > 3 and w.lower() not in skip_words]
                    
                    if important_words:
                        key_word = random.choice(important_words)
                        question_text = sentence.replace(key_word, "______", 1)
                        
                        # Generate plausible wrong answers
                        wrong_options = []
                        
                        # Add variations of the word
                        if key_word.endswith('s') and len(key_word) > 3:
                            wrong_options.append(key_word[:-1])
                        else:
                            wrong_options.append(f"{key_word}s")
                        
                        if not key_word.lower().startswith('un'):
                            wrong_options.append(f"un{key_word.lower()}")
                        else:
                            wrong_options.append(key_word[2:])
                        
                        wrong_options.append(f"{key_word.lower()}_related")
                        
                        # Ensure we have exactly 4 options
                        options = [key_word] + wrong_options[:3]
                        random.shuffle(options)
                        correct_answer = options.index(key_word)
                        
                        questions.append({
                            'question': f"Fill in the blank: {question_text}",
                            'options': options,
                            'correct_answer': correct_answer,
                            'type': 'mcq'
                        })
            
            else:  # flashcard
                if len(words) > 5:
                    # Create meaningful question-answer pairs
                    if any(word in sentence.lower() for word in ['is', 'are', 'means', 'refers', 'defines']):
                        # Definition-style question
                        question = f"What is defined or described in this statement?"
                        answer = sentence
                    elif any(word in sentence.lower() for word in ['because', 'since', 'due to', 'causes']):
                        # Cause-effect question
                        question = f"What cause and effect relationship is described?"
                        answer = sentence
                    else:
                        # General comprehension question
                        question = f"What is the main concept explained here?"
                        answer = sentence
                    
                    questions.append({
                        'question': question,
                        'answer': answer,
                        'type': 'flashcard'
                    })
        
        # Ensure we have at least some questions
        if not questions and sentences:
            # Create at least one question from the content
            first_sentence = sentences[0]
            if quiz_type == 'mcq':
                questions.append({
                    'question': f"Based on your notes, which statement is correct?",
                    'options': [
                        first_sentence[:50] + "...",
                        "This is incorrect information",
                        "The opposite is true",
                        "This is partially correct"
                    ],
                    'correct_answer': 0,
                    'type': 'mcq'
                })
            else:
                questions.append({
                    'question': 'What is the key information from your notes?',
                    'answer': first_sentence,
                    'type': 'flashcard'
                })
        
        return questions

# Initialize database
def init_database():
    """Initialize SQLite database with required tables"""
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("Initializing database tables...")
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            content TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notes_id INTEGER,
            quiz_type TEXT NOT NULL CHECK(quiz_type IN ('mcq', 'flashcard')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (notes_id) REFERENCES notes (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT,
            explanation TEXT,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Create default user
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, email) 
        VALUES (1, 'demo_user', 'demo@example.com')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Database helper functions
def save_quiz_to_db(notes_content, quiz_data, quiz_type):
    """Save quiz to database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Save notes
        cursor.execute(
            "INSERT INTO notes (content, title) VALUES (?, ?)",
            (notes_content, f"Notes from {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        )
        notes_id = cursor.lastrowid
        
        # Save quiz
        cursor.execute(
            "INSERT INTO quizzes (notes_id, quiz_type) VALUES (?, ?)",
            (notes_id, quiz_type)
        )
        quiz_id = cursor.lastrowid
        
        # Save questions
        for question in quiz_data:
            options_json = json.dumps(question.get('options', []))
            
            if question['type'] == 'mcq':
                correct_answer_json = json.dumps(question.get('correct_answer', 0))
            else:
                correct_answer_json = json.dumps(question.get('answer', ''))
            
            cursor.execute(
                "INSERT INTO questions (quiz_id, question_text, question_type, options, correct_answer) VALUES (?, ?, ?, ?, ?)",
                (quiz_id, question['question'], question['type'], options_json, correct_answer_json)
            )
        
        conn.commit()
        conn.close()
        return quiz_id
        
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_quiz_history():
    """Get quiz history from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT q.id, q.quiz_type, q.created_at, n.title, 
                   COUNT(qu.id) as question_count,
                   substr(n.content, 1, 100) as content_preview
            FROM quizzes q
            JOIN notes n ON q.notes_id = n.id
            LEFT JOIN questions qu ON q.id = qu.quiz_id
            GROUP BY q.id
            ORDER BY q.created_at DESC
            LIMIT 10
        ''')
        
        history = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'type': row[1],
                'date': row[2],
                'title': row[3],
                'question_count': row[4],
                'preview': row[5] + '...' if len(row[5]) == 100 else row[5]
            }
            for row in history
        ]
        
    except Exception as e:
        print(f"Database error: {e}")
        return []

# Initialize AI generator
ai_generator = AIQuizGenerator(HUGGING_FACE_API_KEY)

# Routes
@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@rate_limit(max_requests=10, window=60)  # Max 10 quiz generations per minute
def generate_quiz():
    """Generate quiz from notes using AI"""
    try:
        data = request.get_json()
        
        if not data or 'notes' not in data:
            return jsonify({'success': False, 'error': 'No notes provided'}), 400
        
        # Sanitize input for security
        notes = sanitize_input(data['notes'])
        quiz_type = sanitize_input(data.get('quiz_type', 'mcq'))
        num_questions = min(int(data.get('num_questions', 5)), 10)  # Limit to 10 questions
        
        # Validate input length
        if len(notes) < 30:
            return jsonify({'success': False, 'error': 'Please provide more detailed notes (at least 30 characters)'}), 400
        
        if len(notes) > 5000:
            return jsonify({'success': False, 'error': 'Notes too long. Please limit to 5000 characters.'}), 400
        
        # Validate quiz type
        if quiz_type not in ['mcq', 'flashcard']:
            return jsonify({'success': False, 'error': 'Invalid quiz type'}), 400
        
        print(f"Generating {quiz_type} quiz with {num_questions} questions...")
        
        # Generate quiz using AI
        questions = ai_generator.generate_quiz(notes, quiz_type, num_questions)
        
        if not questions:
            return jsonify({'success': False, 'error': 'Failed to generate questions. Please try with different notes.'}), 500
        
        # Save to database
        quiz_id = save_quiz_to_db(notes, questions, quiz_type)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'quiz_id': quiz_id,
            'message': f'Successfully generated {len(questions)} {quiz_type} questions!',
            'generation_method': 'AI' if HUGGING_FACE_API_KEY else 'Fallback'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        print(f"Error in generate_quiz: {e}")
        return jsonify({'success': False, 'error': 'Internal server error. Please try again.'}), 500

@app.route('/quiz/<int:quiz_id>')
def get_quiz(quiz_id):
    """Retrieve a specific quiz by ID"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT qu.question_text, qu.question_type, qu.options, qu.correct_answer
            FROM questions qu
            WHERE qu.quiz_id = ?
            ORDER BY qu.id
        ''', (quiz_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({'success': False, 'error': 'Quiz not found'}), 404
        
        questions = []
        for row in rows:
            question = {
                'question': row[0],
                'type': row[1]
            }
            
            try:
                if row[1] == 'mcq':
                    question['options'] = json.loads(row[2]) if row[2] else []
                    question['correct_answer'] = json.loads(row[3]) if row[3] else 0
                else:
                    question['answer'] = json.loads(row[3]) if row[3] else ''
            except (json.JSONDecodeError, TypeError):
                # Handle cases where data isn't properly JSON encoded
                if row[1] == 'mcq':
                    question['options'] = ['Option 1', 'Option 2', 'Option 3', 'Option 4']
                    question['correct_answer'] = 0
                else:
                    question['answer'] = row[3] or 'No answer available'
            
            questions.append(question)
        
        return jsonify({
            'success': True,
            'questions': questions
        })
        
    except Exception as e:
        print(f"Error retrieving quiz: {e}")
        return jsonify({'success': False, 'error': 'Failed to retrieve quiz'}), 500

@app.route('/history')
def quiz_history():
    """Get quiz history"""
    try:
        history = get_quiz_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'success': False, 'error': 'Failed to get history'}), 500

@app.route('/api/test')
def test_api():
    """Test API endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'ai_available': bool(HUGGING_FACE_API_KEY),
        'database_path': DATABASE_PATH,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.now().isoformat(),
            'database_tables': table_count,
            'ai_configured': bool(HUGGING_FACE_API_KEY)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Replace the final if __name__ == '__main__': section with:
if __name__ == '__main__':
    print("🚀 Starting AI Quiz Generator...")
    init_database()
    
    if HUGGING_FACE_API_KEY:
        print("✅ AI features enabled")
    else:
        print("⚠️ Using fallback generation")
    
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)