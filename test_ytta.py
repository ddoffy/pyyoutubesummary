from youtube_transcript_api import YouTubeTranscriptApi
import json

VIDEO_ID = "2E41a_xgHE4"

def test_transcript_api():
    print(f"Fetching transcript for {VIDEO_ID}...")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(VIDEO_ID)
        
        print("Transcript List:")
        for t in transcript_list:
            print(f"  {t.language_code} ({t.language}) - Generated: {t.is_generated}")
            
        # Try to find English or Vietnamese
        # prioritized order: Manual En -> Manual Vi -> Auto En -> Auto Vi
        
        target = None
        
        try:
             target = transcript_list.find_manually_created_transcript(['en', 'vi'])
        except:
             pass
             
        if not target:
            try:
                target = transcript_list.find_generated_transcript(['en', 'vi'])
            except:
                pass
        
        if target:
            print(f"\nFetching transcript for {target.language_code}...")
            data = target.fetch()
            print("Success!")
            print(f"Lines: {len(data)}")
            print(f"Sample: {data[:3]}")
        else:
             print("No suitable transcript found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcript_api()
