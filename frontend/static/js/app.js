// Global variables for enhanced functionality
let currentQuiz = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let quizType = 'mcq';
let quizStartTime = null;
let questionTimes = [];

// API configuration with environment detection
const API_BASE_URL = window.location.origin;

// Enhanced analytics tracking
let appAnalytics = {
    quizzesGenerated: 0,
    questionsAnswered: 0,
    averageScore: 0,
    timeSpentLearning: 0
};

// Initialize the app with performance monitoring
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI Quiz Generator initialized');
    loadQuizHistory();
    setupPerformanceMonitoring();
    checkAPIStatus();
});

// Check API connectivity and show status
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/test`);
        const data = await response.json();
        
        if (data.success) {
            console.log('✅ API connected:', data.message);
            if (!data.ai_available) {
                showNotification('Using smart fallback generation (AI key not configured)', 'info');
            }
        }
    } catch (error) {
        console.warn('⚠️ API connection test failed:', error);
        showNotification('App running in offline mode', 'warning');
    }
}

// Enhanced quiz generation with better error handling
async function generateQuiz() {
    const notes = document.getElementById('notesInput').value.trim();
    const selectedQuizType = document.getElementById('quizType').value;
    
    // Enhanced input validation
    if (!notes) {
        showNotification('Please enter some notes first!', 'error');
        return;
    }
    
    if (notes.length < 30) {
        showNotification('Please provide more detailed notes (at least 30 characters)', 'warning');
        return;
    }
    
    if (notes.length > 5000) {
        showNotification('Notes too long. Please limit to 5000 characters.', 'warning');
        return;
    }

    // Show enhanced loading state
    showLoadingState(true);
    document.getElementById('generateBtn').disabled = true;
    
    const startTime = performance.now();

    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                notes: notes,
                quiz_type: selectedQuizType,
                num_questions: 5
            })
        });

        const data = await response.json();
        
        if (data.success) {
            currentQuiz = data.questions;
            quizType = selectedQuizType;
            currentQuestionIndex = 0;
            userAnswers = new Array(currentQuiz.length).fill(null);
            quizStartTime = Date.now();
            questionTimes = [];
            
            // Update analytics
            appAnalytics.quizzesGenerated++;
            
            // Show generation success with metadata
            const generationTime = ((performance.now() - startTime) / 1000).toFixed(2);
            showNotification(`Quiz generated in ${generationTime}s using ${data.metadata?.generation_method || 'AI'}!`, 'success');
            
            displayQuiz();
        } else {
            throw new Error(data.error || 'Failed to generate quiz');
        }

    } catch (error) {
        console.error('❌ Quiz generation error:', error);
        
        // Enhanced error messages
        if (error.message.includes('Rate limit')) {
            showNotification('Too many requests. Please wait a minute before generating another quiz.', 'warning');
        } else if (error.message.includes('network')) {
            showNotification('Network error. Please check your connection and try again.', 'error');
        } else {
            showNotification('Quiz generation failed. Please try with different notes or check your connection.', 'error');
        }
    } finally {
        showLoadingState(false);
        document.getElementById('generateBtn').disabled = false;
    }
}

// Enhanced notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.insertBefore(notification, document.body.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Enhanced loading state with progress indication
function showLoadingState(show) {
    const loadingElement = document.getElementById('loadingState');
    
    if (show) {
        loadingElement.classList.remove('hidden');
        loadingElement.innerHTML = `
            <div class="spinner"></div>
            <p>🤖 AI is analyzing your notes and creating intelligent questions...</p>
            <div class="progress-steps">
                <span class="step active">📝 Processing notes</span>
                <span class="step">🧠 Generating questions</span>
                <span class="step">✨ Finalizing quiz</span>
            </div>
        `;
        
        // Simulate progress steps
        setTimeout(() => {
            const steps = document.querySelectorAll('.step');
            if (steps[1]) steps[1].classList.add('active');
        }, 1000);
        
        setTimeout(() => {
            const steps = document.querySelectorAll('.step');
            if (steps[2]) steps[2].classList.add('active');
        }, 2500);
        
    } else {
        loadingElement.classList.add('hidden');
    }
}

// Display the quiz
function displayQuiz() {
    document.getElementById('quizSection').classList.remove('hidden');
    updateQuestionDisplay();
}

// Update question display
function updateQuestionDisplay() {
    const question = currentQuiz[currentQuestionIndex];
    const totalQuestions = currentQuiz.length;
    
    // Update counter
    document.getElementById('questionCounter').textContent = 
        `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;
    
    // Update question text
    document.getElementById('questionText').textContent = question.question;
    
    // Handle different quiz types
    if (quizType === 'mcq') {
        displayMCQ(question);
    } else {
        displayFlashcard(question);
    }
    
    // Update navigation buttons
    document.getElementById('prevBtn').disabled = currentQuestionIndex === 0;
    document.getElementById('nextBtn').textContent = 
        currentQuestionIndex === totalQuestions - 1 ? 'Finish Quiz' : 'Next →';
}

// Display multiple choice question
function displayMCQ(question) {
    document.getElementById('optionsContainer').classList.remove('hidden');
    document.getElementById('flashcardAnswer').classList.add('hidden');
    
    const optionsContainer = document.getElementById('optionsContainer');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        optionDiv.textContent = option;
        optionDiv.onclick = () => selectOption(index, optionDiv);
        
        // Restore previous selection
        if (userAnswers[currentQuestionIndex] === index) {
            optionDiv.classList.add('selected');
        }
        
        optionsContainer.appendChild(optionDiv);
    });
}

// Display flashcard
function displayFlashcard(question) {
    document.getElementById('optionsContainer').classList.add('hidden');
    document.getElementById('flashcardAnswer').classList.remove('hidden');
    
    // Reset flashcard state
    document.getElementById('revealBtn').classList.remove('hidden');
    document.getElementById('answerText').classList.add('hidden');
    document.getElementById('answerText').textContent = question.answer;
}

// Select MCQ option
function selectOption(index, optionElement) {
    // Remove previous selections
    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('selected');
    });
    
    // Add selection to current option
    optionElement.classList.add('selected');
    userAnswers[currentQuestionIndex] = index;
}

// Reveal flashcard answer
function revealAnswer() {
    document.getElementById('revealBtn').classList.add('hidden');
    document.getElementById('answerText').classList.remove('hidden');
}

// Navigation functions
function nextQuestion() {
    if (currentQuestionIndex < currentQuiz.length - 1) {
        currentQuestionIndex++;
        updateQuestionDisplay();
    } else {
        finishQuiz();
    }
}

function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        updateQuestionDisplay();
    }
}

// Finish quiz and show results
function finishQuiz() {
    if (quizType === 'mcq') {
        calculateAndShowResults();
    } else {
        showFlashcardCompletion();
    }
}

// Calculate MCQ results
function calculateAndShowResults() {
    let correct = 0;
    currentQuiz.forEach((question, index) => {
        if (userAnswers[index] === question.correct_answer) {
            correct++;
        }
    });
    
    const percentage = Math.round((correct / currentQuiz.length) * 100);
    
    document.getElementById('questionContainer').classList.add('hidden');
    document.getElementById('resultsContainer').classList.remove('hidden');
    
    document.getElementById('scoreDisplay').innerHTML = `
        <div class="score-display">
            <h4>Your Score: ${correct}/${currentQuiz.length} (${percentage}%)</h4>
            <p class="score-message">${getScoreMessage(percentage)}</p>
        </div>
    `;
    
    // Save quiz to history
    saveQuizToHistory();
}

// Show flashcard completion
function showFlashcardCompletion() {
    document.getElementById('questionContainer').classList.add('hidden');
    document.getElementById('resultsContainer').classList.remove('hidden');
    
    document.getElementById('scoreDisplay').innerHTML = `
        <div class="completion-display">
            <h4>Flashcard Review Complete!</h4>
            <p>You've reviewed ${currentQuiz.length} flashcards. Great job studying! 📚</p>
        </div>
    `;
    
    saveQuizToHistory();
}

// Get encouraging score message
function getScoreMessage(percentage) {
    if (percentage >= 90) return "Excellent! You've mastered this material! 🌟";
    if (percentage >= 80) return "Great job! You have a solid understanding! 👏";
    if (percentage >= 70) return "Good work! A bit more review and you'll ace it! 📈";
    if (percentage >= 60) return "Not bad! Keep studying to improve your score! 📚";
    return "Keep practicing! Review your notes and try again! 💪";
}

// Restart quiz
function restartQuiz() {
    document.getElementById('quizSection').classList.add('hidden');
    document.getElementById('notesInput').value = '';
    document.getElementById('notesInput').focus();
}

// Save quiz to history (using in-memory storage for demo)
function saveQuizToHistory() {
    const quiz = {
        id: Date.now(),
        date: new Date().toLocaleDateString(),
        type: quizType,
        questions: currentQuiz.length,
        notes_preview: document.getElementById('notesInput').value.substring(0, 100) + '...'
    };
    
    // In a real app, this would be saved to database
    addQuizToHistoryDisplay(quiz);
}

// Add quiz to history display
function addQuizToHistoryDisplay(quiz) {
    const historyContainer = document.getElementById('historyContainer');
    
    // Remove empty state if present
    const emptyState = historyContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const quizItem = document.createElement('div');
    quizItem.className = 'history-item';
    quizItem.innerHTML = `
        <div class="history-item-content">
            <h4>${quiz.type === 'mcq' ? '🎯 Multiple Choice Quiz' : '📇 Flashcard Set'}</h4>
            <p><strong>Date:</strong> ${quiz.date}</p>
            <p><strong>Questions:</strong> ${quiz.questions}</p>
            <p><strong>Notes:</strong> ${quiz.notes_preview}</p>
        </div>
    `;
    
    historyContainer.insertBefore(quizItem, historyContainer.firstChild);
}

// Load quiz history (placeholder for demo)
function loadQuizHistory() {
    // In a real app, this would fetch from database
    console.log('Quiz history loaded');
}

// Error handling for network requests
function handleNetworkError(error) {
    console.error('Network error:', error);
    alert('Connection error. Please check your internet connection and try again.');
}

// Add some basic styling for history items
const style = document.createElement('style');
style.textContent = `
    .history-item {
        background: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #667eea;
    }
    
    .history-item h4 {
        color: #4a5568;
        margin-bottom: 8px;
    }
    
    .history-item p {
        color: #718096;
        font-size: 0.9em;
        margin-bottom: 4px;
    }
    
    .score-display, .completion-display {
        background: #f0fff4;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #48bb78;
    }
    
    .score-display h4, .completion-display h4 {
        color: #22543d;
        margin-bottom: 10px;
    }
    
    .score-message {
        color: #2f855a;
        font-weight: 500;
    }
`;
document.head.appendChild(style);