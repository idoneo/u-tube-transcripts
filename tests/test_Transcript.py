from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Each line in transcript is a dict with keys: 
        # 'text', 'start', 'duration'
        for line in transcript:
            print(f"{line['start']:.1f}s: {line['text']}")
            
    except TranscriptsDisabled:
        print("Transcripts are disabled for this video")
    except NoTranscriptFound:
        print("No transcript found for this video")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage with a video ID
video_id = "Jo4ZWAmwtgg&t=3231s" # Replace with your video ID
get_transcript(video_id)