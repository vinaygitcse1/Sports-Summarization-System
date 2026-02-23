import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline
import re
from collections import Counter

class SportsSummarizer:
    def __init__(self):
        # Download NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        # Sports-specific keywords
        self.sports_keywords = {
            'goal', 'score', 'penalty', 'corner', 'foul', 'red card', 'yellow card',
            'substitution', 'injury', 'free kick', 'offside', 'save', 'assist',
            'hat-trick', 'brace', 'equalizer', 'winner', 'draw', 'victory', 'defeat'
        }
        
        # Initialize transformer model (using smaller model for local)
        self.summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            tokenizer="sshleifer/distilbart-cnn-12-6"
        )
    
    def preprocess_text(self, text):
        """Clean and preprocess commentary text"""
        # Remove timestamps like [12:34] or (12:34)
        text = re.sub(r'[\[\(]\d{1,2}:\d{2}[\]\)]', '', text)
        
        # Remove special characters but keep punctuation for sentences
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        
        # Replace multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_key_events(self, text):
        """Extract key sports events from commentary"""
        sentences = sent_tokenize(text)
        key_events = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check for sports keywords
            keywords_found = [kw for kw in self.sports_keywords if kw in sentence_lower]
            
            if keywords_found:
                # Score pattern detection
                score_pattern = r'(\d+\s*[-:]\s*\d+)'
                scores = re.findall(score_pattern, sentence)
                
                # Time pattern detection
                time_pattern = r'(\d+[\'’]\d*|\d+th\s+minute)'
                times = re.findall(time_pattern, sentence)
                
                key_events.append({
                    'sentence': sentence.strip(),
                    'keywords': keywords_found,
                    'score': scores[0] if scores else None,
                    'time': times[0] if times else None,
                    'type': self.classify_event(keywords_found)
                })
        
        return key_events
    
    def classify_event(self, keywords):
        """Classify the type of event"""
        scoring_keywords = {'goal', 'score', 'hat-trick', 'brace', 'equalizer'}
        disciplinary_keywords = {'foul', 'red card', 'yellow card'}
        
        if any(kw in scoring_keywords for kw in keywords):
            return 'scoring'
        elif any(kw in disciplinary_keywords for kw in keywords):
            return 'disciplinary'
        elif 'substitution' in keywords:
            return 'substitution'
        elif 'injury' in keywords:
            return 'injury'
        else:
            return 'general'
    
    def generate_summary(self, text, max_length=150, min_length=30):
        """Generate summary using transformer model"""
        # Preprocess text
        cleaned_text = self.preprocess_text(text)
        
        # Extract key events
        key_events = self.extract_key_events(cleaned_text)
        
        # Generate summary
        if len(cleaned_text.split()) < 50:
            # For very short texts, use extractive summarization
            summary = self.extractive_summarization(cleaned_text)
        else:
            # Use transformer model
            try:
                summary_result = self.summarizer(
                    cleaned_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summary = summary_result[0]['summary_text']
            except:
                # Fallback to extractive summarization
                summary = self.extractive_summarization(cleaned_text)
        
        return {
            'summary': summary,
            'key_events': key_events,
            'word_count': len(cleaned_text.split()),
            'event_count': len(key_events)
        }
    
    def extractive_summarization(self, text, num_sentences=3):
        """Simple extractive summarization as fallback"""
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return ' '.join(sentences)
        
        # Score sentences based on keyword presence
        scored_sentences = []
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # Score based on sports keywords
            for keyword in self.sports_keywords:
                if keyword in sentence_lower:
                    score += 3
            
            # Score based on numeric patterns (scores, times)
            if re.search(r'\d', sentence):
                score += 2
            
            # Penalize very short sentences
            if len(sentence.split()) < 5:
                score -= 1
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored_sentences[:num_sentences]]
        
        # Maintain original order
        top_sentences.sort(key=lambda x: sentences.index(x))
        
        return ' '.join(top_sentences)