import json
import os
import re
from typing import Optional

from google import genai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="YouTube Summary API")


class SummaryRequest(BaseModel):
    id: str
    format: str = "json"
    cookies: Optional[str] = None
    userAgent: Optional[str] = None


def extract_transcript(video_id: str, cookies: Optional[str], user_agent: Optional[str]) -> tuple[str, str, str, str]:
    """Extract transcript and metadata from a YouTube video."""
    
    # 1. Get Metadata using yt-dlp (metadata only, no subtitles download)
    url = f"https://www.youtube.com/watch?v={video_id}"
    video_title = "Unknown"
    video_channel = "Unknown"
    video_duration = "Unknown"

    try:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "format": "bestaudio/best",
            "ignore_no_formats_error": True,
        }
        if user_agent:
            ydl_opts["http_headers"] = {"User-Agent": user_agent}
        
        # We don't use cookies for metadata to avoid complexity, usually strictly generic metadata is fine.
        # If restricted, it might fail, but currently user is facing subtitle 429s which are distinct.

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                video_title = info.get("title", "Unknown")
                video_channel = info.get("channel", info.get("uploader", "Unknown"))
                video_duration = info.get("duration_string", "Unknown")
    except Exception as e:
        print(f"Metadata extraction warning: {e}")
        # Continue to try transcript even if metadata fails (though unlikely)

    # 2. Get Transcript using youtube-transcript-api
    try:
        tta = YouTubeTranscriptApi()
        transcript_list = tta.list(video_id)
        
        target = None
        
        # Priority: Manual English -> Manual Native (Vietnamese etc) -> Auto English -> Auto Native -> Any
        # We try to find specific languages first
        priority_langs = ['en', 'vi'] 
        
        # 1. Manual
        try:
            target = transcript_list.find_manually_created_transcript(priority_langs)
        except:
            pass
            
        # 2. Generated
        if not target:
            try:
                target = transcript_list.find_generated_transcript(priority_langs)
            except:
                pass
        
        # 3. Fallback to any
        if not target:
            try:
                # iterating gives us available transcripts, pick first
                target = next(iter(transcript_list))
            except StopIteration:
                pass
                
        if not target:
            raise HTTPException(status_code=422, detail="No suitable transcript found")

        # Fetch
        transcript_data = target.fetch()
        
        # transcript_data is a list of objects with .text attribute
        # We need to join them
        segments = []
        for item in transcript_data:
            # Check if it's an object or dict (based on installed version ambiguity)
            text = ""
            if hasattr(item, 'text'):
                text = item.text
            elif isinstance(item, dict) and 'text' in item:
                text = item['text']
            
            if text:
                segments.append(text)
                
        transcript = " ".join(segments)
        transcript = re.sub(r"\s+", " ", transcript).strip()
        
        if not transcript:
             raise HTTPException(status_code=422, detail="Transcript is empty")
             
        return transcript, video_title, video_channel, video_duration

    except Exception as e:
        # Map specific exceptions if possible, otherwise generic 500 or 422
        # If it's a 404/VideoUnavailable from library
        error_msg = str(e)
        if "VideoUnavailable" in error_msg:
             raise HTTPException(status_code=404, detail="Video unavailable")
        elif "NoTranscriptFound" in error_msg:
             raise HTTPException(status_code=422, detail="No transcript found")
        else:
             print(f"Transcript error: {e}")
             raise HTTPException(status_code=500, detail=f"Failed to fetch transcript: {e}")


def summarize_with_gemini(
    transcript: str, title: str, channel: str, duration: str
) -> dict:
    """Summarize the transcript using Google Gemini API."""

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

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
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
