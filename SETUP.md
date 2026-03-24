# 🚀 GitHub Profile — Live Tech Feed Setup Guide

## What's Inside

```
github-profile-live/
├── README.md                        ← Your profile README (copy to TitoKilonzo/TitoKilonzo)
├── .github/
│   └── workflows/
│       ├── update-feed.yml          ← ⏰ Runs EVERY HOUR — fetches tech news, renders SVG cards
│       └── update-stats.yml         ← 📊 Runs DAILY   — caches GitHub stats SVGs locally
├── scripts/
│   ├── update_feed.py               ← Main feed logic (RSS → SVG cards)
│   ├── update_stats.py              ← Stats caching logic
│   └── requirements.txt             ← feedparser==6.0.11
└── assets/
    ├── feed/                        ← 8 auto-generated SVG cards (2 per category)
    │   ├── ai_card_1.svg  ai_card_2.svg
    │   ├── cyber_card_1.svg  cyber_card_2.svg
    │   ├── tech_card_1.svg  tech_card_2.svg
    │   └── dev_card_1.svg  dev_card_2.svg
    └── github-stats/                ← Cached GitHub stats SVGs
        ├── stats.svg
        ├── top-langs.svg
        └── streak.svg
```

---

## One-Time Setup (5 minutes)

### Step 1 — Create your profile repo

Your GitHub profile README lives in a special repo named **exactly** the same as your username.

1. Go to **github.com/new**
2. Set repository name to: `TitoKilonzo`
3. Check ✅ **Public**
4. Check ✅ **Add a README file**
5. Click **Create repository**

### Step 2 — Upload files

Option A — **GitHub Web UI** (easiest):
1. Open your new repo at `github.com/TitoKilonzo/TitoKilonzo`
2. Click **Add file → Upload files**
3. Drag and drop the entire contents of this folder (not the folder itself)
4. Commit directly to `main`

Option B — **Git CLI**:
```bash
git clone https://github.com/TitoKilonzo/TitoKilonzo.git
cd TitoKilonzo

# Copy everything from this folder into it
cp -r /path/to/github-profile-live/. .

git add -A
git commit -m "🚀 initial: live tech feed profile setup"
git push origin main
```

### Step 3 — Enable GitHub Actions write permission

1. Go to your repo → **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select ✅ **Read and write permissions**
4. Click **Save**

### Step 4 — Trigger the first run

1. Go to **Actions** tab in your repo
2. Click **🔴 Live Tech Feed — Hourly Refresh**
3. Click **Run workflow** → **Run workflow**
4. Watch it fetch news and generate your SVG cards live!
5. Repeat for **📊 GitHub Stats — Daily Cache**

That's it. From now on everything updates automatically.

---

## How It Works

```
Every Hour (GitHub Actions cron)
        │
        ▼
update_feed.py
        │
        ├─ Fetches RSS from:
        │    • TechCrunch AI feed
        │    • Ars Technica
        │    • The Hacker News (cybersecurity)
        │    • Krebs on Security
        │    • Schneier on Security
        │    • Wired
        │    • VentureBeat AI
        │    • Dev.to
        │
        ├─ Filters articles by keywords
        │    • AI & Claude: "claude", "anthropic", "llm", "gpt", ...
        │    • Cybersecurity: "vulnerability", "breach", "exploit", ...
        │    • Tech Advances: "quantum", "chip", "innovation", ...
        │    • Dev Insights: "developer", "open source", "rust", ...
        │
        ├─ Generates 8 SVG cards (490×~180px each)
        │    with: category badge, title, author quote, date, source
        │
        ├─ Updates README.md timestamp
        │
        └─ Commits & pushes to main
```

---

## Customisation

### Add or change RSS feed sources

Edit `scripts/update_feed.py`, find the `CATEGORIES` list, and modify the `"feeds"` array for any category.

```python
{
    "name": "AI & Claude",
    "feeds": [
        "https://your-custom-feed.com/rss",  # ← add here
        ...
    ],
    ...
}
```

### Change keyword filters

Update the `"keywords"` list in each category to refine which articles are picked up.

### Change number of cards per category

```python
MAX_CARDS = 2   # ← increase to 3 for 3 cards per category
```

### Change card colours

Each category has a `"color"` (text/border) and `"glow"` (accent) value in hex:

```python
{"name": "AI & Claude", "color": "#A78BFA", "glow": "#7C3AED", ...}
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Cards show "Fetching latest news…" | Run the workflow manually once (Actions → Run workflow) |
| Workflow fails with permission error | Enable read/write permissions in repo Settings → Actions |
| Stats SVGs are broken | Run the **📊 GitHub Stats** workflow manually |
| No articles found for a category | The RSS feeds may be temporarily down; they retry on the next hourly run |

---

*Built with ❤️ for Tito Kilonzo · SynthLink Technologies · Nairobi, Kenya*
