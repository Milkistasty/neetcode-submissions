"""
Generates a themed SVG "NeetCode Progress" card from a NeetCode.io
GitHub-Sync repository (structure: <topic>/<problem-id>/submission-N.<ext>).

Run inside the target repo's own GitHub Actions workflow, where GITHUB_TOKEN
and GITHUB_REPOSITORY are provided automatically.
"""

import os
import re
import sys
import requests

REPO_FULL = os.environ.get("GITHUB_REPOSITORY", "Milkistasty/neetcode-submissions")
BRANCH = os.environ.get("DEFAULT_BRANCH", "main")
TOKEN = os.environ.get("GITHUB_TOKEN")

# Anthropic-inspired warm palette, matching the profile README
PALETTE = ["#d97757", "#D4A27F", "#6a9bcc", "#788c5d", "#b0817a", "#8fa6c9"]
BG = "#faf9f5"
BORDER = "#e8e6dc"
TEXT = "#141413"
MUTED = "#6a5a4a"
TITLE_COLOR = "#d97757"

SUBMISSION_RE = re.compile(r"^submission-\d+\.\w+$")
FONT = "Segoe UI, Ubuntu, Sans-Serif"


def fetch_tree():
    url = f"https://api.github.com/repos/{REPO_FULL}/git/trees/{BRANCH}?recursive=1"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "neetcode-stats-card-generator",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        print("Warning: tree response was truncated by the GitHub API", file=sys.stderr)
    return data.get("tree", [])


def collect_stats(tree):
    topic_problems = {}  # topic -> set(problem ids)
    total_submissions = 0
    lang_counts = {}

    for item in tree:
        if item.get("type") != "blob":
            continue
        parts = item["path"].split("/")
        if len(parts) != 3:
            continue
        topic, problem, filename = parts
        if not SUBMISSION_RE.match(filename):
            continue
        topic_problems.setdefault(topic, set()).add(problem)
        total_submissions += 1
        ext = filename.rsplit(".", 1)[-1]
        lang_counts[ext] = lang_counts.get(ext, 0) + 1

    topic_counts = {t: len(p) for t, p in topic_problems.items()}
    total_problems = sum(topic_counts.values())
    return topic_counts, total_problems, total_submissions, lang_counts


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_svg(topic_counts, total_problems, total_submissions):
    rows = sorted(topic_counts.items(), key=lambda kv: kv[1], reverse=True)
    max_rows = 6
    shown = rows[:max_rows]
    extra = len(rows) - len(shown)

    row_h = 26
    header_h = 74
    footer_h = 24 if extra > 0 else 10
    height = header_h + row_h * len(shown) + footer_h
    width = 420
    max_count = max((c for _, c in shown), default=1)
    bar_max_w = width - 190

    bars = []
    y = header_h
    for i, (topic, count) in enumerate(shown):
        color = PALETTE[i % len(PALETTE)]
        bar_w = max(4, int(bar_max_w * count / max_count))
        label = topic if len(topic) <= 26 else topic[:24] + "…"
        bars.append(f'''
    <text x="25" y="{y + 15}" font-size="12" fill="{TEXT}" font-family="{FONT}">{esc(label)}</text>
    <rect x="185" y="{y + 5}" width="{bar_max_w}" height="8" rx="4" fill="{BORDER}"/>
    <rect x="185" y="{y + 5}" width="{bar_w}" height="8" rx="4" fill="{color}"/>
    <text x="{185 + bar_max_w + 10}" y="{y + 13}" font-size="11" fill="{MUTED}" font-family="{FONT}">{count}</text>''')
        y += row_h

    footer = ""
    if extra > 0:
        footer = (
            f'<text x="25" y="{y + 14}" font-size="11" fill="{MUTED}" '
            f'font-family="{FONT}">+{extra} more topics</text>'
        )

    dot = "\u00b7"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <text x="25" y="32" font-size="17" font-weight="700" fill="{TITLE_COLOR}" font-family="{FONT}">NeetCode Progress</text>
  <text x="25" y="52" font-size="12" fill="{MUTED}" font-family="{FONT}">{total_problems} problems synced {dot} {total_submissions} submissions</text>
  {''.join(bars)}
  {footer}
</svg>'''
    return svg


def main():
    tree = fetch_tree()
    topic_counts, total_problems, total_submissions, lang_counts = collect_stats(tree)
    svg = render_svg(topic_counts, total_problems, total_submissions)
    with open("neetcode-stats-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(
        f"Wrote neetcode-stats-card.svg: {total_problems} problems, "
        f"{total_submissions} submissions across {len(topic_counts)} topics"
    )


if __name__ == "__main__":
    main()
