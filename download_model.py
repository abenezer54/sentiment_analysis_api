from transformers import pipeline
import os

# Get the model name from your environment variables, same as your app
MODEL_NAME = os.getenv(
    'SENTIMENT_MODEL_NAME', 
    'cardiffnlp/twitter-roberta-base-sentiment-latest'
)

def download_and_cache_model():
    """
    Downloads the specified Hugging Face model to the local cache.
    """
    print(f"--- Downloading and caching model: {MODEL_NAME} ---")
    print("This may take a while depending on your internet connection.")
    
    try:
        # This line will trigger the download and save it to the cache
        # directory (usually C:/Users/your_user/.cache/huggingface/hub)
        pipeline("sentiment-analysis", model=MODEL_NAME)
        
        print("\n--- Model downloaded and cached successfully! ---")
        
    except Exception as e:
        print(f"\nAn error occurred during download: {e}")
        print("Please check your internet connection and try running the script again.")

if __name__ == "__main__":
    download_and_cache_model()