 
import sqlite3
import os

def create_database():
    """Create and initialize the SQLite database"""
    
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect('database/quiz_app.db')
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Notes table
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
    
    # Quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notes_id INTEGER,
            quiz_type TEXT NOT NULL CHECK(quiz_type IN ('mcq', 'flashcard')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (notes_id) REFERENCES notes (id)
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            options TEXT,  -- JSON string for MCQ options
            correct_answer TEXT,  -- JSON string
            explanation TEXT,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Create a default user for demo purposes
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, email) 
        VALUES (1, 'demo_user', 'demo@example.com')
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quizzes_notes_id ON quizzes(notes_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_quiz_id ON questions(quiz_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print("Tables created: users, notes, quizzes, questions")
    
def test_database():
    """Test database connection and basic operations"""
    try:
        conn = sqlite3.connect('database/quiz_app.db')
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n📊 Database Test Results:")
        print(f"Found {len(tables)} tables: {[table[0] for table in tables]}")
        
        # Test insert
        cursor.execute(
            "INSERT INTO notes (content, title) VALUES (?, ?)",
            ("Sample notes for testing", "Test Notes")
        )
        
        cursor.execute("SELECT COUNT(*) FROM notes")
        count = cursor.fetchone()[0]
        print(f"Notes table has {count} records")
        
        conn.commit()
        conn.close()
        
        print("✅ Database test passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    print("🚀 Initializing AI Quiz Generator Database...")
    create_database()
    test_database()
    print("\n🎯 Database setup complete! Ready to run the Flask app.")