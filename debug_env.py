import sys
import os
import youtube_transcript_api

print(f"Python executable: {sys.executable}")
print(f"Version: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    print(f"youtube_transcript_api file: {youtube_transcript_api.__file__}")
    print(f"dir(youtube_transcript_api): {dir(youtube_transcript_api)}")
    
    from youtube_transcript_api import YouTubeTranscriptApi
    print(f"YouTubeTranscriptApi: {YouTubeTranscriptApi}")
    print(f"dir(YouTubeTranscriptApi): {dir(YouTubeTranscriptApi)}")
except Exception as e:
    print(f"Import Error: {e}")
