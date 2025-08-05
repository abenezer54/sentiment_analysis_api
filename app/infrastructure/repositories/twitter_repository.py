import tweepy
from typing import List
from datetime import datetime
import re
import logging

from ...domain.interfaces import TwitterRepository
from ...domain.models import Tweet
from config import config

logger = logging.getLogger(__name__)

class TwitterRepositoryImpl(TwitterRepository):
    """Twitter API implementation using Tweepy"""
    
    def __init__(self):
        """Initialize Twitter API client"""
        self.config = config['default']
        
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=self.config.TWITTER_BEARER_TOKEN,
            consumer_key=self.config.TWITTER_API_KEY,
            consumer_secret=self.config.TWITTER_API_SECRET,
            access_token=self.config.TWITTER_ACCESS_TOKEN,
            access_token_secret=self.config.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
    
    def search_tweets(self, topic: str, max_tweets: int = 100) -> List[Tweet]:
        """Search for tweets about a given topic"""
        try:
            # Clean the topic for search
            clean_topic = self._clean_topic(topic)
            
            # Search tweets using Twitter API v2
            response = self.client.search_recent_tweets(
                query=clean_topic,
                max_results=min(max_tweets, 100),  # Twitter API v2 limit
                tweet_fields=['created_at', 'author_id'],
                language='en'
            )
            
            if not response.data:
                logger.warning(f"No tweets found for topic: {topic}")
                return []
            
            tweets = []
            for tweet_data in response.data:
                # Clean the tweet text
                cleaned_text = self._clean_tweet_text(tweet_data.text)
                
                # Skip tweets that are too short after cleaning
                if len(cleaned_text.strip()) < 10:
                    continue
                
                tweet = Tweet(
                    id=str(tweet_data.id),
                    text=cleaned_text,
                    author_id=str(tweet_data.author_id),
                    created_at=tweet_data.created_at
                )
                tweets.append(tweet)
            
            logger.info(f"Retrieved {len(tweets)} tweets for topic: {topic}")
            return tweets
            
        except tweepy.TooManyRequests:
            logger.error("Twitter API rate limit exceeded")
            raise Exception("Twitter API rate limit exceeded")
        except tweepy.Unauthorized:
            logger.error("Twitter API authentication failed")
            raise Exception("Twitter API authentication failed")
        except Exception as e:
            logger.error(f"Error fetching tweets: {str(e)}")
            raise Exception(f"Failed to fetch tweets: {str(e)}")
    
    def _clean_topic(self, topic: str) -> str:
        """Clean and format topic for Twitter search"""
        # Remove special characters and format for search
        clean_topic = re.sub(r'[^\w\s]', '', topic)
        clean_topic = clean_topic.strip()
        
        # Add quotes for exact phrase matching
        return f'"{clean_topic}"'
    
    def _clean_tweet_text(self, text: str) -> str:
        """Clean tweet text by removing URLs, mentions, and other noise"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags (but keep the text)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove RT (retweet indicator)
        text = re.sub(r'^RT\s+', '', text)
        
        return text.strip()
