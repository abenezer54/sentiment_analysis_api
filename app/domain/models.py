from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class AnalysisStatus(Enum):
    """Status of sentiment analysis job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Tweet:
    """Domain model for a tweet"""
    id: str
    text: str
    author_id: str
    created_at: datetime
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None

@dataclass
class SentimentResult:
    """Domain model for sentiment analysis result"""
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    average_polarity: float
    total_tweets: int
    analyzed_tweets: int

@dataclass
class Analysis:
    """Domain model for sentiment analysis job"""
    job_id: str
    topic: str
    status: AnalysisStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[SentimentResult] = None
    error_message: Optional[str] = None
    tweets: Optional[List[Tweet]] = None

@dataclass
class AnalysisRequest:
    """Domain model for analysis request"""
    topic: str
    max_tweets: int = 10
