import whisper
import subprocess
from pathlib import Path
import yt_dlp
from tqdm import tqdm
import time
from urllib.parse import parse_qs, urlparse

def download_youtube_audio(video_url, output_dir='source-wav'):
    """Download audio from YouTube video with progress tracking"""
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Extract video ID for filename
        if 'youtu.be' in video_url:
            video_id = video_url.split('/')[-1].split('?')[0]
        elif '/shorts/' in video_url:
            video_id = video_url.split('/shorts/')[1].split('?')[0]
        else:
            query = parse_qs(urlparse(video_url).query)
            video_id = query['v'][0]
        
        output_path = Path(output_dir) / f"{video_id}.wav"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': str(output_path.with_suffix('')),
            'progress_hooks': [lambda d: print(f"\rDownload Progress: {d['_percent_str']}", end='') 
                             if d['status'] == 'downloading' else None],
        }
        
        print(f"\nDownloading audio for video ID: {video_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("\nAudio download and conversion complete!")
        return str(output_path)
    except Exception as e:
        print(f"\nError downloading audio: {str(e)}")
        return None

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def transcribe_local_wav_files(input_dir='wav-files', output_dir='completed-transcript'):
    """Transcribe all WAV files in the specified directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get all WAV files
    wav_files = list(input_path.glob('*.wav'))
    
    if not wav_files:
        print(f"No WAV files found in {input_dir}")
        return
    
    print("\n🎯 Starting Batch Spanish Transcription Process")
    print(f"Found {len(wav_files)} WAV files to process")
    
    # Load model once for all files
    print("\nLoading Whisper large model...")
    model = whisper.load_model("large")
    
    for wav_file in wav_files:
        print("\n" + "="*50)
        print(f"Processing: {wav_file.name}")
        
        # Ask user before proceeding
        input("Press Enter to start processing this file...")
        
        start_time = time.time()
        
        try:
            print("Transcribing audio...")
            print("This may take several minutes. Progress will be shown below:")
            
            result = model.transcribe(
                str(wav_file),
                language="es",
                temperature=0.1,
                initial_prompt="El siguiente es un discurso en español cubano:",
                verbose=True
            )
            
            # Save transcript with progress indicator
            srt_output = output_path / f"{wav_file.stem}.srt"
            print(f"\nGenerating SRT file: {srt_output}")
            
            total_segments = len(result["segments"])
            with open(srt_output, 'w', encoding='utf-8') as f:
                for i, segment in tqdm(enumerate(result["segments"], 1), 
                                     total=total_segments,
                                     desc="Writing SRT file",
                                     unit="segments"):
                    start_time_str = format_timestamp(segment['start'])
                    end_time_str = format_timestamp(segment['end'])
                    
                    f.write(f"{i}\n")
                    f.write(f"{start_time_str} --> {end_time_str}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
            
            # Calculate processing time for this file
            total_time = time.time() - start_time
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            
            print(f"✨ Transcription complete for {wav_file.name}")
            print(f"📝 Transcript saved to: {srt_output}")
            print(f"⏱️  Processing time: {minutes}m {seconds}s")
            
        except Exception as e:
            print(f"\n❌ Error processing {wav_file.name}: {str(e)}")

def transcribe_spanish_from_youtube(video_url):
    """Download and transcribe YouTube video with progress tracking"""
    try:
        print("\n🎬 Starting YouTube Spanish Transcription Process")
        print("\n" + "="*50)
        print("Step 1/3: Downloading and converting audio...")
        start_time = time.time()
        
        # Download to source-wav directory
        audio_path = download_youtube_audio(video_url, 'source-wav')
        if not audio_path:
            return
        
        print("\n" + "="*50)
        print("Step 2/3: Loading Whisper model...")
        model = whisper.load_model("large")  # Changed to large model
        
        print("\n" + "="*50)
        print("Step 3/3: Transcribing audio...")
        print("This may take several minutes. Progress will be shown below:")
        
        result = model.transcribe(
            audio_path,
            language="es",
            temperature=0.0,
            initial_prompt="El siguiente es un discurso en español cubano:",
            verbose=True
        )
        
        # Save transcript to completed-transcript directory
        output_path = Path('completed-transcript') / f"{Path(audio_path).stem}.srt"
        Path('completed-transcript').mkdir(exist_ok=True)
        
        print(f"\nGenerating SRT file: {output_path}")
        
        total_segments = len(result["segments"])
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in tqdm(enumerate(result["segments"], 1), 
                                 total=total_segments,
                                 desc="Writing SRT file",
                                 unit="segments"):
                start_time_str = format_timestamp(segment['start'])
                end_time_str = format_timestamp(segment['end'])
                
                f.write(f"{i}\n")
                f.write(f"{start_time_str} --> {end_time_str}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        
        # Calculate total processing time
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        print("\n" + "="*50)
        print(f"✨ Transcription complete!")
        print(f"📝 Transcript saved to: {output_path}")
        print(f"⏱️  Total processing time: {minutes}m {seconds}s")
        print("="*50 + "\n")
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    while True:
        print("\nChoose operation mode:")
        print("1. Process local WAV files")
        print("2. Download and transcribe from YouTube")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            transcribe_local_wav_files()
        elif choice == "2":
            video_url = input("Enter YouTube URL: ")
            transcribe_spanish_from_youtube(video_url)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")