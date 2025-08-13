# Contains the 'AnalyzeTopicUseCase' and other application-specific logic.

from ..domain.models import AnalysisRequest
from ..domain.services import AnalysisOrchestrator
from ..infrastructure.repositories.twitter_repository import TwitterRepositoryImpl
from ..infrastructure.repositories.analysis_db_repository import AnalysisDBRepository
from ..infrastructure.services.ml_sentiment_service import MLSentimentService
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AnalyzeTopicUseCase:
    """Use case for analyzing sentiment of a topic"""
    
    def __init__(self):
        """Initialize use case with concrete implementations"""
        # Initialize repositories and services
        self.twitter_repo = TwitterRepositoryImpl()
        self.sentiment_service = MLSentimentService()
        self.analysis_repo = AnalysisDBRepository()
        
        # Initialize orchestrator
        self.orchestrator = AnalysisOrchestrator(
            twitter_repo=self.twitter_repo,
            sentiment_service=self.sentiment_service,
            analysis_repo=self.analysis_repo
        )
    
    def create_analysis_job(self, topic: str, max_tweets: int = 100) -> str:
        """Create a new analysis job and queue it for processing"""
        try:
            # Create the analysis job in the database
            job_id = self.orchestrator.create_analysis_job(topic, max_tweets)
            
            # Queue the background task using the Flask app's Celery instance
            from ..infrastructure.task_queue.tasks import analyze_topic_task
            current_app.celery.send_task('analyze_topic_task', args=[job_id, topic, max_tweets])
            
            logger.info(f"Created analysis job {job_id} for topic: {topic}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error creating analysis job: {str(e)}")
            raise
    
    def get_analysis_results(self, job_id: str):
        """Retrieve analysis results by job ID"""
        try:
            analysis = self.analysis_repo.get_by_id(job_id)
            return analysis
            
        except Exception as e:
            logger.error(f"Error retrieving analysis results for job {job_id}: {str(e)}")
            raise
