from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Analysis, Tweet, SentimentResult

class AnalysisRepository(ABC):
    """Abstract interface for analysis data persistence"""
    
    @abstractmethod
    def create(self, analysis: Analysis) -> Analysis:
        """Create a new analysis record"""
        pass
    
    @abstractmethod
    def get_by_id(self, job_id: str) -> Optional[Analysis]:
        """Retrieve analysis by job ID"""
        pass
    
    @abstractmethod
    def update_status(self, job_id: str, status: str, result: Optional[SentimentResult] = None, error_message: Optional[str] = None) -> bool:
        """Update analysis status and result"""
        pass

class TwitterRepository(ABC):
    """Abstract interface for Twitter data access"""
    
    @abstractmethod
    def search_tweets(self, topic: str, max_tweets: int = 10) -> List[Tweet]:
        """Search for tweets about a given topic"""
        pass

class SentimentService(ABC):
    """Abstract interface for sentiment analysis service"""
    
    @abstractmethod
    def analyze_text(self, text: str) -> tuple[str, float]:
        """Analyze sentiment of a single text and return (label, score)"""
        pass
    
    @abstractmethod
    def analyze_batch(self, texts: List[str]) -> List[tuple[str, float]]:
        """Analyze sentiment of multiple texts"""
        pass
