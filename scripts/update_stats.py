#!/usr/bin/env python3
"""
GitHub Stats SVG Cacher
Downloads GitHub stats SVGs from external services and commits them locally,
preventing broken images from rate-limiting or service outages.
"""

import urllib.request
import urllib.error
import os
import time

GITHUB_USERNAME = "TitoKilonzo"
OUTPUT_DIR      = "assets/github-stats"

SOURCES = {
    "streak.svg": (
        f"https://streak-stats.demolab.com"
        f"?user={GITHUB_USERNAME}&theme=tokyonight&hide_border=true"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GitHubActionsBot/1.0; "
        "+https://github.com/" + GITHUB_USERNAME + ")"
    )
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\n{'═'*50}")
print(f"  📊  GitHub Stats Cache Refresh")
print(f"{'═'*50}\n")

for filename, url in SOURCES.items():
    dest = os.path.join(OUTPUT_DIR, filename)
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)
            print(f"  ✔  {filename}  ({len(data):,} bytes)")
            break
        except urllib.error.HTTPError as e:
            print(f"  ✗  {filename}  HTTP {e.code} (attempt {attempt}/3)")
        except Exception as e:
            print(f"  ✗  {filename}  {e!s:.60} (attempt {attempt}/3)")
        time.sleep(3 * attempt)
    else:
        print(f"  ⚠  {filename}  — keeping cached version (all attempts failed)")

print(f"\n  ✨  Stats cache updated → {OUTPUT_DIR}/\n")
