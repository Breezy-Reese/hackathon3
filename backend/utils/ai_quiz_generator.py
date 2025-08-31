import requests
import json
import re
import random
from typing import List, Dict, Any

class AIQuizGenerator:
    """AI-powered quiz generator using Hugging Face models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        
        # Best models for quiz generation
        self.models = {
            'text_generation': 'microsoft/DialoGPT-medium',
            'question_answering': 'deepset/roberta-base-squad2',
            'text2text': 'google/flan-t5-base'  # Best for quiz generation
        }
    
    def generate_quiz(self, notes: str, quiz_type: str = 'mcq', num_questions: int = 5) -> List[Dict]:
        """Main method to generate quiz questions"""
        
        # Clean and validate input
        notes = self._clean_text(notes)
        if len(notes.split()) < 20:
            raise ValueError("Notes too short. Please provide more detailed content.")
        
        try:
            # Try AI generation first
            if quiz_type == 'mcq':
                questions = self._generate_mcq_with_ai(notes, num_questions)
            else:
                questions = self._generate_flashcards_with_ai(notes, num_questions)
                
            # Fallback if AI fails
            if not questions or len(questions) == 0:
                print("AI generation failed, using fallback method")
                questions = self._generate_fallback_quiz(notes, quiz_type, num_questions)
            
            return questions[:num_questions]  # Ensure we don't exceed requested number
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return self._generate_fallback_quiz(notes, quiz_type, num_questions)
    
    def _generate_mcq_with_ai(self, notes: str, num_questions: int) -> List[Dict]:
        """Generate MCQ using Hugging Face text generation"""
        
        # Create a structured prompt for better results
        prompt = f"""Generate {num_questions} multiple choice questions based on this content:

{notes}

Format EXACTLY as follows for each question:
QUESTION: [Write clear question here]
A) [First option]
B) [Second option] 
C) [Third option]
D) [Fourth option]
CORRECT: [A, B, C, or D]
---

QUESTION:"""

        try:
            # Use Flan-T5 for better text generation
            api_url = f"https://api-inference.huggingface.co/models/{self.models['text2text']}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 800,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    return self._parse_mcq_response(generated_text)
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
        
        return []
    
    def _generate_flashcards_with_ai(self, notes: str, num_questions: int) -> List[Dict]:
        """Generate flashcards using AI"""
        
        prompt = f"""Create {num_questions} flashcard questions from this content:

{notes}

Format EXACTLY as follows:
Q: [Question]
A: [Answer]
---
Q:"""

        try:
            api_url = f"https://api-inference.huggingface.co/models/{self.models['text2text']}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 600,
                    "temperature": 0.6
                }
            }
            
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    return self._parse_flashcard_response(generated_text)
            
        except Exception as e:
            print(f"Flashcard generation error: {e}")
        
        return []
    
    def _parse_mcq_response(self, text: str) -> List[Dict]:
        """Parse AI-generated MCQ text into structured format"""
        questions = []
        
        # Split by question markers
        question_blocks = re.split(r'QUESTION:', text)
        
        for block in question_blocks[1:]:  # Skip first empty block
            try:
                lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
                
                if len(lines) < 6:  # Need question + 4 options + correct answer
                    continue
                
                question_text = lines[0].strip()
                options = []
                correct_answer = 0
                
                # Extract options
                for line in lines[1:5]:
                    if re.match(r'^[A-D]\)', line):
                        option = re.sub(r'^[A-D]\)\s*', '', line).strip()
                        options.append(option)
                
                # Find correct answer
                correct_line = next((line for line in lines if line.startswith('CORRECT:')), '')
                if correct_line:
                    correct_letter = correct_line.replace('CORRECT:', '').strip().upper()
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
                print(f"Error parsing question block: {e}")
                continue
        
        return questions
    
    def _parse_flashcard_response(self, text: str) -> List[Dict]:
        """Parse AI-generated flashcard text"""
        questions = []
        
        # Split by Q: markers
        parts = re.split(r'\bQ:', text)
        
        for part in parts[1:]:  # Skip first empty part
            try:
                lines = [line.strip() for line in part.strip().split('\n') if line.strip()]
                
                if len(lines) < 2:
                    continue
                
                question_text = lines[0].strip()
                
                # Find answer line
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
    
    def _generate_fallback_quiz(self, notes: str, quiz_type: str, num_questions: int) -> List[Dict]:
        """Fallback quiz generation when AI fails"""
        
        sentences = [s.strip() for s in notes.split('.') if s.strip() and len(s.split()) > 3]
        questions = []
        
        for i, sentence in enumerate(sentences[:num_questions]):
            words = sentence.split()
            
            if quiz_type == 'mcq':
                # Create fill-in-the-blank MCQ
                if len(words) > 5:
                    # Pick important word (avoid articles, prepositions)
                    important_words = [w for w in words if len(w) > 3 and w.lower() not in 
                                     ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']]
                    
                    if important_words:
                        key_word = random.choice(important_words)
                        question_text = sentence.replace(key_word, "______", 1)
                        
                        # Generate plausible wrong answers
                        wrong_options = [
                            f"{key_word}s",
                            f"non-{key_word}",
                            f"{key_word[:-1]}y" if len(key_word) > 3 else f"{key_word}_alt"
                        ]
                        
                        options = [key_word] + wrong_options
                        random.shuffle(options)
                        correct_answer = options.index(key_word)
                        
                        questions.append({
                            'question': f"Fill in the blank: {question_text}",
                            'options': options,
                            'correct_answer': correct_answer,
                            'type': 'mcq'
                        })
            
            else:  # flashcard
                if len(words) > 3:
                    # Create question from sentence
                    question = f"What does this describe: {' '.join(words[:4])}...?"
                    answer = sentence
                    
                    questions.append({
                        'question': question,
                        'answer': answer,
                        'type': 'flashcard'
                    })
        
        return questions
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might confuse the AI
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()

# Test the AI generator
if __name__ == "__main__":
    # Test with sample notes
    sample_notes = """
    The mitochondria is the powerhouse of the cell. It produces ATP through cellular respiration.
    Photosynthesis occurs in chloroplasts and converts sunlight into chemical energy.
    DNA is stored in the nucleus and contains genetic information.
    Ribosomes are responsible for protein synthesis in the cell.
    """
    
    # Note: You'll need to set your Hugging Face API key
    generator = AIQuizGenerator("your_hugging_face_api_key_here")
    
    print("Testing MCQ generation...")
    mcq_questions = generator.generate_quiz(sample_notes, 'mcq', 3)
    print(f"Generated {len(mcq_questions)} MCQ questions")
    
    print("\nTesting Flashcard generation...")
    flashcard_questions = generator.generate_quiz(sample_notes, 'flashcard', 3)
    print(f"Generated {len(flashcard_questions)} flashcard questions")
    
    print("\n✅ AI integration test complete!")