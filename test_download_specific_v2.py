from yt_dlp import YoutubeDL
import tempfile
import glob
import os

VIDEO_ID = "2E41a_xgHE4"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"

COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

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

def test_download_specific():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write cookies to file
        cookie_file = os.path.join(temp_dir, "cookies.txt")
        with open(cookie_file, "w") as f:
            f.write(COOKIES)

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "vi"], 
            "subtitlesformat": "json3",
            "quiet": False,
            "no_warnings": False,
            "format": "bestaudio/best",
            "ignore_no_formats_error": True,
            "outtmpl": f"{temp_dir}/%(id)s",
            "paths": {"home": temp_dir},
            "cookiefile": cookie_file,
            "impersonate": "chrome", 
        }

        print(f"Downloading subtitles for {URL} into {temp_dir} with cookies...")
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(URL, download=True)
                
                files = glob.glob(os.path.join(temp_dir, "*"))
                # Filter out the cookie file itself
                files = [f for f in files if "cookies.txt" not in f]
                print(f"Downloaded files: {[os.path.basename(f) for f in files]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_download_specific()
