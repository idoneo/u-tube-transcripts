import yt_dlp
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import os
from tqdm import tqdm

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    
    # Handle YouTube shorts
    if '/shorts/' in url:
        return url.split('/shorts/')[1].split('?')[0]
    
    # Handle regular YouTube videos
    query = parse_qs(urlparse(url).query)
    if 'v' in query:
        return query['v'][0]
    
    raise ValueError(f"Could not extract video ID from URL: {url}")

def download_audio(url, output_dir):
    """Download audio from a single YouTube video"""
    try:
        video_id = get_video_id(url)
        output_path = Path(output_dir) / f"{video_id}.wav"
        
        # Create progress bar for download
        progress_bar = tqdm(total=100, position=1, desc='Download Progress', leave=False)
        
        def update_progress(d):
            if d['status'] == 'downloading':
                try:
                    # Extract percentage without color codes
                    percent_str = d.get('_percent_str', '0%').strip()
                    percent = float(percent_str.replace('%', ''))
                    progress_bar.n = percent
                    progress_bar.refresh()
                except:
                    pass  # Ignore progress parsing errors
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': str(output_path.with_suffix('')),
            'progress_hooks': [update_progress],
            'quiet': True,  # Suppress yt-dlp's output
            'no_color': True  # Disable color codes in output
        }
        
        print(f"\nDownloading audio for video ID: {video_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        progress_bar.close()
        print(f"Successfully downloaded: {output_path}")
        return True
        
    except Exception as e:
        print(f"\nError downloading {url}: {str(e)}")
        return False

def batch_download_audio(urls_file='youtube_urls.txt', output_dir='wav-files'):
    """Process a list of YouTube URLs and download their audio"""
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Read URLs from file
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading URLs file: {str(e)}")
        return
    
    # Process each URL
    print(f"\nFound {len(urls)} URLs to process")
    print("="*50)
    
    successful = 0
    failed = 0
    
    # Create progress bar for overall progress
    with tqdm(total=len(urls), position=0, desc='Overall Progress') as pbar:
        for i, url in enumerate(urls, 1):
            if download_audio(url, output_dir):
                successful += 1
            else:
                failed += 1
            pbar.update(1)
    
    # Print summary
    print("\n" + "="*50)
    print("Download Summary:")
    print(f"Total URLs processed: {len(urls)}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed downloads: {failed}")
    print(f"Audio files saved to: {Path(output_dir).absolute()}")
    print("="*50)

if __name__ == "__main__":
    batch_download_audio()