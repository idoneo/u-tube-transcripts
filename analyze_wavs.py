from pathlib import Path
import wave
import datetime
from tqdm import tqdm

def is_valid_wav(file_path):
    """Check if WAV file is valid and readable"""
    try:
        with wave.open(str(file_path), 'rb') as wav:
            return wav.getnframes() > 0 and wav.getframerate() > 0
    except:
        return False

def get_file_info(wav_file, frames, rate):
    """Get detailed WAV file information"""
    duration = frames / float(rate)
    return {
        'path': wav_file,
        'duration': duration,
        'minutes': duration / 60,
        'size_mb': wav_file.stat().st_size / (1024 * 1024),
        'sample_rate': rate,
        'channels': wav_file.getnchannels(),
        'sample_width': wav_file.getsampwidth(),
        'compression': wav_file.getcomptype()
    }

def analyze_wav_files(wav_dir='wav-files'):
    wav_path = Path(wav_dir)
    if not wav_path.exists():
        print(f"❌ Directory not found: {wav_dir}")
        return [], [], []
    
    files = list(wav_path.glob('*.wav'))
    if not files:
        print(f"No WAV files found in {wav_dir}")
        return [], [], []
    
    # Group files by duration
    short_files = []  # < 15 min
    medium_files = [] # 15-30 min
    long_files = []   # > 30 min
    
    print("\n🔍 Analyzing WAV files...")
    print("="*50)
    
    invalid_files = []
    with tqdm(files, desc="Analyzing files") as pbar:
        for file in pbar:
            pbar.set_description(f"Analyzing {file.name}")
            try:
                if not is_valid_wav(file):
                    invalid_files.append(file)
                    continue
                
                with wave.open(str(file), 'rb') as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    duration = frames / float(rate)
                    minutes = duration / 60
                    
                    file_info = {
                        'path': file,
                        'duration': duration,
                        'minutes': minutes,
                        'size_mb': file.stat().st_size / (1024 * 1024)
                    }
                    
                    if minutes < 15:
                        short_files.append(file_info)
                    elif minutes < 30:
                        medium_files.append(file_info)
                    else:
                        long_files.append(file_info)
        
            except Exception as e:
                print(f"Error analyzing {file.name}: {e}")
                invalid_files.append(file)
    
    # Print analysis
    print(f"\nTotal WAV files found: {len(files)}")
    print(f"\nFile Distribution:")
    print(f"Short (<15min): {len(short_files)}")
    print(f"Medium (15-30min): {len(medium_files)}")
    print(f"Long (>30min): {len(long_files)}")
    
    print("\nLong Files (>30min):")
    for file in long_files:
        print(f"- {file['path'].name}")
        print(f"  Duration: {datetime.timedelta(seconds=int(file['duration']))}")
        print(f"  Size: {file['size_mb']:.1f}MB")
        print(f"  Sample Rate: {file['sample_rate']} Hz")
        print(f"  Channels: {file['channels']}")
        print(f"  Bit Depth: {file['sample_width'] * 8} bits")
    
    if invalid_files:
        print("\n⚠️ Invalid or corrupted WAV files:")
        for file in invalid_files:
            print(f"- {file.name}")
    
    return short_files, medium_files, long_files

if __name__ == "__main__":
    analyze_wav_files() 