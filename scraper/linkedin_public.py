"""
LinkedIn public post scraper — NO login required, NO account risk.

Strategy:
  - Searches Google for recent (past year) LinkedIn posts by each expert
  - Filters strictly for AI + SEO related content
  - Falls back to broader search if narrow search returns nothing

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

# (slug, linkedin-username, display name)
EXPERTS = [
    ("aleyda-solis",  "aleydasolis",         "Aleyda Solis"),
    ("kevin-indig",   "kevinindig",          "Kevin Indig"),
    ("lily-ray",      "lily-ray-44a9b813",   "Lily Ray"),
    ("cyrus-shepard", "cyrusshepard",        "Cyrus Shepard"),
    ("chima-mmeje",   "chima-mmeje",         "Chima Mmeje"),
    ("bernard-huang", "bernardjhuang",       "Bernard Huang"),
    ("kyle-roof",     "kyle-roof-seo",       "Kyle Roof"),
    ("koray-tugberk", "koray-tugberk-gubur", "Koray Tugberk"),
    ("ryan-law",      "thinkingslow",        "Ryan Law"),
    ("sam-oh",        "sam-o-84593014",      "Sam Oh Ahrefs"),
]

MAX_POSTS = 5

# Keywords that must appear in post text to be kept
AI_SEO_KEYWORDS = [
    "ai", "seo", "llm", "chatgpt", "search", "content", "generative",
    "artificial intelligence", "geo", "aeo", "overviews", "topical",
]


def is_relevant(text: str) -> bool:
    """Check if post is related to AI or SEO."""
    lower = text.lower()
    hits = sum(1 for kw in AI_SEO_KEYWORDS if kw in lower)
    return hits >= 2


def google_url(query: str, past_year: bool = True) -> str:
    params = {"q": query, "num": "10"}
    if past_year:
        params["tbs"] = "qdr:y"   # past year filter
    return "https://www.google.com/search?" + urllib.parse.urlencode(params)


async def extract_linkedin_links(page) -> list[str]:
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
    return clean


async def get_post_text(page, url: str) -> str:
    try:
        await page.goto(url, timeout=20000)
        await page.wait_for_timeout(2500)
        for sel in [
            ".attributed-text-segment-list__content",
            ".feed-shared-update-v2__description-wrapper",
            ".update-components-text",
            ".feed-shared-text",
            "article",
        ]:
            el = await page.query_selector(sel)
            if el:
                text = (await el.inner_text()).strip()
                if len(text) > 80:
                    return text
        # fallback: grab meaningful lines from body
        body = await page.inner_text("body")
        lines = [l.strip() for l in body.splitlines() if len(l.strip()) > 60]
        return "\n".join(lines[:25]) if lines else ""
    except Exception as e:
        return f"[Error: {e}]"


async def search_and_collect(page, slug: str, username: str, name: str) -> list[dict]:
    """Try multiple Google searches, narrowing to AI SEO, recent first."""
    searches = [
        # Most specific: their LinkedIn username + AI SEO keywords, past year
        (f'site:linkedin.com/posts/{username} "AI" "SEO"', True),
        # Broader: their name + AI SEO, past year
        (f'site:linkedin.com/posts "{name}" "AI" "SEO"', True),
        # No time filter fallback
        (f'site:linkedin.com/posts "{name}" SEO AI', False),
    ]

    all_links = []
    for query, past_year in searches:
        url = google_url(query, past_year)
        print(f"  Google: {query[:70]}...")
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(2000)
        links = await extract_linkedin_links(page)
        all_links.extend(links)
        if len(all_links) >= MAX_POSTS:
            break
        await page.wait_for_timeout(1500)

    # Deduplicate
    seen = set()
    unique = []
    for l in all_links:
        if l not in seen:
            seen.add(l)
            unique.append(l)

    posts = []
    for url in unique[:MAX_POSTS + 3]:   # fetch a few extra so we can filter
        print(f"  Fetching: {url[:65]}...")
        text = await get_post_text(page, url)
        if not text or text.startswith("[Error"):
            continue
        if is_relevant(text):
            posts.append({"url": url, "text": text})
        else:
            print(f"    ↳ skipped (not AI/SEO related)")
        await page.wait_for_timeout(1500)
        if len(posts) >= MAX_POSTS:
            break

    return posts


async def scrape_expert(page, slug: str, username: str, name: str) -> None:
    print(f"\n→ {name}")
    posts = await search_and_collect(page, slug, username, name)

    out_path = OUTPUT_DIR / f"{slug}.md"
    lines = [
        f"# LinkedIn Posts — {name}",
        f"\nProfile: https://www.linkedin.com/in/{username}/",
        f"Collected: {time.strftime('%Y-%m-%d')}",
        f"Filter: AI + SEO related posts, past 12 months",
        "\n---",
    ]

    if posts:
        for i, post in enumerate(posts, 1):
            lines.append(f"\n## Post {i}\n\n**URL:** {post['url']}\n\n{post['text']}\n\n---")
        print(f"  ✓ Saved {len(posts)} relevant posts → {out_path}")
    else:
        lines.append("\n_No AI/SEO posts found automatically. Please add manually._")
        print(f"  ⚠ Nothing found for {name}")

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
        print("LinkedIn Public Scraper — AI SEO posts, past year")
        print("Browser will open. Solve any CAPTCHA manually if shown.")
        print("=" * 60)

        for slug, username, name in EXPERTS:
            try:
                await scrape_expert(page, slug, username, name)
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"  ✗ Error for {name}: {e}")

        await browser.close()
        print("\n✅ Done! Files saved to research/linkedin-posts/")


if __name__ == "__main__":
    asyncio.run(main())
