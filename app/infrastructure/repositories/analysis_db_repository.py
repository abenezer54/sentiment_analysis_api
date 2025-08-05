from sqlalchemy import create_engine, Column, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional
import json

from ...domain.interfaces import AnalysisRepository
from ...domain.models import Analysis, SentimentResult, AnalysisStatus
from config import config

# Database setup
engine = create_engine(config['default'].DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisModel(Base):
    """SQLAlchemy model for analysis table"""
    __tablename__ = "analyses"
    
    job_id = Column(String, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

class AnalysisDBRepository(AnalysisRepository):
    """Database implementation of AnalysisRepository"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def create(self, analysis: Analysis) -> Analysis:
        """Create a new analysis record"""
        db = self.SessionLocal()
        try:
            db_analysis = AnalysisModel(
                job_id=analysis.job_id,
                topic=analysis.topic,
                status=analysis.status.value,
                created_at=analysis.created_at,
                completed_at=analysis.completed_at,
                error_message=analysis.error_message
            )
            
            if analysis.result:
                db_analysis.result_data = {
                    "positive_percentage": analysis.result.positive_percentage,
                    "negative_percentage": analysis.result.negative_percentage,
                    "neutral_percentage": analysis.result.neutral_percentage,
                    "average_polarity": analysis.result.average_polarity,
                    "total_tweets": analysis.result.total_tweets,
                    "analyzed_tweets": analysis.result.analyzed_tweets
                }
            
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            
            return analysis
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_by_id(self, job_id: str) -> Optional[Analysis]:
        """Retrieve analysis by job ID"""
        db = self.SessionLocal()
        try:
            db_analysis = db.query(AnalysisModel).filter(AnalysisModel.job_id == job_id).first()
            
            if not db_analysis:
                return None
            
            # Convert database model to domain model
            result = None
            if db_analysis.result_data:
                result = SentimentResult(
                    positive_percentage=db_analysis.result_data.get("positive_percentage", 0.0),
                    negative_percentage=db_analysis.result_data.get("negative_percentage", 0.0),
                    neutral_percentage=db_analysis.result_data.get("neutral_percentage", 0.0),
                    average_polarity=db_analysis.result_data.get("average_polarity", 0.0),
                    total_tweets=db_analysis.result_data.get("total_tweets", 0),
                    analyzed_tweets=db_analysis.result_data.get("analyzed_tweets", 0)
                )
            
            return Analysis(
                job_id=db_analysis.job_id,
                topic=db_analysis.topic,
                status=AnalysisStatus(db_analysis.status),
                created_at=db_analysis.created_at,
                completed_at=db_analysis.completed_at,
                result=result,
                error_message=db_analysis.error_message
            )
            
        finally:
            db.close()
    
    def update_status(self, job_id: str, status: str, result: Optional[SentimentResult] = None, error_message: Optional[str] = None) -> bool:
        """Update analysis status and result"""
        db = self.SessionLocal()
        try:
            db_analysis = db.query(AnalysisModel).filter(AnalysisModel.job_id == job_id).first()
            
            if not db_analysis:
                return False
            
            db_analysis.status = status
            db_analysis.completed_at = datetime.utcnow() if status in ["completed", "failed"] else None
            db_analysis.error_message = error_message
            
            if result:
                db_analysis.result_data = {
                    "positive_percentage": result.positive_percentage,
                    "negative_percentage": result.negative_percentage,
                    "neutral_percentage": result.neutral_percentage,
                    "average_polarity": result.average_polarity,
                    "total_tweets": result.total_tweets,
                    "analyzed_tweets": result.analyzed_tweets
                }
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
