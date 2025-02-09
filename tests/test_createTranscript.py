import whisper
import subprocess
from pathlib import Path
import yt_dlp

def download_youtube_audio(video_url, output_path=None):
    """Download audio from YouTube video"""
    if output_path is None:
        output_path = 'downloaded_audio.wav'
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': str(Path(output_path).with_suffix('')),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return str(Path(output_path).with_suffix('.wav'))
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        return None

def transcribe_spanish_from_youtube(video_url):
    """Download and transcribe YouTube video"""
    try:
        print("Downloading audio from YouTube...")
        audio_path = download_youtube_audio(video_url)
        if not audio_path:
            return
        
        print("Loading Whisper model...")
        model = whisper.load_model("medium")
        
        print("Transcribing audio...")
        result = model.transcribe(
            audio_path,
            language="es",
            task="transcribe",
            temperature=0.2,
            word_timestamps=True
        )
        
        # Save transcript
        output_path = Path(audio_path).with_suffix('.srt')
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"], 1):
                start_time = f"{int(segment['start'] // 3600):02d}:{int((segment['start'] % 3600) // 60):02d}:{segment['start'] % 60:06.3f}"
                end_time = f"{int(segment['end'] // 3600):02d}:{int((segment['end'] % 3600) // 60):02d}:{segment['end'] % 60:06.3f}"
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        
        # Clean up audio file
        Path(audio_path).unlink()
        
        print(f"Transcription complete! Saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Usage
if __name__ == "__main__":
    #video_url = "https://www.youtube.com/watch?v=Jo4ZWAmwtgg&t=3231s" 1hour long
    video_url = "https://www.youtube.com/watch?v=AsXL13gfhuY&t=105s"
    transcript_file = transcribe_spanish_from_youtube(video_url)
    