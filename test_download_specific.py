from yt_dlp import YoutubeDL
import tempfile
import glob
import os

VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

def test_download_specific():
    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "vi"], # Try English and Vietnamese
            "subtitlesformat": "json3",
            "quiet": False,
            "no_warnings": False,
            "format": "bestaudio/best",
            "ignore_no_formats_error": True,
            "outtmpl": f"{temp_dir}/%(id)s",
            "paths": {"home": temp_dir},
        }

        print(f"Downloading subtitles for {URL} into {temp_dir}...")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(URL, download=True)
            
            files = glob.glob(os.path.join(temp_dir, "*"))
            print(f"Downloaded files: {[os.path.basename(f) for f in files]}")

if __name__ == "__main__":
    test_download_specific()
