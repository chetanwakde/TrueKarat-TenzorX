import os
import subprocess

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data", "AudioTapTest")
    os.makedirs(base_dir, exist_ok=True)
    
    print("Downloading Audio Tap Test samples via yt-dlp...")
    
    queries = [
        "ytsearch3:gold vs tungsten sound test",
        "ytsearch3:real gold coin ping test",
        "ytsearch3:fake gold ring sound drop"
    ]
    
    for query in queries:
        print(f"Searching and downloading: {query}")
        try:
            subprocess.run([
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "wav",
                "--audio-quality", "0",
                "--max-downloads", "3",
                "-o", os.path.join(base_dir, "%(title)s.%(ext)s"),
                query
            ], check=True)
        except Exception as e:
            print(f"Failed on query {query}: {e}")
            
    print("Audio download complete. You can now use these WAV files to train the FFT Audio Head!")

if __name__ == "__main__":
    main()
