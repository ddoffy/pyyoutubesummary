from yt_dlp import YoutubeDL
from curl_cffi import requests
import json
import os

VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

def test_manual_download():
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": False,
        "format": "bestaudio/best",
        "ignore_no_formats_error": True,
    }

    print(f"Extracting info for {URL}...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URL, download=False)
        
        # Get auto-subs
        auto_subs = info.get('automatic_captions', {})
        
        # Try to find En or Vi
        target_lang = None
        target_url = None
        
        for lang in ['en', 'vi']:
            if lang in auto_subs:
                target_lang = lang
                # Prefer json3 formats
                for fmt in auto_subs[lang]:
                    if fmt.get('ext') == 'json3':
                        target_url = fmt['url']
                        break
                if target_url:
                    break
        
        if not target_url:
            print("No suitable subtitle found")
            return

        print(f"Found subtitle for {target_lang}: {target_url[:50]}...")
        
        # Download with curl_cffi
        print("Downloading with curl_cffi...")
        try:
            response = requests.get(
                target_url,
                impersonate="chrome110",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                }
            )
            
            if response.status_code == 200:
                print("Download successful!")
                print(f"Content length: {len(response.text)}")
                # Check if it looks like JSON
                data = response.json()
                print("JSON parsing successful")
                print(f"First event: {data.get('events', [{}])[0]}")
            else:
                print(f"Download failed with status: {response.status_code}")
                print(response.text[:200])
                
        except Exception as e:
            print(f"Error downloading: {e}")

if __name__ == "__main__":
    test_manual_download()
