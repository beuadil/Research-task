# 100Hires Portfolio Project

## Step 1 — Developer Environment Setup

### Tools Installed

- **Cursor IDE** — [cursor.com](https://cursor.com/)
- **Codex** (Cursor Extension) — used as the AI coding assistant after encountering a Claude Code login issue (see below)
- **GitHub** — public repository created and connected to Cursor

### Steps Completed

1. Downloaded and installed Cursor IDE
2. Searched for and installed the Codex extension via Cursor's Extensions panel
3. Created a public GitHub repository
4. Opened the repository locally in Cursor
5. Created this README.md file and pushed it to GitHub
6. Updated the README.md further using terminal commands (git add, commit, push) — without touching the GitHub website
7. Applied the same terminal workflow for all subsequent edits

### Issues & How I Solved Them

**Issue 1: Claude Code required Claude Pro**
The Claude Code extension requires an active Claude Pro subscription to log in. Since I didn't have one, I pivoted to the **Codex** extension as an alternative AI coding assistant, which covers the same core functionality for this task.

**Issue 2: Editing README via GitHub's website**
My first instinct was to edit the README directly on GitHub's site. Instead, I learned how to edit the file locally in Cursor, then stage, commit, and push the updates via the terminal — which is the proper developer workflow. Applied this approach for all subsequent edits.

**Issue 3: Changes weren't showing up on GitHub**
After making my commits, the updates weren't appearing on GitHub. I investigated and realized I had forgotten to run `git push` — the commits were saved locally but never sent to the remote repository. Once I ran the push command, everything synced correctly.

---

## Step 2 — Research Project: AI-Powered SEO Content Production

### Topic chosen

**AI-powered SEO content production** — how practitioners use AI tools to research, write, optimize, and scale SEO content while maintaining quality and rankings.

I chose this topic because it sits at the intersection of two areas that are changing fast at the same time: AI writing tools and search engine algorithms. The playbook for doing this well is still being figured out in public, which makes it the right time to study who is doing it seriously.

---

### What I collected

| Type | Count | Location |
|------|-------|----------|
| LinkedIn posts | 35 posts across 7 experts | `research/linkedin-posts/` |
| YouTube transcripts | 6 transcripts across 3 creators | `research/youtube-transcripts/` |
| Sources index | 10 experts annotated | `research/sources.md` |

**Collection method:**
- LinkedIn posts collected via public Google search (`site:linkedin.com/posts/`) using a Playwright script — no LinkedIn login used, no account risk
- YouTube transcripts pulled using `youtube-transcript-api` Python library — no API key required
- Scripts are in `scraper/linkedin_public.py` and `scraper/youtube_transcripts.py`

---

### The 10 experts and why I chose them

#### LinkedIn Practitioners

| Expert | Role | Why chosen |
|--------|------|------------|
| **Aleyda Solis** | Independent SEO consultant | Advises top global brands on AI search. Posts weekly data-backed frameworks on GEO, AEO, and LLM citation strategies. One of the most rigorous voices in the field. |
| **Kevin Indig** | Growth advisor (ex-Shopify, G2, Atlassian) | Coined "AI Brand Archetype." Publishes Growth Memo newsletter. Tracks how LLMs evaluate brands differently from Google. |
| **Bernard Huang** | Co-founder, Clearscope | Builds the tools SEOs use for AI content optimization. Posts detailed breakdowns of how GPT, Gemini, and Perplexity behave differently as search engines. |
| **Kyle Roof** | Founder, PageOptimizer Pro | Runs controlled SEO experiments nobody else does. Tested 13 LLMs for SEO content quality and published the data. Separates himself from opinion-based commentators with actual numbers. |
| **Koray Tugberk Gubur** | Founder, Holistic SEO | Pioneer of topical authority methodology that predicted how LLMs would process content. His semantic SEO framework is now central to AI search optimization. |
| **Ryan Law** | Director of Content, Ahrefs | Built a 10-step AI content machine at Ahrefs. One of the most honest voices on when AI content is and isn't good enough — challenges hype with nuance. |
| **Sam Oh** | VP Marketing, Ahrefs | Leads Ahrefs' YouTube engine (5M+ views/year). Practical perspective on AI-era content strategy from a company at $100M+ ARR without traditional marketing. |

#### YouTube Creators

| Expert | Channel | Why chosen |
|--------|---------|------------|
| **Matt Diggity** | [@MattDiggity](https://www.youtube.com/@MattDiggity) | Runs real-world AI SEO experiments on affiliate sites with published ranking results. Data-first approach, not theory. |
| **Julian Goldie** | [@JulianGoldieSEO](https://www.youtube.com/@JulianGoldieSEO) | Publishes step-by-step AI SEO workflows. Covers emerging tactics like Perplexity parasite SEO before they go mainstream. High output, fast-moving. |
| **Nathan Gotch** | [@GotchSEO](https://www.youtube.com/@GotchSEO) | Systematic thinker who turns complex AI SEO shifts into actionable skill frameworks. Covers both strategic and execution-level changes. |

---

### Repository structure

```
research/
├── sources.md                            # All 10 experts with links and annotations
├── linkedin-posts/
│   ├── aleyda-solis.md
│   ├── kevin-indig.md
│   ├── bernard-huang.md
│   ├── kyle-roof.md
│   ├── koray-tugberk.md
│   ├── ryan-law.md
│   └── sam-oh.md
└── youtube-transcripts/
    ├── matt-diggity-i-let-ai-run-my-seo-campaign.md
    ├── matt-diggity-ai-seo-for-chatgpt-and-google-ai.md
    ├── julian-goldie-rank-1-with-perplexity-parasite-ai-seo-2026.md
    ├── julian-goldie-rank-1-with-perplexity-parasite-ai-seo.md
    ├── nathan-gotch-seo-is-dead-debunking-with-ai-insights.md
    └── nathan-gotch-6-ai-seo-skills-that-matter-most-2026.md

scraper/
├── linkedin_public.py                    # LinkedIn post collector (no login)
└── youtube_transcripts.py               # YouTube transcript collector
```
