import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url: str):
    """Extract 11-character video ID from watch / shorts / youtu.be / embed / live links"""
    # If the user provides the ID directly
    if re.fullmatch(r'[a-zA-Z0-9_-]{11}', url):
        return url
    pattern = r'(?:v=|/shorts/|/embed/|/live/|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_transcript(url: str, languages=("en")):
    video_id = extract_video_id(url)
    if not video_id:
        print("Invalid link, video ID not found")
        return None

    api = YouTubeTranscriptApi()  # Must create an object first (newer version)

    try:
        try:
            # Try preferred languages first (ordered by priority)
            transcript = api.fetch(video_id, languages=list(languages))
        except NoTranscriptFound:
            # If not available, use the first subtitle language the video has
            first = next(iter(api.list(video_id)))
            print(f"Using subtitle language: {first.language} ({first.language_code})")
            transcript = first.fetch()

        full_text = " ".join(snippet.text for snippet in transcript)

        with open(f"{video_id}_transcript.txt", "w", encoding="utf-8") as f:
            f.write(full_text)

        print(full_text)
        print(f"\nSaved to: {video_id}_transcript.txt")
        return full_text

    except TranscriptsDisabled:
        print(f"Video {video_id} has subtitles disabled")
    except (NoTranscriptFound, StopIteration):
        print(f"Video {video_id} has no subtitles available")
    except Exception as e:
        # Covers cases like IP block, video unavailable, age restriction, etc.
        print(f"An error occurred: {type(e).__name__}: {e}")

# Put the real link here

def input_link():
    while True:
        link = input("Enter the video link you want to read: ")
        print("---")
        get_youtube_transcript(link)
        print("---")
        print()

input_link()
