"""
Generates a themed SVG "NeetCode Progress" card from a NeetCode.io
GitHub-Sync repository (structure: <topic>/<problem-id>/submission-N.<ext>).

Adds a real submission-activity heatmap built from actual commit dates
(NeetCode's GitHub Sync makes one commit per synced submission), the same
idea as LeetCode card services' activity graph, but built from your repo's
real git history instead of an API NeetCode doesn't expose.

Run inside the target repo's own GitHub Actions workflow, where GITHUB_TOKEN
and GITHUB_REPOSITORY are provided automatically.
"""

import os
import re
import sys
from collections import Counter
from datetime import date, timedelta

import requests

REPO_FULL = os.environ.get("GITHUB_REPOSITORY", "Milkistasty/neetcode-submissions")
BRANCH = os.environ.get("DEFAULT_BRANCH", "main")
TOKEN = os.environ.get("GITHUB_TOKEN")

BOT_NAMES = {"github-actions[bot]"}

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "neetcode-stats-card-generator",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# Anthropic-inspired warm palette, matching the profile README
PALETTE = ["#d97757", "#D4A27F", "#6a9bcc", "#788c5d", "#b0817a", "#8fa6c9"]
BG = "#faf9f5"
BORDER = "#e8e6dc"
TEXT = "#141413"
MUTED = "#6a5a4a"
TITLE_COLOR = "#d97757"

# Heatmap intensity scale, lightest to darkest (0 submissions -> 4+)
HEAT_LEVELS = [BORDER, "#f1ddc9", "#e8c9a0", "#D4A27F", "#d97757"]

SUBMISSION_RE = re.compile(r"^submission-\d+\.\w+$")
FONT = "Segoe UI, Ubuntu, Sans-Serif"

WIDTH = 460
LABEL_COL_X = 25
BAR_X = 235
COUNT_GAP = 12


def fetch_tree():
    url = f"https://api.github.com/repos/{REPO_FULL}/git/trees/{BRANCH}?recursive=1"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        print("Warning: tree response was truncated by the GitHub API", file=sys.stderr)
    return data.get("tree", [])


def fetch_commit_dates(max_pages=10):
    """Return a list of ISO calendar-day strings for real submission commits,
    filtering out this workflow's own bot commits."""
    dates = []
    for page in range(1, max_pages + 1):
        url = f"https://api.github.com/repos/{REPO_FULL}/commits?per_page=100&page={page}"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            break
        batch = resp.json()
        if not batch:
            break
        for c in batch:
            author_login = (c.get("author") or {}).get("login", "")
            commit_author_name = c.get("commit", {}).get("author", {}).get("name", "")
            if author_login in BOT_NAMES or commit_author_name in BOT_NAMES:
                continue
            date_str = c.get("commit", {}).get("author", {}).get("date")
            if date_str:
                dates.append(date_str[:10])
        if len(batch) < 100:
            break
    return dates


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
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_bars(topic_counts, top_y):
    rows = sorted(topic_counts.items(), key=lambda kv: kv[1], reverse=True)
    max_rows = 6
    shown = rows[:max_rows]
    extra = len(rows) - len(shown)

    row_h = 26
    max_count = max((c for _, c in shown), default=1)
    bar_max_w = WIDTH - BAR_X - 45

    parts = []
    y = top_y
    for i, (topic, count) in enumerate(shown):
        color = PALETTE[i % len(PALETTE)]
        bar_w = max(4, int(bar_max_w * count / max_count))
        label = topic if len(topic) <= 33 else topic[:31] + "…"
        parts.append(f'''
    <text x="{LABEL_COL_X}" y="{y + 15}" font-size="12" fill="{TEXT}" font-family="{FONT}">{esc(label)}</text>
    <rect x="{BAR_X}" y="{y + 5}" width="{bar_max_w}" height="8" rx="4" fill="{BORDER}"/>
    <rect x="{BAR_X}" y="{y + 5}" width="{bar_w}" height="8" rx="4" fill="{color}"/>
    <text x="{BAR_X + bar_max_w + COUNT_GAP}" y="{y + 13}" font-size="11" fill="{MUTED}" font-family="{FONT}">{count}</text>''')
        y += row_h

    if extra > 0:
        parts.append(
            f'<text x="{LABEL_COL_X}" y="{y + 14}" font-size="11" fill="{MUTED}" '
            f'font-family="{FONT}">+{extra} more topics</text>'
        )
        y += 20

    return "".join(parts), y


def render_heatmap(commit_dates, top_y):
    counts = Counter(commit_dates)
    weeks = 12
    days = weeks * 7
    today = date.today()
    start = today - timedelta(days=days - 1)

    cell = 10
    gap = 2
    step = cell + gap

    label = (
        f'<text x="{LABEL_COL_X}" y="{top_y}" font-size="11" fill="{MUTED}" '
        f'font-family="{FONT}">Submission activity (last {weeks} weeks)</text>'
    )

    grid_y = top_y + 10
    cells = []
    for offset in range(days):
        d = start + timedelta(days=offset)
        col = offset // 7
        row = offset % 7
        n = counts.get(d.isoformat(), 0)
        if n == 0:
            level = 0
        elif n <= 1:
            level = 1
        elif n <= 3:
            level = 2
        elif n <= 5:
            level = 3
        else:
            level = 4
        x = LABEL_COL_X + col * step
        y = grid_y + row * step
        cells.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{HEAT_LEVELS[level]}">'
            f'<title>{d.isoformat()}: {n} submission{"s" if n != 1 else ""}</title></rect>'
        )

    grid_w = weeks * step - gap
    legend_x = LABEL_COL_X + grid_w - (len(HEAT_LEVELS) * step) + gap
    legend_y = grid_y + 7 * step + 4
    legend = [
        f'<text x="{LABEL_COL_X}" y="{legend_y + cell}" font-size="10" fill="{MUTED}" font-family="{FONT}">Less</text>'
    ]
    for i, color in enumerate(HEAT_LEVELS):
        lx = legend_x + i * step
        legend.append(f'<rect x="{lx}" y="{legend_y}" width="{cell}" height="{cell}" rx="2" fill="{color}"/>')
    legend.append(
        f'<text x="{legend_x + len(HEAT_LEVELS) * step + 4}" y="{legend_y + cell}" font-size="10" '
        f'fill="{MUTED}" font-family="{FONT}">More</text>'
    )

    bottom_y = legend_y + cell + 6
    return label + "".join(cells) + "".join(legend), bottom_y


def render_svg(topic_counts, total_problems, total_submissions, commit_dates):
    header_h = 74
    bars_svg, y_after_bars = render_bars(topic_counts, header_h)
    heatmap_svg, y_after_heatmap = render_heatmap(commit_dates, y_after_bars + 14)
    height = y_after_heatmap + 6

    dot = "\u00b7"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <text x="{LABEL_COL_X}" y="32" font-size="17" font-weight="700" fill="{TITLE_COLOR}" font-family="{FONT}">NeetCode Progress</text>
  <text x="{LABEL_COL_X}" y="52" font-size="12" fill="{MUTED}" font-family="{FONT}">{total_problems} problems synced {dot} {total_submissions} submissions</text>
  {bars_svg}
  {heatmap_svg}
</svg>'''
    return svg


def main():
    tree = fetch_tree()
    commit_dates = fetch_commit_dates()
    topic_counts, total_problems, total_submissions, lang_counts = collect_stats(tree)
    svg = render_svg(topic_counts, total_problems, total_submissions, commit_dates)
    with open("neetcode-stats-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(
        f"Wrote neetcode-stats-card.svg: {total_problems} problems, "
        f"{total_submissions} submissions across {len(topic_counts)} topics, "
        f"{len(commit_dates)} activity commits"
    )


if __name__ == "__main__":
    main()