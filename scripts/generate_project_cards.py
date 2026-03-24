import os

PROJECTS = [
    {
        "name": "CyberScribe",
        "desc": "Open-source cybersecurity skills library for AI coding agents — 700+ structured Markdown skill definitions across 16 domains",
        "stack": ["Markdown", "GitHub Actions"],
        "url": "https://github.com/TitoKilonzo/CyberScribe",
        "color": "#A78BFA" # Purple aura
    },
    {
        "name": "Bongotoons",
        "desc": "Netflix/Showmax-style video streaming platform",
        "stack": ["React", "Vite", "Appwrite"],
        "url": "https://github.com/TitoKilonzo",
        "color": "#F43F5E" # Rose aura
    },
    {
        "name": "NexVault",
        "desc": "Fintech dashboard with JWT authentication",
        "stack": ["React", "Node.js", "PostgreSQL"],
        "url": "https://github.com/TitoKilonzo",
        "color": "#3B82F6" # Blue aura
    },
    {
        "name": "LUMINARY",
        "desc": "Financial literacy web library",
        "stack": ["React", "MongoDB Atlas"],
        "url": "https://github.com/TitoKilonzo",
        "color": "#F59E0B" # Amber aura
    },
    {
        "name": "Shift Master",
        "desc": "Cross-platform shift management mobile app",
        "stack": ["Flutter", "Dart"],
        "url": "https://github.com/TitoKilonzo/shift_master",
        "color": "#0EA5E9" # Sky aura
    },
    {
        "name": "Gmail Sentinel",
        "desc": "Automated email monitoring with SMS alerts",
        "stack": ["Node.js", "Gmail API", "Africa's Talking"],
        "url": "https://github.com/TitoKilonzo",
        "color": "#10B981" # Emerald aura
    }
]

SVG_TEMPLATE = """\
<svg width="490" height="150" viewBox="0 0 490 150" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <filter id="aura" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <rect width="490" height="150" rx="12" fill="url(#bg)" stroke="{color}" stroke-opacity="0.25" stroke-width="1" />
  
  <!-- Glowing left accent -->
  <rect x="0" y="25" width="4" height="100" rx="2" fill="{color}" filter="url(#aura)"/>
  <circle cx="465" cy="25" r="5" fill="{color}" filter="url(#aura)" fill-opacity="0.8"/>

  <!-- Icon and Title -->
  <text x="25" y="38" font-family="'Segoe UI', 'SF Pro Display', Arial, sans-serif" font-size="16" font-weight="bold" fill="#E6EDF3">{name}</text>
  
  <!-- Description -->
  {desc_svg}

  <!-- Stack Badges -->
  {stack_svg}
  
  <line x1="25" y1="125" x2="465" y2="125" stroke="#21262d" stroke-width="1"/>
  <text x="25" y="142" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="{color}">⭐ Featured Project &#8212; 🌐 View Source</text>
</svg>
"""

import textwrap

output_dir = r"c:\Users\PC\Desktop\TitoKilonzo\assets\projects"
os.makedirs(output_dir, exist_ok=True)

for p in PROJECTS:
    # Handle description wrap
    import html
    desc_clean = html.escape(p["desc"])
    lines = textwrap.wrap(desc_clean, width=70, max_lines=2, placeholder="...")
    desc_svg = ""
    y_pos = 65
    for l in lines:
        desc_svg += f'<text x="25" y="{y_pos}" font-family="\'Segoe UI\', Arial, sans-serif" font-size="12" fill="#8B949E">{l}</text>\n  '
        y_pos += 18
        
    # Handle stack badges
    stack_svg = ""
    bx = 25
    for tk in p["stack"]:
        w = len(tk) * 7.5 + 16
        stack_svg += f'<rect x="{bx}" y="{y_pos}" width="{w}" height="20" rx="10" fill="{p["color"]}" fill-opacity="0.15" />\n  '
        stack_svg += f'<text x="{bx+w/2}" y="{y_pos+14}" font-family="\'Segoe UI\', Arial, sans-serif" font-size="10" font-weight="bold" fill="{p["color"]}" text-anchor="middle">{html.escape(tk)}</text>\n  '
        bx += w + 8
        
    svg = SVG_TEMPLATE.format(
        name=html.escape(p["name"]),
        color=p["color"],
        desc_svg=desc_svg,
        stack_svg=stack_svg
    )
    
    file_path = os.path.join(output_dir, f'{p["name"].replace(" ", "_").lower()}.svg')
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg)
        
print("Generated stylish aura SVG cards for projects in assets/projects/")
