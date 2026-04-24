"""
YouTube transcript collector — no API key needed.

Usage:
  python3 scraper/youtube_transcripts.py

Experts: Matt Diggity, Julian Goldie, Nathan Gotch — all focused on AI-powered SEO.
"""

import time
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

OUTPUT_DIR = Path("research/youtube-transcripts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Format: ("expert-slug", "video-id", "video title")
# These are AI-SEO focused videos from each creator
VIDEOS = [
    # Matt Diggity — data-driven AI SEO experiments
    ("matt-diggity", "xG9Vu9yrQzw", "i-let-ai-run-my-seo-campaign"),
    ("matt-diggity", "4GBlHObjOrY", "ai-seo-for-chatgpt-and-google-ai"),

    # Julian Goldie — AI SEO workflow automation
    ("julian-goldie", "WhLyFjzbzvQ", "rank-1-with-perplexity-parasite-ai-seo-2026"),
    ("julian-goldie", "fjwu45wqgx0", "rank-1-with-perplexity-parasite-ai-seo"),

    # Nathan Gotch (GotchSEO) — systematic AI SEO strategy
    ("nathan-gotch", "QLpSxF4armY", "seo-is-dead-debunking-with-ai-insights"),
    ("nathan-gotch", "mbCfRlY7elM", "6-ai-seo-skills-that-matter-most-2026"),
]


def get_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return " ".join(chunk.text for chunk in transcript)


def main():
    success = 0
    for expert, video_id, title in VIDEOS:
        print(f"→ {expert} / {title} (ID: {video_id}) ...")
        try:
            text = get_transcript(video_id)
            out_path = OUTPUT_DIR / f"{expert}-{title}.md"
            out_path.write_text(
                f"# Transcript: {title}\n\n"
                f"Expert: {expert}\n"
                f"Video ID: {video_id}\n"
                f"URL: https://www.youtube.com/watch?v={video_id}\n"
                f"Collected: {time.strftime('%Y-%m-%d')}\n\n"
                f"---\n\n{text}\n",
                encoding="utf-8",
            )
            words = len(text.split())
            print(f"  ✓ Saved {words:,} words → {out_path}")
            success += 1
        except TranscriptsDisabled:
            print(f"  ✗ Transcripts disabled for this video — try a different one")
        except NoTranscriptFound:
            print(f"  ✗ No transcript available — try a different video")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\nDone. {success}/{len(VIDEOS)} transcripts saved to research/youtube-transcripts/")


if __name__ == "__main__":
    main()
