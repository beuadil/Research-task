"""
YouTube transcript collector — no API key needed.

Usage:
  python3 scraper/youtube_transcripts.py

Add video IDs to the VIDEOS list below (the part after ?v= in the URL).
Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ  →  ID is dQw4w9WgXcQ
"""

from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

OUTPUT_DIR = Path("research/youtube-transcripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Format: ("expert-slug", "video-id", "video title for filename")
# Find video IDs by opening a YouTube video and copying the ?v=... part of the URL
VIDEOS = [
    # Aleyda Solis — Crawling Mondays AI episodes (replace IDs with real ones)
    ("aleyda-solis", "REPLACE_VIDEO_ID", "crawling-mondays-ai-seo"),

    # Sam Oh / Ahrefs — AI SEO videos
    ("sam-oh", "REPLACE_VIDEO_ID", "ahrefs-ai-seo-strategy"),

    # Koray Tugberk — technical AI SEO
    ("koray-tugberk", "REPLACE_VIDEO_ID", "koray-ai-seo-entities"),

    # Add more here as you find the video IDs
]


def get_transcript(video_id: str) -> str:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join(chunk["text"] for chunk in transcript)


def main():
    for expert, video_id, title in VIDEOS:
        if video_id == "REPLACE_VIDEO_ID":
            print(f"⚠  Skipping {expert} / {title} — no video ID set yet")
            continue

        print(f"→ Fetching transcript: {expert} / {title} ...")
        try:
            text = get_transcript(video_id)
            out_path = OUTPUT_DIR / f"{expert}-{title}.md"
            out_path.write_text(
                f"# Transcript: {title}\n\nExpert: {expert}\nVideo ID: {video_id}\nURL: https://www.youtube.com/watch?v={video_id}\n\n---\n\n{text}\n",
                encoding="utf-8",
            )
            words = len(text.split())
            print(f"  ✓ Saved {words} words → {out_path}")
        except TranscriptsDisabled:
            print(f"  ✗ Transcripts disabled for {video_id}")
        except NoTranscriptFound:
            print(f"  ✗ No transcript found for {video_id} (try a different video)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\nDone. Files saved to research/youtube-transcripts/")


if __name__ == "__main__":
    main()
