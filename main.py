import json
import os
import re
import tempfile
from typing import Optional

import google.generativeai as genai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from yt_dlp import YoutubeDL

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="YouTube Summary API")


class SummaryRequest(BaseModel):
    id: str
    format: str = "json"
    cookies: Optional[str] = None
    userAgent: Optional[str] = None


def extract_transcript(video_id: str, cookies: Optional[str], user_agent: Optional[str]) -> str:
    """Extract transcript/subtitles from a YouTube video using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"

    cookie_file = None
    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-orig"],
            "subtitlesformat": "json3",
            "quiet": True,
            "no_warnings": True,
            "format": "best",
        }

        # cookies
        if cookies:
            cookie_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            )
            cookie_file.write(cookies)
            cookie_file.close()
            ydl_opts["cookiefile"] = cookie_file.name

        if user_agent:
            ydl_opts["http_headers"] = {"User-Agent": user_agent}

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info:
                raise HTTPException(status_code=404, detail="Video not found")

            # Try to get subtitles: prefer manual, then automatic
            subtitles = info.get("subtitles", {})
            auto_captions = info.get("automatic_captions", {})

            sub_data = None
            sub_url = None

            # Check manual subtitles first
            for lang in ["en", "en-orig", "en-US"]:
                if lang in subtitles:
                    for fmt in subtitles[lang]:
                        if fmt.get("ext") == "json3":
                            sub_url = fmt["url"]
                            break
                    if sub_url:
                        break

            # Fall back to auto captions
            if not sub_url:
                for lang in ["en", "en-orig", "en-US"]:
                    if lang in auto_captions:
                        for fmt in auto_captions[lang]:
                            if fmt.get("ext") == "json3":
                                sub_url = fmt["url"]
                                break
                        if sub_url:
                            break

            if not sub_url:
                raise HTTPException(
                    status_code=422,
                    detail="No English subtitles/captions found for this video",
                )

            # Download the subtitle content
            sub_data = ydl.urlopen(sub_url).read().decode("utf-8")
            sub_json = json.loads(sub_data)

            # Extract text from json3 format
            segments = []
            for event in sub_json.get("events", []):
                segs = event.get("segs", [])
                text = "".join(s.get("utf8", "") for s in segs).strip()
                if text and text != "\n":
                    segments.append(text)

            transcript = " ".join(segments)
            # Clean up whitespace
            transcript = re.sub(r"\s+", " ", transcript).strip()

            if not transcript:
                raise HTTPException(
                    status_code=422, detail="Subtitles found but transcript is empty"
                )

            video_title = info.get("title", "Unknown")
            video_channel = info.get("channel", info.get("uploader", "Unknown"))
            video_duration = info.get("duration_string", "Unknown")

            return transcript, video_title, video_channel, video_duration

    finally:
        if cookie_file and os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)


def summarize_with_gemini(
    transcript: str, title: str, channel: str, duration: str
) -> dict:
    """Summarize the transcript using Google Gemini API."""
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""You are a helpful assistant that summarizes YouTube videos.

Video Title: {title}
Channel: {channel}
Duration: {duration}

Below is the transcript of the video. Please provide:
1. A concise summary (2-3 paragraphs)
2. Key points (bullet list)
3. Main takeaways

Transcript:
{transcript[:30000]}

Respond in JSON format:
{{
  "summary": "...",
  "keyPoints": ["...", "..."],
  "takeaways": ["...", "..."]
}}"""

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json",
        ),
    )

    return json.loads(response.text)


@app.post("/api/summary")
async def get_summary(request: SummaryRequest):
    transcript, title, channel, duration = extract_transcript(
        request.id, request.cookies, request.userAgent
    )

    result = summarize_with_gemini(transcript, title, channel, duration)

    return {
        "videoId": request.id,
        "title": title,
        "channel": channel,
        "duration": duration,
        **result,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8282)
