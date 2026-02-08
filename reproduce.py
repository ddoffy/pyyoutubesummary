from yt_dlp import YoutubeDL
import sys

# Video ID that was failing
VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

def test_extract():
    # Options that were failing + attempts to fix
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-orig"],
        "subtitlesformat": "json3",
        "quiet": False,
        "no_warnings": False,
        # Try ignoring format requirements since we only want subs
        "format": "bestaudio/best",
        "ignore_no_formats_error": True,
    }

    print(f"Testing extraction for {URL}...")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(URL, download=False)
            print("Extraction successful!")
            print(f"Title: {info.get('title')}")
            
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    test_extract()
