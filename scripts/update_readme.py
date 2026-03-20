#!/usr/bin/env python3
"""
update_readme.py — Hourly live README updater for TitoKilonzo/TitoKilonzo
Sections updated: FEATURED_PROJECTS · TECH_NEWS · TECH_BLOGS
"""

import os, re, requests, feedparser
from datetime import datetime
from zoneinfo import ZoneInfo

GITHUB_USERNAME = "TitoKilonzo"
NAIROBI_TZ      = ZoneInfo("Africa/Nairobi")
README_PATH     = "README.md"

# Pinned repos in display order (exact GitHub repo names).
# Add a manual description for repos that have none on GitHub.
PINNED_REPOS = [
    {
        "name": "Bongotoons",
        "fallback_desc": "Netflix-style video streaming platform built with React, Vite, and Appwrite."
    },
    {
        "name": "NexVault",
        "fallback_desc": "Fintech dashboard with React, Node.js/Express, PostgreSQL, and JWT authentication."
    },
    {
        "name": "CyberScribe",
        "fallback_desc": "Open-source cybersecurity skills library — 700+ structured Markdown definitions across 16 domains."
    },
    {
        "name": "shift_master",
        "fallback_desc": "Cross-platform mobile app for work shift management built with Flutter and Dart."
    },
    {
        "name": "ChatBot",
        "fallback_desc": "Intelligent Python chatbot with NLP capabilities and AI integration."
    },
    {
        "name": "nodejs-weather-app",
        "fallback_desc": "Dynamic weather application with real-time data via a live weather API."
    },
]

LANG_EMOJI = {
    "Python": "🐍", "JavaScript": "🟨", "TypeScript": "🔷",
    "Dart": "🎯",   "HTML": "🌐",       "CSS": "🎨",
    "Java": "☕",   "Go": "🐹",         "Rust": "🦀",
    "Shell": "🐚",
}

NEWS_FEEDS = [
    {"name": "Hacker News",     "url": "https://hnrss.org/frontpage",                    "emoji": "🔶"},
    {"name": "TechCrunch",      "url": "https://techcrunch.com/feed/",                    "emoji": "🟢"},
    {"name": "The Verge",       "url": "https://www.theverge.com/rss/index.xml",          "emoji": "🔵"},
    {"name": "Ars Technica",    "url": "https://feeds.arstechnica.com/arstechnica/index", "emoji": "🟣"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/",          "emoji": "🏛️"},
]

BLOG_FEEDS = [
    {"name": "Dev.to",            "url": "https://dev.to/feed",                        "emoji": "💻"},
    {"name": "freeCodeCamp",      "url": "https://www.freecodecamp.org/news/rss/",     "emoji": "🏕️"},
    {"name": "CSS-Tricks",        "url": "https://css-tricks.com/feed/",               "emoji": "🎨"},
    {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/",     "emoji": "📐"},
    {"name": "LogRocket Blog",    "url": "https://blog.logrocket.com/feed/",           "emoji": "🚀"},
    {"name": "JavaScript",        "url": "https://dev.to/feed/tag/javascript",         "emoji": "⚡"},
    {"name": "Python",            "url": "https://dev.to/feed/tag/python",             "emoji": "🐍"},
    {"name": "AI / Machine Learning", "url": "https://dev.to/feed/tag/machinelearning","emoji": "🤖"},
]

REQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GitHubActions/readme-updater; "
        f"+https://github.com/{GITHUB_USERNAME}/{GITHUB_USERNAME})"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ── helpers ───────────────────────────────────────────────────────────────────

def trim(text: str, n: int = 95) -> str:
    text = text.strip()
    return text if len(text) <= n else text[:n - 3] + "..."

def fetch_feed(info: dict, max_items: int = 5) -> list:
    try:
        r = requests.get(info["url"], headers=REQ_HEADERS, timeout=12)
        r.raise_for_status()
        entries = []
        for e in feedparser.parse(r.content).entries[:max_items]:
            entries.append({"title": trim(e.get("title","Untitled")),
                            "link": e.get("link","#"),
                            "emoji": info["emoji"], "name": info["name"]})
        print(f"  ✅ {info['name']}: {len(entries)} items")
        return entries
    except Exception as ex:
        print(f"  ⚠  {info['name']}: {ex}")
        return []

# ── github projects ───────────────────────────────────────────────────────────

def fetch_projects() -> list:
    token   = os.environ.get("GH_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json",
               "User-Agent": REQ_HEADERS["User-Agent"]}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.get(
            f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
            "?type=public&sort=updated&per_page=100",
            headers=headers, timeout=15)
        r.raise_for_status()
        repo_map = {repo["name"]: repo for repo in r.json()}
        print(f"  ✅ GitHub API: {len(repo_map)} repos")
    except Exception as ex:
        print(f"  ⚠  GitHub API: {ex}")
        return []

    result = []
    for pin in PINNED_REPOS:
        repo = repo_map.get(pin["name"])
        if not repo:
            continue
        lang  = repo.get("language") or "Code"
        # Use GitHub description if it exists, otherwise use our fallback
        desc  = (repo.get("description") or "").strip() or pin.get("fallback_desc", "")
        desc  = trim(desc, 100)
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
        return ""
    lines = []
    for repo in repos:
        topics_str = " ".join(f"`{t}`" for t in repo["topics"]) if repo["topics"] else ""
        demo       = f" &nbsp;|&nbsp; [🌐 Live Demo]({repo['homepage']})" if repo["homepage"] else ""
        lines += [
            f"### {repo['emoji']} [{repo['name']}]({repo['url']})",
            f"> {repo['desc']}",
            f"- **Language:** {repo['lang']} &nbsp;|&nbsp; ⭐ {repo['stars']} &nbsp;|&nbsp; 🍴 {repo['forks']}",
        ]
        if topics_str:
            lines.append(f"- **Topics:** {topics_str}")
        lines.append(f"- [📂 Source Code]({repo['url']}){demo}\n")
    return "\n".join(lines)

# ── feed blocks ───────────────────────────────────────────────────────────────

def build_news_block() -> str:
    lines = [
        "| &nbsp; | Headline | Source |",
        "| :---: | :--- | :---: |",
    ]
    for info in NEWS_FEEDS:
        for item in fetch_feed(info, 5):
            lines.append(f"| {item['emoji']} | [{item['title']}]({item['link']}) | **{item['name']}** |")
    return "\n".join(lines)

def build_blogs_block() -> str:
    lines = []
    for info in BLOG_FEEDS:
        items = fetch_feed(info, 3)
        if not items:
            continue
        lines.append(f"\n#### {info['emoji']} {info['name']}\n")
        for item in items:
            lines.append(f"- [{item['title']}]({item['link']})")
    return "\n".join(lines).lstrip("\n")

# ── readme writer ─────────────────────────────────────────────────────────────

def replace_section(content: str, tag: str, body: str) -> str:
    start = f"<!-- {tag}:START -->"
    end   = f"<!-- {tag}:END -->"
    pat   = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pat.search(content):
        raise ValueError(f"Markers for '{tag}' not found in README.md")
    return pat.sub(f"{start}\n{body}\n{end}", content)

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n🚀 README updater starting...\n")

    print("📦 Fetching GitHub repos...")
    projects_block = build_projects_block(fetch_projects())

    print("\n📰 Fetching tech news...")
    news_block = build_news_block()

    print("\n📝 Fetching dev blogs...")
    blogs_block = build_blogs_block()

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    if projects_block:
        readme = replace_section(readme, "FEATURED_PROJECTS", projects_block)
    readme = replace_section(readme, "TECH_NEWS",  news_block)
    readme = replace_section(readme, "TECH_BLOGS", blogs_block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)

    print("\n✅ Done!")

if __name__ == "__main__":
    main()
