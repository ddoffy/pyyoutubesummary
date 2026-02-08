from yt_dlp import YoutubeDL
from curl_cffi import requests
import json
import os

VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

COOKIES_TXT = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	FALSE	1804911072	HSID	AZ-5i3jokYaR-euQb
.youtube.com	TRUE	/	TRUE	1804911072	SSID	ABNoGWvcEx-aFbhv1
.youtube.com	TRUE	/	FALSE	1804911072	APISID	dN_PrthHBKSjoL1u/ATjcuaXsthyXJJdnh
.youtube.com	TRUE	/	TRUE	1804911072	SAPISID	4wnXiREayiVqAglm/AY4sH5KGrEoIHDT5A
.youtube.com	TRUE	/	TRUE	1804911072	__Secure-1PAPISID	4wnXiREayiVqAglm/AY4sH5KGrEoIHDT5A
.youtube.com	TRUE	/	TRUE	1804911072	__Secure-3PAPISID	4wnXiREayiVqAglm/AY4sH5KGrEoIHDT5A
.youtube.com	TRUE	/	TRUE	1794446231	LOGIN_INFO	AFmmF2swRgIhAM7d_wDgxVzOTThsIySEbp3g61g3UpRXPU519lf07_UZAiEAvMTB5fZJNxw5vKsiuGtzxByIvoX9c_l4KiyvQDiLEww:QUQ3MjNmeE0yOXdFUDR0NHNZMk5HRVhIYVhfRzQ0TmR5YWdENnBLMVhhNVJvYWhBTG5XNHJfUzlVcUdEQ0g0QmdJSVBvR2NuMUt4SVNsd3I2YS1OR1Frc3hDREttUUhqUnpuR2VnTVU4aEFzT3htQ3BGQ1ZmN0JKTGFwVG41ZGQ1djRMaHVodHQ5bTZsa2Y1ZFRlS3AzbkxmT0NqOEFaX05R
.youtube.com	TRUE	/	FALSE	1804911072	SID	g.a0006gg1JoTdc-4mcDbZEU_BtMFnblsQ6-kqcLFYlY7zNdp6DbyD3Q1s9EMJNq-dE-dtqwZ3nAACgYKARgSARASFQHGX2MisC7nds0ApUNUyXGx4MsP-BoVAUF8yKoYLX1lycLJkcL9it_8FmPh0076
.youtube.com	TRUE	/	TRUE	1804911072	__Secure-1PSID	g.a0006gg1JoTdc-4mcDbZEU_BtMFnblsQ6-kqcLFYlY7zNdp6DbyDIOQ0XNqEb6eBF2jpCcueWQACgYKAZ8SARASFQHGX2Mi_QdyleDUEfUwuJo0ys4F3hoVAUF8yKrRzngWLghWEERwUAxi-QKR0076
.youtube.com	TRUE	/	TRUE	1804911072	__Secure-3PSID	g.a0006gg1JoTdc-4mcDbZEU_BtMFnblsQ6-kqcLFYlY7zNdp6DbyD69VMseRrgJzYMR8ggqUsfAACgYKAQ4SARASFQHGX2MiEPOGDiGbvXyN2Q4n8qg3_BoVAUF8yKrXvUxV79kvSQXEEI_dj3X60076
.youtube.com	TRUE	/	TRUE	1805073198	PREF	f6=40000080&f7=4100&tz=America.Mexico_City&f3=10&utco=420&f5=20000
.youtube.com	TRUE	/	TRUE	1802050672	__Secure-1PSIDTS	sidts-CjIB7I_69EMHJ7Fc5_zXNAhBlBGSf3YIRU9wkKjTRGfliQx-5m751Jd2oZv4ahwRkGr8tBAA
.youtube.com	TRUE	/	TRUE	1802050672	__Secure-3PSIDTS	sidts-CjIB7I_69EMHJ7Fc5_zXNAhBlBGSf3YIRU9wkKjTRGfliQx-5m751Jd2oZv4ahwRkGr8tBAA
.youtube.com	TRUE	/	FALSE	1802050672	SIDCC	AKEyXzVYZWVDbkyMrAEM-KU1VJHQACG5jJtxd3es_tYOLfbitz6x0_7YTDxoLbAVIPgDU4NP06k
.youtube.com	TRUE	/	TRUE	1802050672	__Secure-1PSIDCC	AKEyXzWxNebp-RX_528Pn_qTzStVx-30DoYRd66EBBTX4Ye0eP1OUA6nEO0e6r65XEHw_nso1aA
.youtube.com	TRUE	/	TRUE	1802050672	__Secure-3PSIDCC	AKEyXzW3jspRkhGDqvlvl7nUydVyDMPzpU3HJlpHndGXk6XSfziOzBZGejb0dVOr23mVgl1bjA
"""

def parse_cookies(cookie_content):
    cookies = {}
    for line in cookie_content.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 7:
            cookies[parts[5]] = parts[6]
    return cookies

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
        
        # Parse cookies
        cookies = parse_cookies(COOKIES_TXT)
        
        # Download with curl_cffi
        print("Downloading with curl_cffi + cookies...")
        try:
            response = requests.get(
                target_url,
                cookies=cookies,
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
                # print(response.text[:200])
                
        except Exception as e:
            print(f"Error downloading: {e}")

if __name__ == "__main__":
    test_manual_download()
