import os
import re
import logging
from typing import List, Tuple, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

from transformers import pipeline
from dotenv import load_dotenv
import google.generativeai as genai

# Setup
load_dotenv()
logger = logging.getLogger(__name__)

# Ensure required NLTK resources
def ensure_nltk_data():
    required = {
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords',
        'wordnet': 'corpora/wordnet',
        'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
        'vader_lexicon': 'sentiment/vader_lexicon',
        'omw-1.4': 'corpora/omw-1.4'
    }
    for name, path in required.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name)

ensure_nltk_data()

class AIUtils:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer()
        self.text_generator = pipeline('text-generation', model='gpt2')

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        return self.sentiment_analyzer.polarity_scores(text)

    def suggest_category(self, title: str, description: str) -> Tuple[str, float]:
        prompt = f"""Analyze this grievance and suggest the most appropriate category from these:
        - infrastructure
        - sanitation
        - safety
        - education
        - health
        - other

        Title: {title}
        Description: {description}

        Return only the category name and confidence score (0-1), e.g. "infrastructure,0.85"
        """
        try:
            response = self.model.generate_content(prompt)
            category, confidence = response.text.strip().split(',')
            return category.lower(), float(confidence)
        except Exception as e:
            logger.error(f"Category suggestion error: {str(e)}")
            return 'other', 0.5

    def find_similar_grievances(self, current: str, all_others: List[str], top_n: int = 5) -> List[Tuple[str, float]]:
        if not all_others:
            return []
        try:
            tfidf_matrix = self.vectorizer.fit_transform([current] + all_others)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            indices = similarities.argsort()[-top_n:][::-1]
            return [(all_others[i], similarities[i]) for i in indices]
        except Exception as e:
            logger.error(f"Similarity check error: {str(e)}")
            return []

    def generate_response_suggestion(self, description: str, context: str = "") -> str:
        prompt = f"""Generate a professional, empathetic response for this grievance.
        Context: {context}
        Grievance: {description}

        The response should:
        1. Acknowledge the issue
        2. Show empathy
        3. Outline next steps (max 3 sentences)
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI response generation error: {str(e)}")
            return "Thank you for your submission. We will address it as soon as possible."

    def prioritize_grievance(self, title: str, description: str) -> Tuple[str, float]:
        prompt = f"""Analyze this grievance for priority (Low, Medium, High) based on:
        - Urgency
        - Public safety impact
        - Affected people
        - Time sensitivity

        Title: {title}
        Description: {description}

        Return format: "High,0.92"
        """
        try:
            response = self.model.generate_content(prompt)
            priority, confidence = response.text.strip().split(',')
            return priority.strip(), float(confidence)
        except Exception as e:
            logger.error(f"Priority assessment error: {str(e)}")
            return 'Medium', 0.5

class SearchEnhancer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_text(self, text: str) -> List[str]:
        try:
            text = re.sub(r'[^\w\s]', '', text.lower())
            tokens = word_tokenize(text)
            return [self.lemmatizer.lemmatize(tok) for tok in tokens if tok not in self.stop_words]
        except Exception as e:
            logger.warning(f"Text preprocessing failed: {str(e)}")
            return []

    def get_synonyms(self, word: str) -> List[str]:
        try:
            synonyms = set()
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    synonyms.add(lemma.name())
            return list(synonyms) or [word]
        except Exception:
            return [word]

    def enhance_search_query(self, query: str) -> List[str]:
        processed = self.preprocess_text(query)
        expanded = set(processed)
        for word in processed:
            expanded.update(self.get_synonyms(word))
        return list(expanded)

    def calculate_relevance_score(self, text: str, terms: List[str]) -> int:
        text_tokens = self.preprocess_text(text)
        exact = sum(1 for term in terms if term in text_tokens)
        partial = sum(1 for term in terms if any(term in t for t in text_tokens))
        return (exact * 2) + partial

class PriorityAssessor:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.priority_keywords = {
            'urgent': 3, 'emergency': 3, 'critical': 3, 'immediate': 3, 'danger': 3,
            'hazard': 3, 'accident': 3, 'injury': 3, 'death': 3, 'serious': 2,
            'important': 2, 'severe': 2, 'major': 2, 'concern': 1, 'issue': 1,
            'problem': 1, 'request': 1, 'suggestion': 1,
        }

    def _calculate_sentiment_score(self, text: str) -> float:
        return self.sia.polarity_scores(text)['compound']

    def _extract_keywords(self, text: str) -> Dict[str, int]:
        words = [w for w in word_tokenize(text.lower()) if w not in self.stop_words]
        return {w: words.count(w) for w in set(words) if w in self.priority_keywords}

    def _calculate_priority_score(self, title: str, description: str) -> float:
        full_text = f"{title} {description}"
        keywords = self._extract_keywords(full_text)
        keyword_score = sum(self.priority_keywords[k] * v for k, v in keywords.items())
        max_score = sum(self.priority_keywords.values())
        sentiment = (self._calculate_sentiment_score(full_text) + 1) / 2
        return (0.7 * (keyword_score / max_score)) + (0.3 * sentiment)

    def assess_priority(self, title: str, description: str) -> Tuple[str, float]:
        score = self._calculate_priority_score(title, description)
        if score >= 0.7:
            return 'High', min(1.0, score + 0.2)
        elif score >= 0.4:
            return 'Medium', min(1.0, score + 0.2)
        return 'Low', min(1.0, score + 0.2)
