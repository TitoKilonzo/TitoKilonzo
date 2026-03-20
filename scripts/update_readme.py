#!/usr/bin/env python3
"""
update_readme.py — Hourly live README updater for TitoKilonzo/TitoKilonzo
  • Pulls top GitHub repos via GitHub API   → Featured Projects section
  • Pulls tech news & blog RSS feeds        → Live Feed sections
  v2 — fixed: proper request headers, no infinite push loop, GitHub API projects
"""

import os
import re
import requests
import feedparser
from datetime import datetime
from zoneinfo import ZoneInfo

# ─── CONFIG ───────────────────────────────────────────────────────────────────

GITHUB_USERNAME = "TitoKilonzo"
NAIROBI_TZ      = ZoneInfo("Africa/Nairobi")
README_PATH     = "README.md"

# Repos to always pin (exact repo names on GitHub). Shown in this order.
PINNED_REPOS = [
    "Bongotoons",
    "NexVault",
    "shift_master",
    "CyberScribe",
    "ChatBot",
    "nodejs-weather-app",
]

LANG_EMOJI = {
    "Python": "🐍", "JavaScript": "🟨", "TypeScript": "🔷",
    "Dart": "🎯",   "HTML": "🌐",       "CSS": "🎨",
    "Java": "☕",   "Go": "🐹",         "Rust": "🦀",
    "Shell": "🐚",  "C": "⚙️",          "C++": "⚙️",
}

NEWS_FEEDS = [
    {"name": "Hacker News",      "url": "https://hnrss.org/frontpage",                    "emoji": "🔶"},
    {"name": "TechCrunch",       "url": "https://techcrunch.com/feed/",                    "emoji": "🟢"},
    {"name": "The Verge",        "url": "https://www.theverge.com/rss/index.xml",          "emoji": "🔵"},
    {"name": "Ars Technica",     "url": "https://feeds.arstechnica.com/arstechnica/index", "emoji": "🟣"},
    {"name": "MIT Tech Review",  "url": "https://www.technologyreview.com/feed/",          "emoji": "🏛️"},
]

BLOG_FEEDS = [
    {"name": "Dev.to",            "url": "https://dev.to/feed",                        "emoji": "💻"},
    {"name": "freeCodeCamp",      "url": "https://www.freecodecamp.org/news/rss/",     "emoji": "🏕️"},
    {"name": "CSS-Tricks",        "url": "https://css-tricks.com/feed/",               "emoji": "🎨"},
    {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/",     "emoji": "📐"},
    {"name": "LogRocket Blog",    "url": "https://blog.logrocket.com/feed/",           "emoji": "🚀"},
    {"name": "DEV: JavaScript",   "url": "https://dev.to/feed/tag/javascript",         "emoji": "⚡"},
    {"name": "DEV: Python",       "url": "https://dev.to/feed/tag/python",             "emoji": "🐍"},
    {"name": "DEV: AI / ML",      "url": "https://dev.to/feed/tag/machinelearning",    "emoji": "🤖"},
]

REQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GitHubActions/readme-updater; "
        f"+https://github.com/{GITHUB_USERNAME}/{GITHUB_USERNAME})"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def now_str() -> str:
    now = datetime.now(tz=NAIROBI_TZ)
    return now.strftime("%a %d %b %Y · %I:%M %p EAT")


def trim(text: str, max_len: int = 90) -> str:
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def fetch_feed(feed_info: dict, max_items: int = 5) -> list:
    """Fetch RSS using requests (for proper headers) then parse with feedparser."""
    try:
        resp = requests.get(feed_info["url"], headers=REQ_HEADERS, timeout=12)
        resp.raise_for_status()
        parsed  = feedparser.parse(resp.content)
        entries = []
        for entry in parsed.entries[:max_items]:
            title = trim(entry.get("title", "Untitled"))
            link  = entry.get("link", "#")
            entries.append({"title": title, "link": link,
                             "source": feed_info["name"], "emoji": feed_info["emoji"]})
        print(f"  ✅ {feed_info['name']}: {len(entries)} items")
        return entries
    except Exception as exc:
        print(f"  ⚠  {feed_info['name']}: {exc}")
        return []


# ─── GITHUB PROJECTS ──────────────────────────────────────────────────────────

def fetch_github_repos() -> list:
    token   = os.environ.get("GH_TOKEN", "")
    gh_hdrs = {"Accept": "application/vnd.github.v3+json", "User-Agent": REQ_HEADERS["User-Agent"]}
    if token:
        gh_hdrs["Authorization"] = f"Bearer {token}"

    url = (f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
           "?type=public&sort=updated&per_page=100")
    try:
        resp = requests.get(url, headers=gh_hdrs, timeout=15)
        resp.raise_for_status()
        all_repos = resp.json()
        print(f"  ✅ GitHub API: {len(all_repos)} repos fetched")
    except Exception as exc:
        print(f"  ⚠  GitHub API failed: {exc}")
        return []

    if PINNED_REPOS:
        repo_map = {r["name"]: r for r in all_repos}
        repos    = [repo_map[n] for n in PINNED_REPOS if n in repo_map]
        if len(repos) < 6:
            extras = sorted(
                [r for r in all_repos if r["name"] not in PINNED_REPOS],
                key=lambda r: r["stargazers_count"], reverse=True
            )
            repos += extras[:6 - len(repos)]
    else:
        repos = sorted(all_repos, key=lambda r: r["stargazers_count"], reverse=True)[:6]

    result = []
    for repo in repos:
        lang  = repo.get("language") or "Code"
        desc  = trim(repo.get("description") or "No description provided.", 100)
        result.append({
            "name":     repo["name"],
            "desc":     desc,
            "url":      repo["html_url"],
            "homepage": repo.get("homepage") or "",
            "lang":     lang,
            "emoji":    LANG_EMOJI.get(lang, "📦"),
            "stars":    repo.get("stargazers_count", 0),
            "forks":    repo.get("forks_count", 0),
            "topics":   repo.get("topics", [])[:4],
        })
    return result


def build_projects_block(repos: list) -> str:
    if not repos:
        return "> ⚠️ Could not fetch repositories at this time.\n"

    lines = [f"> 🤖 **Auto-fetched from GitHub API** · Updated `{now_str()}`\n"]
    for repo in repos:
        topics_str = " ".join(f"`{t}`" for t in repo["topics"]) if repo["topics"] else ""
        demo_link  = f" · [🌐 Live Demo]({repo['homepage']})" if repo["homepage"] else ""
        lines += [
            f"### {repo['emoji']} [{repo['name']}]({repo['url']})",
            f"> {repo['desc']}",
            f"- **Language:** {repo['lang']}  **Stars:** ⭐ {repo['stars']}  **Forks:** 🍴 {repo['forks']}",
        ]
        if topics_str:
            lines.append(f"- **Topics:** {topics_str}")
        lines.append(f"- [📂 Source Code]({repo['url']}){demo_link}\n")
    return "\n".join(lines)


# ─── LIVE FEED BLOCKS ─────────────────────────────────────────────────────────

def build_news_block() -> str:
    lines = [
        f"> 🕐 **Last updated:** `{now_str()}`  ·  Auto-refreshes every hour\n",
        "| &nbsp; | Headline | Source |",
        "| :---: | :--- | :---: |",
    ]
    for feed in NEWS_FEEDS:
        for item in fetch_feed(feed, max_items=5):
            lines.append(f"| {item['emoji']} | [{item['title']}]({item['link']}) | **{item['source']}** |")
    return "\n".join(lines)


def build_blogs_block() -> str:
    lines = [f"> 📡 **Live feed from top dev blogs** · Updated `{now_str()}`\n"]
    for feed in BLOG_FEEDS:
        items = fetch_feed(feed, max_items=3)
        if not items:
            continue
        lines.append(f"\n#### {feed['emoji']} {feed['name']}\n")
        for item in items:
            lines.append(f"- [{item['title']}]({item['link']})")
    return "\n".join(lines)


# ─── README WRITER ────────────────────────────────────────────────────────────

def replace_section(content: str, tag: str, body: str) -> str:
    start = f"<!-- {tag}:START -->"
    end   = f"<!-- {tag}:END -->"
    pat   = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pat.search(content):
        raise ValueError(f"Markers for '{tag}' not found in README.md")
    return pat.sub(f"{start}\n{body}\n{end}", content)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n🚀 README updater v2 starting...\n")

    print("📦 Fetching GitHub repos...")
    repos          = fetch_github_repos()
    projects_block = build_projects_block(repos)

    print("\n📰 Fetching tech news...")
    news_block  = build_news_block()

    print("\n📝 Fetching dev blogs...")
    blogs_block = build_blogs_block()

    print(f"\n✍️  Writing {README_PATH}...")
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    readme = replace_section(readme, "FEATURED_PROJECTS", projects_block)
    readme = replace_section(readme, "TECH_NEWS",         news_block)
    readme = replace_section(readme, "TECH_BLOGS",        blogs_block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
