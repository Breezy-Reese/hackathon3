 
# 🧠 AI Quiz Generator - Hackathon Project

Transform your study notes into interactive quizzes using AI! This app automatically generates multiple-choice questions and flashcards to help students learn more effectively.

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ installed
- Git installed
- Hugging Face account (free)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-quiz-generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 2: Get Hugging Face API Key

1. Go to [Hugging Face](https://huggingface.co/)
2. Sign up for a free account
3. Go to Settings → Access Tokens
4. Create a new token with "Read" permissions
5. Copy the token

### Step 3: Configure Environment

Create a `.env` file in the root directory:

```bash
HUGGING_FACE_API_KEY=your_actual_api_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### Step 4: Initialize Database

```bash
# Navigate to backend directory
cd backend

# Initialize the database
python ../database/init_db.py
```

### Step 5: Run the Application

```bash
# Start the Flask server (from backend directory)
python app.py
```

Open your browser and go to: `http://localhost:5000`

## 🧪 Testing Your App

### Test 1: Basic Functionality
1. Paste sample notes: "The mitochondria is the powerhouse of the cell. It produces ATP through cellular respiration. DNA is stored in the nucleus."
2. Select "Multiple Choice Questions"
3. Click "Generate Quiz"
4. Verify questions appear

### Test 2: Flashcards
1. Use the same notes
2. Select "Flashcards"
3. Generate and test navigation

### Test 3: API Endpoints
```bash
# Test health check
curl http://localhost:5000/health

# Test API status
curl http://localhost:5000/api/test
```

## 🎯 Features

- ✅ **AI-Powered Generation**: Uses Hugging Face models to create intelligent questions
- ✅ **Multiple Formats**: MCQ and Flashcard support
- ✅ **Local Database**: SQLite for storing quizzes and history
- ✅ **Responsive Design**: Works on mobile and desktop
- ✅ **Fallback System**: Works even without AI API
- ✅ **Quiz History**: Track previous generated quizzes

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: SQLite
- **AI**: Hugging Face Transformers API
- **Deployment**: Ready for Render/Replit

## 📁 Project Structure

```
ai-quiz-generator/
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── backend/
│   ├── app.py
│   └── requirements.txt
├── database/
│   ├── init_db.py
│   └── quiz_app.db
├── .env
└── README.md
```

## 🌐 Deployment Instructions

### Deploy to Render

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy!

### Deploy to Replit

1. Import GitHub repo to Replit
2. Add environment variables in Secrets tab
3. Run the app

## 🔑 Environment Variables

```bash
HUGGING_FACE_API_KEY=hf_xxxxxxxxxxxx
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'flask'"**
   - Make sure virtual environment is activated
   - Run: `pip install -r backend/requirements.txt`

2. **Database errors**
   - Run: `python database/init_db.py`
   - Check file permissions

3. **AI generation not working**
   - Verify Hugging Face API key in `.env`
   - App will use fallback generation automatically

4. **CORS errors**
   - Ensure Flask-CORS is installed
   - Check API_BASE_URL in frontend JavaScript

### Performance Tips

- Limit notes to 1000 characters for faster generation
- Use 3-5 questions for optimal performance
- Clear browser cache if seeing old data

## 🎯 Hackathon Demo Script

1. **Show Problem**: "Students struggle to create effective study materials"
2. **Demo Input**: Paste biology notes about cells
3. **Show AI Magic**: Watch questions generate automatically
4. **Test Quiz**: Answer some questions, show scoring
5. **Show History**: Display saved quizzes
6. **Highlight Impact**: "Saves hours of manual quiz creation"

## 🚀 Future Enhancements

- User authentication
- Export quizzes to PDF
- Spaced repetition algorithm
- Subject categorization
- Team collaboration features
- Advanced AI models (GPT-4, Claude)

## 📊 Metrics for Judges

- **Lines of Code**: ~500 (efficient!)
- **Setup Time**: 10 minutes
- **AI Response Time**: 3-10 seconds
- **Supported Note Length**: 50-2000 characters
- **Question Types**: 2 (MCQ, Flashcards)

## 🏆 Why This Project Wins

1. **Real Impact**: Solves actual student problems
2. **AI Integration**: Smart use of Hugging Face
3. **Low-Code Approach**: Simple, clean architecture
4. **Complete Solution**: Frontend + Backend + Database
5. **Scalable**: Ready for production deployment

---

**Built with ❤️ for [Hackathon Name]**