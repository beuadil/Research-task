"""
LinkedIn public post scraper — NO login required, NO account risk.

Strategy:
  - Visits each expert's public LinkedIn profile page (no login)
  - LinkedIn shows 2-3 recent posts before the login wall
  - Falls back to Google search if profile shows nothing

Usage:
  python3 scraper/linkedin_public.py
"""

import asyncio
import re
import time
import urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("research/linkedin-posts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# (slug, linkedin-username, real name for Google fallback)
EXPERTS = [
    ("aleyda-solis",   "aleydasolis",              "Aleyda Solis"),
    ("kevin-indig",    "kevinindig",               "Kevin Indig"),
    ("lily-ray",       "lily-ray-44a9b813",        "Lily Ray"),
    ("cyrus-shepard",  "cyrusshepard",             "Cyrus Shepard"),
    ("chima-mmeje",    "chima-mmeje",              "Chima Mmeje"),
    ("bernard-huang",  "bernardhuang",             "Bernard Huang"),
    ("kyle-roof",      "kyleroof",                 "Kyle Roof"),
    ("koray-tugberk",  "koraytugberkgubur",        "Koray Tugberk"),
    ("ryan-law",       "ryan-a-law",               "Ryan Law"),
    ("sam-oh",         "samoh",                    "Sam Oh"),
]

MAX_POSTS = 5


async def scroll_and_collect(page) -> list[str]:
    """Scroll page and collect visible post text blocks."""
    for _ in range(4):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)

    selectors = [
        ".feed-shared-update-v2__description-wrapper",
        ".update-components-text",
        ".feed-shared-text",
        ".attributed-text-segment-list__content",
        "span[dir='ltr']",
    ]
    posts = []
    for sel in selectors:
        elements = await page.query_selector_all(sel)
        for el in elements:
            text = (await el.inner_text()).strip()
            if len(text) > 100:
                posts.append(text)
        if posts:
            break
    return list(dict.fromkeys(posts))[:MAX_POSTS]


async def try_profile_page(page, username: str) -> list[str]:
    """Visit the public LinkedIn profile and grab visible posts."""
    url = f"https://www.linkedin.com/in/{username}/recent-activity/shares/"
    print(f"  Trying profile: {url}")
    await page.goto(url, timeout=30000)
    await page.wait_for_timeout(3000)
    return await scroll_and_collect(page)


async def try_google_fallback(page, name: str) -> list[dict]:
    """Search Google for LinkedIn posts by this person."""
    query = f'site:linkedin.com/posts "{name}" SEO AI'
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query) + "&num=10"
    print(f"  Trying Google: {query}")
    await page.goto(url, timeout=30000)
    await page.wait_for_timeout(2000)

    # Extract LinkedIn post URLs from Google results
    links = await page.evaluate("""() => {
        const anchors = document.querySelectorAll('a[href]');
        const found = [];
        for (const a of anchors) {
            const h = a.href;
            if (h.includes('linkedin.com/posts/') || h.includes('linkedin.com/feed/update/')) {
                found.push(h);
            }
        }
        return [...new Set(found)];
    }""")

    clean = []
    for link in links:
        if "google.com/url" in link:
            m = re.search(r"[?&]q=([^&]+)", link)
            if m:
                link = urllib.parse.unquote(m.group(1))
        if "linkedin.com" in link:
            clean.append(link)

    posts = []
    for url in clean[:MAX_POSTS]:
        print(f"  Fetching post: {url[:65]}...")
        try:
            await page.goto(url, timeout=20000)
            await page.wait_for_timeout(2000)
            text_chunks = await scroll_and_collect(page)
            text = text_chunks[0] if text_chunks else "[Could not extract]"
            posts.append({"url": url, "text": text})
        except Exception as e:
            posts.append({"url": url, "text": f"[Error: {e}]"})
        await page.wait_for_timeout(1500)

    return posts


async def scrape_expert(page, slug: str, username: str, name: str) -> None:
    print(f"\n→ {name}")

    # Strategy 1: public profile page (no login)
    posts_text = await try_profile_page(page, username)

    if posts_text:
        out_path = OUTPUT_DIR / f"{slug}.md"
        lines = [
            f"# LinkedIn Posts — {name}",
            f"\nSource: https://www.linkedin.com/in/{username}/recent-activity/shares/",
            f"Collected: {time.strftime('%Y-%m-%d')}",
            "\n---",
        ]
        for i, text in enumerate(posts_text, 1):
            lines.append(f"\n## Post {i}\n\n{text}\n\n---")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  ✓ Saved {len(posts_text)} posts via profile page → {out_path}")
        return

    # Strategy 2: Google fallback
    print(f"  Profile page empty, trying Google...")
    posts = await try_google_fallback(page, name)

    out_path = OUTPUT_DIR / f"{slug}.md"
    lines = [
        f"# LinkedIn Posts — {name}",
        f"\nSource: Google search fallback",
        f"Collected: {time.strftime('%Y-%m-%d')}",
        "\n---",
    ]
    if posts:
        for i, post in enumerate(posts, 1):
            lines.append(f"\n## Post {i}\n\n**URL:** {post['url']}\n\n{post['text']}\n\n---")
        print(f"  ✓ Saved {len(posts)} posts via Google → {out_path}")
    else:
        lines.append("\n_No posts found automatically. Please copy manually from LinkedIn._")
        print(f"  ⚠ Nothing found for {name} — add manually")

    out_path.write_text("\n".join(lines), encoding="utf-8")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        print("=" * 60)
        print("LinkedIn Public Scraper — no login needed")
        print("Browser will open. Solve any CAPTCHA manually if shown.")
        print("=" * 60)

        for slug, username, name in EXPERTS:
            try:
                await scrape_expert(page, slug, username, name)
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  ✗ Error for {name}: {e}")

        await browser.close()
        print("\n✅ Done! Check research/linkedin-posts/")
        print("Open each .md file and remove any junk text manually.")


if __name__ == "__main__":
    asyncio.run(main())
