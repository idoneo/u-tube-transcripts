import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key and video ID from environment variables
API_KEY = os.getenv('YOUTUBE_API_KEY')
VIDEO_ID = os.getenv('YOUTUBE_VIDEO_ID')

def get_transcript(video_id, api_key):
    try:
        # Create YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # First, get the caption tracks available for the video
        captions_response = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
        
        # Get the first available caption track ID
        if 'items' in captions_response:
            caption_id = captions_response['items'][0]['id']
            
            # Download the transcript
            transcript = youtube.captions().download(
                id=caption_id,
                tfmt='srt'
            ).execute()
            
            return transcript
        else:
            return "No captions found for this video."
            
    except HttpError as e:
        return f"An HTTP error occurred: {e.resp.status} {e.content}"

def main():
    # Replace with your API key and video ID
    API_KEY = 'YOUR_API_KEY_HERE'
    VIDEO_ID = 'YOUTUBE_VIDEO_ID_HERE'
    
    transcript = get_transcript(VIDEO_ID, API_KEY)
    print(transcript)

if __name__ == "__main__":
    print("Starting...")
    main()