from yt_dlp import YoutubeDL

VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

def list_subs():
    ydl_opts = {
        "skip_download": True,
        "list_subs": True, # List available subtitles
        "quiet": False,    # Show output
        "no_warnings": False,
        "format": "bestaudio/best",
        "ignore_no_formats_error": True,
    }

    print(f"Listing subtitles for {URL}...")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(URL, download=False)

if __name__ == "__main__":
    list_subs()
