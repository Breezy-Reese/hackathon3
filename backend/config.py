 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-for-hackathon-demo')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'quiz_app.db')
    
    # API Configuration
    HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')
    
    # Hugging Face Models Configuration
    HUGGING_FACE_MODELS = {
        'text_generation': 'gpt2',
        'question_answering': 'deepset/roberta-base-squad2',
        'text2text': 'google/flan-t5-base',
        'summarization': 'facebook/bart-large-cnn'
    }
    
    # Quiz Configuration
    MAX_QUESTIONS_PER_QUIZ = 10
    MIN_NOTES_LENGTH = 30
    MAX_NOTES_LENGTH = 5000
    DEFAULT_QUIZ_TYPE = 'mcq'
    
    # API Timeouts and Limits
    HUGGING_FACE_TIMEOUT = 30  # seconds
    MAX_API_RETRIES = 2
    
    # Database Configuration
    DB_CONNECTION_TIMEOUT = 30
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://127.0.0.1:5000']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production values
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Production database (could be PostgreSQL)
    DATABASE_URL = os.getenv('DATABASE_URL', Config.DATABASE_PATH)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# AI Model Configuration
class AIConfig:
    """AI-specific configuration"""
    
    # Recommended models for different tasks
    BEST_MODELS = {
        'mcq_generation': 'microsoft/DialoGPT-medium',
        'flashcard_generation': 'gpt2',
        'text_summarization': 'facebook/bart-large-cnn',
        'question_answering': 'deepset/roberta-base-squad2'
    }
    
    # Model parameters for different quiz types
    MCQ_GENERATION_PARAMS = {
        "max_new_tokens": 600,
        "temperature": 0.7,
        "do_sample": True,
        "top_p": 0.9,
        "return_full_text": False
    }
    
    FLASHCARD_GENERATION_PARAMS = {
        "max_new_tokens": 400,
        "temperature": 0.6,
        "do_sample": True,
        "return_full_text": False
    }
    
    # Fallback generation settings
    FALLBACK_ENABLED = True
    MIN_WORDS_PER_SENTENCE = 4
    EXCLUDED_WORDS = {
        'the', 'and', 'or', 'but', 'with', 'from', 'they', 'this', 'that', 
        'have', 'been', 'will', 'were', 'are', 'is', 'in', 'on', 'at', 
        'to', 'for', 'of', 'by', 'as', 'an', 'a', 'it', 'be', 'was'
    }

# Optional: IntaSend Configuration for monetization
class PaymentConfig:
    """Payment integration configuration"""
    
    INTASEND_PUBLISHABLE_KEY = os.getenv('INTASEND_PUBLISHABLE_KEY')
    INTASEND_SECRET_KEY = os.getenv('INTASEND_SECRET_KEY')
    INTASEND_TEST_MODE = os.getenv('INTASEND_TEST_MODE', 'true').lower() == 'true'
    
    # Pricing (in KES - Kenyan Shillings)
    PREMIUM_PRICE = 100  # 1 USD ≈ 100 KES
    QUIZ_CREDITS_FREE = 5
    QUIZ_CREDITS_PREMIUM = 50

# Logging Configuration
class LoggingConfig:
    """Logging configuration"""
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# Usage example:
if __name__ == "__main__":
    # Test configuration
    config_class = get_config()
    print(f"🔧 Configuration: {config_class.__name__}")
    print(f"🐛 Debug mode: {config_class.DEBUG}")
    print(f"🗄️  Database path: {config_class.DATABASE_PATH}")
    print(f"🤖 AI API configured: {bool(config_class.HUGGING_FACE_API_KEY)}")
    
    # Test AI config
    ai_config = AIConfig()
    print(f"🎯 Best MCQ model: {ai_config.BEST_MODELS['mcq_generation']}")
    print(f"📇 Best flashcard model: {ai_config.BEST_MODELS['flashcard_generation']}")
    
    print("✅ Configuration test complete!")