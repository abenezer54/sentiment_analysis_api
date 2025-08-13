from transformers import pipeline
from typing import List, Tuple
import logging
import torch
import threading

from ...domain.interfaces import SentimentService
from config import config

logger = logging.getLogger(__name__)

class MLSentimentService(SentimentService):
    """Machine Learning sentiment analysis service using Hugging Face transformers"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MLSentimentService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the sentiment analysis pipeline only once"""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._initialize_pipeline()
                    self._initialized = True
    
    def _initialize_pipeline(self):
        """Initialize the sentiment analysis pipeline"""
        self.config = config['default']
        
        try:
            logger.info(f"Initializing sentiment analysis model: {self.config.SENTIMENT_MODEL_NAME}")
            
            # Initialize the sentiment analysis pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.config.SENTIMENT_MODEL_NAME,
                device=0 if torch.cuda.is_available() else -1  # Use GPU if available
            )
            logger.info(f"Successfully initialized sentiment analysis model: {self.config.SENTIMENT_MODEL_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analysis model: {str(e)}")
            raise Exception(f"Failed to initialize sentiment analysis model: {str(e)}")
    
    def analyze_text(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of a single text and return (label, score)"""
        try:
            # Skip very short texts
            if len(text.strip()) < 3:
                return "neutral", 0.5
            
            # Run sentiment analysis
            result = self.pipeline(text, truncation=True, max_length=512)
            
            # Extract label and score
            label = result[0]['label'].lower()
            score = result[0]['score']
            
            # Normalize labels to our expected format
            if label in ['positive', 'pos']:
                label = 'positive'
            elif label in ['negative', 'neg']:
                label = 'negative'
            else:
                label = 'neutral'
            
            return label, score
            
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {str(e)}")
            # Return neutral sentiment as fallback
            return "neutral", 0.5
    
    def analyze_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """Analyze sentiment of multiple texts"""
        try:
            if not texts:
                return []
            
            # Filter out very short texts
            valid_texts = [text for text in texts if len(text.strip()) >= 3]
            
            if not valid_texts:
                return [("neutral", 0.5)] * len(texts)
            
            # Run batch sentiment analysis
            results = self.pipeline(valid_texts, truncation=True, max_length=512)
            
            # Process results
            processed_results = []
            for result in results:
                label = result['label'].lower()
                score = result['score']
                
                # Normalize labels
                if label in ['positive', 'pos']:
                    label = 'positive'
                elif label in ['negative', 'neg']:
                    label = 'negative'
                else:
                    label = 'neutral'
                
                processed_results.append((label, score))
            
            # Pad results if some texts were filtered out
            while len(processed_results) < len(texts):
                processed_results.append(("neutral", 0.5))
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {str(e)}")
            # Return neutral sentiments as fallback
            return [("neutral", 0.5)] * len(texts)
