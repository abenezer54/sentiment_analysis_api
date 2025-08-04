from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from .schemas import AnalysisRequestSchema, AnalysisResponseSchema, ErrorResponseSchema
from ..use_cases.analyze_topic import AnalyzeTopicUseCase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze_topic():
    """Start a new sentiment analysis job"""
    try:
        # Validate request data
        request_data = request.get_json()
        if not request_data:
            return jsonify(ErrorResponseSchema(
                error="Request body is required"
            ).dict()), 400
        
        # Validate with Pydantic schema
        try:
            validated_data = AnalysisRequestSchema(**request_data)
        except ValidationError as e:
            return jsonify(ErrorResponseSchema(
                error="Invalid request data",
                details={"validation_errors": e.errors()}
            ).dict()), 400
        
        # Initialize use case (this would be injected in a real app)
        use_case = AnalyzeTopicUseCase()
        
        # Execute use case
        job_id = use_case.create_analysis_job(
            topic=validated_data.topic,
            max_tweets=validated_data.max_tweets
        )
        
        # Return immediate response with job ID
        return jsonify({
            "job_id": job_id,
            "status": "pending",
            "message": "Analysis job created successfully"
        }), 202
        
    except Exception as e:
        logger.error(f"Error creating analysis job: {str(e)}")
        return jsonify(ErrorResponseSchema(
            error="Internal server error"
        ).dict()), 500

@api_bp.route('/results/<job_id>', methods=['GET'])
def get_analysis_results(job_id):
    """Get analysis results by job ID"""
    try:
        # Initialize use case
        use_case = AnalyzeTopicUseCase()
        
        # Get analysis results
        analysis = use_case.get_analysis_results(job_id)
        
        if not analysis:
            return jsonify(ErrorResponseSchema(
                error="Analysis job not found"
            ).dict()), 404
        
        # Convert domain model to response schema
        response_data = {
            "job_id": analysis.job_id,
            "status": analysis.status.value,
            "topic": analysis.topic,
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at,
            "error_message": analysis.error_message
        }
        
        # Add result data if analysis is completed
        if analysis.result:
            response_data.update({
                "positive_percentage": analysis.result.positive_percentage,
                "negative_percentage": analysis.result.negative_percentage,
                "neutral_percentage": analysis.result.neutral_percentage,
                "average_polarity": analysis.result.average_polarity,
                "total_tweets": analysis.result.total_tweets,
                "analyzed_tweets": analysis.result.analyzed_tweets
            })
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analysis results: {str(e)}")
        return jsonify(ErrorResponseSchema(
            error="Internal server error"
        ).dict()), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "sentiment-analysis-api"
    }), 200
