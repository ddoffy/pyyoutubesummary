from yt_dlp import YoutubeDL
import json

VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

def check_subs():
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": False,
        "format": "bestaudio/best",
        "ignore_no_formats_error": True,
    }

    print(f"Checking subtitles for {URL}...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URL, download=False)
        
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        
        print(f"\nManual Subtitles: {list(subs.keys())}")
        for lang, formats in subs.items():
             print(f"  {lang}: {[f['ext'] for f in formats]}")

        print(f"\nAutomatic Captions: {list(auto_subs.keys())}")
        for lang, formats in auto_subs.items():
             print(f"  {lang}: {[f['ext'] for f in formats]}")

if __name__ == "__main__":
    check_subs()
