from youtube_transcript_api import YouTubeTranscriptApi

VIDEO_ID = "2E41a_xgHE4"

def test_fallback():
    print(f"Fetching transcript for {VIDEO_ID} using fallback...")
    try:
        # Try to get English or Vietnamese
        # prioritized order: ['en', 'vi']
        # include_generated=True needed? In older versions it might be automatic or separate arg
        
        transcript = YouTubeTranscriptApi.get_transcript(VIDEO_ID, languages=['en', 'vi'])
        
        print("Success!")
        print(f"Lines: {len(transcript)}")
        print(f"Sample: {transcript[:3]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fallback()
