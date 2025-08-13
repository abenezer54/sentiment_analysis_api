from celery import Celery
from typing import List
import logging

from ...domain.services import AnalysisOrchestrator
from ...infrastructure.repositories.twitter_repository import TwitterRepositoryImpl
from ...infrastructure.repositories.analysis_db_repository import AnalysisDBRepository
from ...infrastructure.services.ml_sentiment_service import MLSentimentService
from ...domain.models import AnalysisStatus
from config import config

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    'sentiment_analysis',
    broker=config['default'].CELERY_BROKER_URL,
    backend=config['default'].CELERY_RESULT_BACKEND
)

@celery_app.task(bind=True, name='analyze_topic_task')
def analyze_topic_task(self, job_id: str, topic: str, max_tweets: int = 100):
    """Celery task to perform sentiment analysis on a topic"""
    try:
        logger.info(f"Starting analysis task for job {job_id}, topic: {topic}")
        
        # Initialize repositories and services
        # Note: MLSentimentService is now a singleton, so it won't reload the model
        twitter_repo = TwitterRepositoryImpl()
        sentiment_service = MLSentimentService()  # This will reuse existing instance
        analysis_repo = AnalysisDBRepository()
        
        # Initialize orchestrator
        orchestrator = AnalysisOrchestrator(
            twitter_repo=twitter_repo,
            sentiment_service=sentiment_service,
            analysis_repo=analysis_repo
        )
        
        # Execute the analysis
        success = orchestrator.execute_analysis(job_id, topic, max_tweets)
        
        if success:
            logger.info(f"Analysis completed successfully for job {job_id}")
            return {
                'job_id': job_id,
                'status': 'completed',
                'topic': topic
            }
        else:
            logger.error(f"Analysis failed for job {job_id}")
            return {
                'job_id': job_id,
                'status': 'failed',
                'topic': topic
            }
            
    except Exception as e:
        logger.error(f"Error in analysis task for job {job_id}: {str(e)}")
        
        # Update analysis status to failed
        try:
            analysis_repo = AnalysisDBRepository()
            analysis_repo.update_status(
                job_id, 
                AnalysisStatus.FAILED.value, 
                error_message=str(e)
            )
        except Exception as update_error:
            logger.error(f"Failed to update analysis status: {str(update_error)}")
        
        # Re-raise the exception to mark task as failed
        raise

@celery_app.task(name='health_check_task')
def health_check_task():
    """Health check task for Celery workers"""
    return {
        'status': 'healthy',
        'service': 'sentiment-analysis-worker'
    }
