#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║         Live Tech Feed Generator — GitHub Profile README                ║
║         Fetches RSS/Atom feeds → Generates SVG cards → Updates README   ║
║         Scheduled: Every Hour via GitHub Actions                         ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import feedparser
import os
import re
import html as html_lib
import textwrap
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────────

GITHUB_USERNAME = "TitoKilonzo"
OUTPUT_DIR      = "assets/feed"
MAX_CARDS       = 2   # cards per category

CATEGORIES = [
    {
        "name":     "AI & Claude",
        "slug":     "ai",
        "icon":     "🤖",
        "color":    "#A78BFA",
        "glow":     "#7C3AED",
        "feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.theverge.com/rss/index.xml",
            "https://venturebeat.com/category/ai/feed/",
        ],
        "keywords": [
            "claude", "anthropic", "llm", "gpt", "gemini", "chatgpt",
            "artificial intelligence", "machine learning", "openai",
            "large language model", "neural network", "deep learning",
            "ai agent", "foundation model", "generative ai",
        ],
    },
    {
        "name":     "Cybersecurity",
        "slug":     "cyber",
        "icon":     "🔐",
        "color":    "#F87171",
        "glow":     "#DC2626",
        "feeds": [
            "https://feeds.feedburner.com/TheHackersNews",
            "https://krebsonsecurity.com/feed/",
            "https://www.schneier.com/feed/atom/",
            "https://www.darkreading.com/rss.xml",
        ],
        "keywords": [
            "security", "cyber", "hack", "vulnerability", "breach",
            "malware", "ransomware", "phishing", "exploit", "threat",
            "zero-day", "cve", "patch", "firewall", "encryption",
            "incident", "intrusion", "spyware", "botnet",
        ],
    },
    {
        "name":     "Tech Advances",
        "slug":     "tech",
        "icon":     "⚡",
        "color":    "#60A5FA",
        "glow":     "#2563EB",
        "feeds": [
            "https://www.wired.com/feed/rss",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://techcrunch.com/feed/",
            "https://feeds.feedburner.com/MITTechnologyReview",
        ],
        "keywords": [
            "technology", "innovation", "breakthrough", "research",
            "quantum", "chip", "semiconductor", "robotics", "space",
            "battery", "electric", "5g", "6g", "biotech", "nanotech",
            "processor", "hardware", "computing",
        ],
    },
    {
        "name":     "Dev Insights",
        "slug":     "dev",
        "icon":     "💻",
        "color":    "#34D399",
        "glow":     "#059669",
        "feeds": [
            "https://dev.to/feed",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://techcrunch.com/feed/",
        ],
        "keywords": [
            "developer", "programming", "code", "software", "api",
            "framework", "open source", "devops", "kubernetes", "docker",
            "rust", "python", "javascript", "typescript", "github",
            "backend", "frontend", "full stack", "microservice",
        ],
    },
]

# ── Text utilities ─────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    if not text:
        return ""
    text = html_lib.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def xe(s: str) -> str:
    """Escape XML/SVG special characters."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


def wrap(text: str, width: int, max_lines: int = 2) -> list[str]:
    text = clean(text)
    lines = textwrap.wrap(text, width=width, max_lines=max_lines, placeholder="…")
    while len(lines) < max_lines:
        lines.append("")
    return lines


def trunc(text: str, n: int) -> str:
    text = clean(text)
    return text if len(text) <= n else text[: n - 1] + "…"


# ── Feed fetching ──────────────────────────────────────────────────────────────

def fetch_articles(category: dict) -> list[dict]:
    articles: list[dict] = []
    seen_titles: set[str] = set()
    kws = [k.lower() for k in category["keywords"]]

    for feed_url in category["feeds"]:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:25]:
                title   = clean(entry.get("title", ""))
                summary = clean(entry.get("summary", entry.get("description", "")))
                if not title:
                    continue

                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in kws):
                    continue
                if title in seen_titles:
                    continue
                seen_titles.add(title)

                # Author resolution
                author = clean(entry.get("author", ""))
                if not author:
                    author = clean(feed.feed.get("title", ""))
                author = trunc(author, 40)

                # Source name
                source = clean(feed.feed.get("title", feed_url.split("/")[2]))

                # Date
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    dt       = datetime(*pub[:6], tzinfo=timezone.utc)
                    date_str = dt.strftime("%b %d, %Y")
                else:
                    date_str = datetime.now(timezone.utc).strftime("%b %d, %Y")

                articles.append(
                    {
                        "title":   title,
                        "summary": trunc(summary, 110),
                        "author":  author,
                        "source":  source,
                        "date":    date_str,
                        "link":    entry.get("link", "#"),
                    }
                )
                if len(articles) >= MAX_CARDS:
                    break
        except Exception as e:
            print(f"    ⚠ Feed error ({feed_url[:60]}): {e}")
            continue

        if len(articles) >= MAX_CARDS:
            break

    return articles[:MAX_CARDS]


# ── SVG card generation ────────────────────────────────────────────────────────

CARD_W = 490

def make_card(article: dict, category: dict, uid: int) -> str:
    color = category["color"]
    glow  = category["glow"]
    icon  = category["icon"]
    cname = xe(category["name"])

    t_lines = wrap(article["title"], 54, 2)
    t1 = xe(t_lines[0])
    t2 = xe(t_lines[1])

    excerpt = article["summary"]
    e_lines = wrap(excerpt, 60, 2)
    e1 = xe(e_lines[0])
    e2 = xe(e_lines[1])

    author  = xe(trunc(article["author"], 38))
    source  = xe(trunc(article["source"], 32))
    date    = xe(article["date"])
    ts      = datetime.now(timezone.utc).strftime("%H:%M UTC")

    # Dynamic height based on content
    has_t2  = bool(t2)
    has_e2  = bool(e2)
    height  = 170 + (has_t2 * 18) + (has_e2 * 16)

    # Y positions
    t1_y    = 57
    t2_y    = t1_y + 18
    auth_y  = (t2_y if has_t2 else t1_y) + 22
    e1_y    = auth_y + 20
    e2_y    = e1_y + 16
    foot_y  = (e2_y if has_e2 else e1_y) + 22

    badge_w = len(category["name"]) * 7 + 32

    svg = f'''\
<svg width="{CARD_W}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg{uid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <filter id="glow{uid}" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{CARD_W}" height="{height}" rx="12" fill="url(#bg{uid})"/>
  <!-- Border -->
  <rect width="{CARD_W}" height="{height}" rx="12" fill="none"
        stroke="{color}" stroke-width="1.2" stroke-opacity="0.35"/>
  <!-- Left accent bar -->
  <rect x="0" y="20" width="3.5" height="{height - 40}" rx="2" fill="{color}"/>
  <!-- Accent corner dot -->
  <circle cx="{CARD_W - 18}" cy="18" r="5" fill="{glow}" fill-opacity="0.6"
          filter="url(#glow{uid})"/>

  <!-- Category badge -->
  <rect x="14" y="12" width="{badge_w}" height="21" rx="10"
        fill="{glow}" fill-opacity="0.18"/>
  <text x="24" y="27"
        font-family="'Segoe UI', 'SF Pro Display', Arial, sans-serif"
        font-size="10.5" font-weight="700" fill="{color}"
        letter-spacing="0.3">{icon} {cname}</text>

  <!-- Title line 1 -->
  <text x="14" y="{t1_y}"
        font-family="'Segoe UI', 'SF Pro Display', Arial, sans-serif"
        font-size="13.5" font-weight="700" fill="#E6EDF3">{t1}</text>
'''

    if has_t2:
        svg += f'''\
  <!-- Title line 2 -->
  <text x="14" y="{t2_y}"
        font-family="'Segoe UI', 'SF Pro Display', Arial, sans-serif"
        font-size="13.5" font-weight="700" fill="#E6EDF3">{t2}</text>
'''

    svg += f'''\
  <!-- Author & date -->
  <text x="14" y="{auth_y}"
        font-family="'Segoe UI', Arial, sans-serif"
        font-size="10.5" fill="{color}">&#9997;&#65039; {author} &#183; {date}</text>
'''

    if e1:
        svg += f'''\
  <!-- Excerpt line 1 -->
  <text x="14" y="{e1_y}"
        font-family="'Segoe UI', Georgia, serif"
        font-size="11" fill="#8B949E" font-style="italic">&#8220;{e1}</text>
'''
    if has_e2:
        svg += f'''\
  <!-- Excerpt line 2 -->
  <text x="14" y="{e2_y}"
        font-family="'Segoe UI', Georgia, serif"
        font-size="11" fill="#8B949E" font-style="italic">{e2}&#8221;</text>
'''
    elif e1:
        # close the quote on same line — patch line 1
        svg = svg.replace(f">&#8220;{e1}</text>", f">&#8220;{e1}&#8221;</text>")

    svg += f'''\
  <!-- Footer -->
  <line x1="14" y1="{foot_y - 8}" x2="{CARD_W - 14}" y2="{foot_y - 8}"
        stroke="#21262d" stroke-width="1"/>
  <text x="14" y="{foot_y + 5}"
        font-family="'Courier New', 'Fira Code', monospace"
        font-size="9.5" fill="#484F58">&#128279; {source} &#183; &#128336; Updated {ts}</text>

</svg>'''

    return svg


def make_placeholder(category: dict, uid: int) -> str:
    color  = category["color"]
    glow   = category["glow"]
    icon   = category["icon"]
    cname  = xe(category["name"])
    ts     = datetime.now(timezone.utc).strftime("%H:%M UTC")
    height = 120

    return f'''\
<svg width="{CARD_W}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="pbg{uid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
  </defs>
  <rect width="{CARD_W}" height="{height}" rx="12" fill="url(#pbg{uid})"/>
  <rect width="{CARD_W}" height="{height}" rx="12" fill="none"
        stroke="{glow}" stroke-width="1" stroke-opacity="0.3" stroke-dasharray="6,4"/>
  <rect x="0" y="20" width="3.5" height="{height - 40}" rx="2" fill="{color}"/>
  <text x="{CARD_W // 2}" y="48"
        font-family="'Segoe UI', Arial, sans-serif"
        font-size="26" text-anchor="middle">{icon}</text>
  <text x="{CARD_W // 2}" y="72"
        font-family="'Segoe UI', Arial, sans-serif"
        font-size="12" fill="#8B949E" text-anchor="middle">
    Fetching latest {cname} news…
  </text>
  <text x="{CARD_W // 2}" y="92"
        font-family="'Courier New', monospace"
        font-size="9.5" fill="#484F58" text-anchor="middle">&#128336; {ts}</text>
</svg>'''


# ── README timestamp update ────────────────────────────────────────────────────

def update_readme(path: str = "README.md") -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        content = f.read()

    ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d at %H:%M UTC")
    mark  = "<!-- FEED_TIMESTAMP -->"
    repl  = f"{mark}\n> 🕐 **Live Feed Last Refreshed:** `{ts}` — updates automatically every hour via GitHub Actions."

    if mark in content:
        content = re.sub(
            rf"{re.escape(mark)}.*?(?=\n##|\Z)",
            repl + "\n\n",
            content,
            flags=re.DOTALL,
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ README timestamp updated → {ts}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'═'*60}")
    print(f"  🚀  Live Tech Feed Update  ·  {now}")
    print(f"{'═'*60}\n")

    uid = 0
    for cat in CATEGORIES:
        print(f"📡  {cat['name']}")
        articles = fetch_articles(cat)

        for i in range(1, MAX_CARDS + 1):
            uid += 1
            path = os.path.join(OUTPUT_DIR, f"{cat['slug']}_card_{i}.svg")
            if i <= len(articles):
                art = articles[i - 1]
                svg = make_card(art, cat, uid)
                print(f"    ✔  Card {i}: {art['title'][:55]}…")
            else:
                svg = make_placeholder(cat, uid)
                print(f"    ○  Card {i}: placeholder (no matching article)")

            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)

    update_readme()
    print(f"\n{'═'*60}")
    print(f"  ✨  Done — {uid} cards written to {OUTPUT_DIR}/")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()
