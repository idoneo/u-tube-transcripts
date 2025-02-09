from pathlib import Path
import re
from tqdm import tqdm
import textwrap

def clean_transcript(srt_file, output_dir):
    """Extract just the text from an SRT file, removing numbers and timestamps"""
    try:
        print(f"\nReading file: {srt_file.name}")
        
        # Read the SRT file with progress bar
        file_size = srt_file.stat().st_size
        content = ""
        with open(srt_file, 'r', encoding='utf-8') as f:
            with tqdm(total=file_size, desc="Reading SRT", unit='B', unit_scale=True) as pbar:
                while chunk := f.read(8192):
                    content += chunk
                    pbar.update(len(chunk.encode('utf-8')))
        
        print("\nCleaning transcript...")
        
        # Split content into entries
        entries = re.split(r'\n\n+', content.strip())
        cleaned_lines = []
        
        for entry in entries:
            lines = entry.split('\n')
            if len(lines) >= 3:  # Valid SRT entry should have at least 3 lines
                # Skip first line (number) and second line (timestamp)
                text_lines = lines[2:]
                cleaned_text = ' '.join(line.strip() for line in text_lines if line.strip())
                if cleaned_text:
                    cleaned_lines.append(cleaned_text)
        
        # Join all cleaned lines with proper spacing
        clean_text = ' '.join(cleaned_lines)
        
        # Wrap text to 80 characters
        wrapped_text = '\n'.join(textwrap.fill(line, width=80) 
                               for line in clean_text.split('\n'))
        
        # Create output filename in the specified directory
        output_file = Path(output_dir) / f"{srt_file.stem}.txt"
        summary_file = Path(output_dir) / f"{srt_file.stem}_summary.txt"
        
        # Generate summary
        print("\nGenerating summary...")
        word_count = len(clean_text.split())
        sentence_count = len(re.split(r'[.!?]+', clean_text))
        char_count = len(clean_text)
        
        summary = f"""TRANSCRIPT SUMMARY
====================
Filename: {srt_file.name}
Word Count: {word_count}
Sentence Count: {sentence_count}
Character Count: {char_count}
====================

FULL TRANSCRIPT:
"""
        
        # Save clean text with progress bar
        print("\nSaving cleaned transcript and summary...")
        total_bytes = len(wrapped_text.encode('utf-8'))
        
        # Save main transcript with wrapping
        with open(output_file, 'w', encoding='utf-8') as f:
            with tqdm(total=total_bytes, desc="Writing TXT", unit='B', unit_scale=True) as pbar:
                f.write(wrapped_text)
                pbar.update(total_bytes)
        
        # Save summary file with wrapped text
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
            f.write('\n')
            f.write(wrapped_text)
            
        # Print file statistics
        original_size = file_size / 1024  # KB
        cleaned_size = output_file.stat().st_size / 1024  # KB
        
        print(f"\n✨ Processing complete for: {srt_file.name}")
        print(f"📊 File Statistics:")
        print(f"   - Original SRT size: {original_size:.2f} KB")
        print(f"   - Cleaned TXT size: {cleaned_size:.2f} KB")
        print(f"   - Reduction: {((original_size - cleaned_size) / original_size * 100):.1f}%")
        print(f"   - Word count: {word_count}")
        print(f"   - Sentence count: {sentence_count}")
        print(f"📝 Files saved:")
        print(f"   - Clean transcript: {output_file}")
        print(f"   - Summary file: {summary_file}")
        
        return clean_text
        
    except Exception as e:
        print(f"\n❌ Error processing {srt_file}: {str(e)}")
        return None

def process_all_transcripts(input_dir='completed-transcript', output_dir='processed-transcript'):
    """Process all SRT files in the completed-transcript directory"""
    # Ensure directories exist
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find all SRT files
    srt_files = list(input_path.glob('*.srt'))
    
    if not srt_files:
        print(f"No SRT files found in {input_dir}")
        return
    
    print(f"\n🎯 Found {len(srt_files)} SRT files to process")
    print("="*50)
    
    for i, srt_file in enumerate(srt_files, 1):
        print(f"\n[File {i}/{len(srt_files)}]")
        print(f"Next file to process: {srt_file.name}")
        input("Press Enter to start processing this file...")
        
        clean_transcript(srt_file, output_dir)
        print("="*50)

if __name__ == "__main__":
    process_all_transcripts()