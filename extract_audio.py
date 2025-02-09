from pathlib import Path
import subprocess
from tqdm import tqdm
import os

def extract_audio(video_path, output_dir='wav-files'):
    """Extract audio from video file to WAV format"""
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Create output filename
        video_name = Path(video_path).stem
        output_path = Path(output_dir) / f"{video_name}.wav"
        
        # Skip if output file already exists
        if output_path.exists():
            print(f"⏩ Skipping {video_name} - WAV file already exists")
            return True
        
        print(f"\nExtracting audio from: {video_name}")
        
        # Use ffmpeg to extract audio
        command = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # Disable video
            '-acodec', 'pcm_s16le',  # Audio codec for WAV
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        # Run ffmpeg
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode == 0:
            print(f"✨ Successfully extracted audio to: {output_path}")
            return True
        else:
            print(f"❌ Error extracting audio: {process.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {video_path}: {str(e)}")
        return False

def process_videos(pcloud_dir, process_mode='ask'):
    """Process all MP4 files in the pCloud directory"""
    input_path = Path(pcloud_dir).expanduser()
    
    if not input_path.exists():
        print(f"❌ pCloud directory not found: {pcloud_dir}")
        return
    
    # Find all MP4 files (including subdirectories)
    all_videos = list(input_path.rglob('*.mp4'))
    
    if not all_videos:
        print(f"No MP4 files found in {pcloud_dir}")
        return
    
    # Filter out videos that already have WAV files
    video_files = []
    already_processed = []
    for video in all_videos:
        wav_path = Path('wav-files') / f"{video.stem}.wav"
        if wav_path.exists():
            already_processed.append(video)
        else:
            video_files.append(video)
    
    print(f"\n🎯 Found {len(all_videos)} total videos")
    print(f"Already processed: {len(already_processed)}")
    print(f"New videos to process: {len(video_files)}")
    
    if not video_files:
        print("\nAll videos have already been processed!")
        return
    
    print("\nNew files to process:")
    for file in video_files:
        print(f"- {file.relative_to(input_path)}")
    
    print("\n" + "="*50)
    
    successful = 0
    failed = 0
    skipped = 0
    
    if process_mode == 'all':
        print("\nProcessing all files automatically...")
        for i, video_file in enumerate(video_files, 1):
            print(f"\n[Video {i}/{len(video_files)}]")
            print(f"File: {video_file.relative_to(input_path)}")
            
            if extract_audio(video_file):
                successful += 1
            else:
                failed += 1
            
            print("="*50)
    else:
        for i, video_file in enumerate(video_files, 1):
            print(f"\n[Video {i}/{len(video_files)}]")
            print(f"File: {video_file.relative_to(input_path)}")
            
            # Ask user before processing each file
            response = input("Press Enter to process this file (s to skip, q to quit)...").lower()
            
            if response == 'q':
                print("Operation cancelled by user")
                break
            elif response == 's':
                print("Skipping file...")
                skipped += 1
                continue
            
            if extract_audio(video_file):
                successful += 1
            else:
                failed += 1
            
            print("="*50)
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total videos found: {len(all_videos)}")
    print(f"Previously processed: {len(already_processed)}")
    print(f"New videos processed: {successful}")
    print(f"Failed conversions: {failed}")
    print(f"Skipped: {skipped}")
    print(f"WAV files saved to: {Path('wav-files').absolute()}")

if __name__ == "__main__":
    # Set specific pCloud directory path
    default_dir = "~/pCloud Drive/MyVideos/Utube/FelixCorona"
    pcloud_dir = input(f"Enter your pCloud directory path (default: {default_dir}): ").strip()
    
    if not pcloud_dir:
        pcloud_dir = default_dir
    
    # Ask for processing mode
    print("\nChoose processing mode:")
    print("1. Process one by one (ask for each file)")
    print("2. Process all files automatically")
    
    mode = input("\nEnter your choice (1 or 2): ").strip()
    
    process_videos(pcloud_dir, 'ask' if mode == '1' else 'all') 