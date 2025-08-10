from typing import List
from .models import Tweet, SentimentResult, Analysis, AnalysisStatus
from .interfaces import TwitterRepository, SentimentService, AnalysisRepository
from datetime import datetime
import uuid

class SentimentCalculator:
    """Core business logic for sentiment analysis calculations"""
    
    @staticmethod   
    def calculate_sentiment_statistics(tweets: List[Tweet]) -> SentimentResult:
        """Calculate sentiment statistics from analyzed tweets"""
        if not tweets:
            return SentimentResult(
                positive_percentage=0.0,
                negative_percentage=0.0,
                neutral_percentage=0.0,
                average_polarity=0.0,
                total_tweets=0,
                analyzed_tweets=0
            )
        
        total_tweets = len(tweets)
        analyzed_tweets = len([t for t in tweets if t.sentiment_label is not None])
        
        if analyzed_tweets == 0:
            return SentimentResult(
                positive_percentage=0.0,
                negative_percentage=0.0,
                neutral_percentage=0.0,
                average_polarity=0.0,
                total_tweets=total_tweets,
                analyzed_tweets=analyzed_tweets
            )
        
        # Count sentiment labels
        positive_count = len([t for t in tweets if t.sentiment_label == 'positive'])
        negative_count = len([t for t in tweets if t.sentiment_label == 'negative'])
        neutral_count = len([t for t in tweets if t.sentiment_label == 'neutral'])
        
        # Calculate percentages
        positive_percentage = (positive_count / analyzed_tweets) * 100
        negative_percentage = (negative_count / analyzed_tweets) * 100
        neutral_percentage = (neutral_count / analyzed_tweets) * 100
        
        # Calculate average polarity (sentiment scores)
        sentiment_scores = [t.sentiment_score for t in tweets if t.sentiment_score is not None]
        average_polarity = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        return SentimentResult(
            positive_percentage=positive_percentage,
            negative_percentage=negative_percentage,
            neutral_percentage=neutral_percentage,
            average_polarity=average_polarity,
            total_tweets=total_tweets,
            analyzed_tweets=analyzed_tweets
        )

class AnalysisOrchestrator:
    """Orchestrates the complete sentiment analysis workflow"""
    
    def __init__(
        self,
        twitter_repo: TwitterRepository,
        sentiment_service: SentimentService,
        analysis_repo: AnalysisRepository
    ):
        self.twitter_repo = twitter_repo
        self.sentiment_service = sentiment_service
        self.analysis_repo = analysis_repo
    
    def create_analysis_job(self, topic: str, max_tweets: int = 10) -> str:
        """Create a new analysis job and return job ID"""
        job_id = str(uuid.uuid4())
        
        analysis = Analysis(
            job_id=job_id,
            topic=topic,
            status=AnalysisStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.analysis_repo.create(analysis)
        return job_id
    
    def execute_analysis(self, job_id: str, topic: str, max_tweets: int = 10) -> bool:
        """Execute the complete sentiment analysis workflow"""
        try:
            # Update status to processing
            self.analysis_repo.update_status(job_id, AnalysisStatus.PROCESSING.value)
            
            # Step 1: Fetch tweets
            tweets = self.twitter_repo.search_tweets(topic, max_tweets)
            
            # Step 2: Analyze sentiment for each tweet
            for tweet in tweets:
                label, score = self.sentiment_service.analyze_text(tweet.text)
                tweet.sentiment_label = label
                tweet.sentiment_score = score
            
            # Step 3: Calculate aggregated results
            sentiment_result = SentimentCalculator.calculate_sentiment_statistics(tweets)
            
            # Step 4: Update analysis with results
            self.analysis_repo.update_status(
                job_id, 
                AnalysisStatus.COMPLETED.value, 
                result=sentiment_result
            )
            
            return True
            
        except Exception as e:
            # Update status to failed
            self.analysis_repo.update_status(
                job_id, 
                AnalysisStatus.FAILED.value, 
                error_message=str(e)
            )
            return False
