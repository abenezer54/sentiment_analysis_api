"""Worker initialization script to preload models and services"""
import logging
from .ml_sentiment_service import MLSentimentService

logger = logging.getLogger(__name__)

def initialize_worker():
    """Initialize worker services and preload models"""
    try:
        logger.info("Initializing Celery worker...")
        
        # Preload the sentiment analysis model
        logger.info("Preloading sentiment analysis model...")
        sentiment_service = MLSentimentService()
        logger.info("Sentiment analysis model loaded successfully")
        
        # You can add other service initializations here
        
        logger.info("Celery worker initialization completed")
        
    except Exception as e:
        logger.error(f"Failed to initialize Celery worker: {str(e)}")
        raise
