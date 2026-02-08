from youtube_transcript_api import YouTubeTranscriptApi
import json

VIDEO_ID = "2E41a_xgHE4"

def test_transcript_api():
    print(f"Fetching transcript for {VIDEO_ID}...")
    try:
        # Instantiate the API
        tta = YouTubeTranscriptApi()
        
        # Get list of transcripts
        print("Listing transcripts...")
        transcript_list = tta.list(VIDEO_ID)
        
        for t in transcript_list:
            print(f"  {t.language_code} ({t.language}) - Generated: {t.is_generated}")
            
        # Try to find English, then Vietnamese
        # prioritized order: Manual En -> Manual Vi -> Auto En -> Auto Vi
        
        target = None
        
        # Manual
        try:
             target = transcript_list.find_manually_created_transcript(['en', 'vi'])
        except:
             pass
        
        # Generated
        if not target:
            try:
                target = transcript_list.find_generated_transcript(['en', 'vi'])
            except:
                pass
        
        # Fallback to any if specific ones not found?
        if not target:
             # Just pick the first one?
             # But transcript_list is iterable
             try:
                 target = next(iter(transcript_list))
             except StopIteration:
                 pass
        
        if target:
            print(f"\nFetching transcript for {target.language_code} ({target.is_generated})...")
            data = target.fetch()
            print("Success!")
            print(f"Lines: {len(data)}")
            # text is in 'text' field of each item
            sample_text = " ".join([item['text'] for item in data[:5]])
            print(f"Sample: {sample_text}")
        else:
             print("No suitable transcript found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_transcript_api()
