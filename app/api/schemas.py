from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AnalysisRequestSchema(BaseModel):
    """Schema for analysis request"""
    topic: str = Field(..., min_length=1, max_length=200, description="Topic to analyze")
    max_tweets: Optional[int] = Field(default=10, ge=1, le=1000, description="Maximum number of tweets to analyze")

class AnalysisResponseSchema(BaseModel):
    """Schema for analysis response"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    topic: str = Field(..., description="Analyzed topic")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    
    # Results (only present when completed)
    positive_percentage: Optional[float] = Field(None, description="Percentage of positive tweets")
    negative_percentage: Optional[float] = Field(None, description="Percentage of negative tweets")
    neutral_percentage: Optional[float] = Field(None, description="Percentage of neutral tweets")
    average_polarity: Optional[float] = Field(None, description="Average sentiment polarity score")
    total_tweets: Optional[int] = Field(None, description="Total tweets fetched")
    analyzed_tweets: Optional[int] = Field(None, description="Number of tweets successfully analyzed")
    
    # Error information (only present when failed)
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")

class ErrorResponseSchema(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
