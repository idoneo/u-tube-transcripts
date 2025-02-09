from pathlib import Path
import wave
import datetime

def analyze_wav_files(wav_dir='wav-files'):
    wav_path = Path(wav_dir)
    files = list(wav_path.glob('*.wav'))
    
    # Group files by duration
    short_files = []  # < 15 min
    medium_files = [] # 15-30 min
    long_files = []   # > 30 min
    
    print("\n🔍 Analyzing WAV files...")
    print("="*50)
    
    for file in files:
        try:
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
    
    return short_files, medium_files, long_files

if __name__ == "__main__":
    analyze_wav_files() 