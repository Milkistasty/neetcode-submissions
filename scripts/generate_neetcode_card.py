"""
Generates a themed SVG "NeetCode Progress" card from a NeetCode.io
GitHub-Sync repository (structure: <topic>/<problem-id>/submission-N.<ext>).

The card shows NeetCode All progress by difficulty, recent submissions
(date, language, problem name) in the same row layout as a LeetCode stats
card, and a submission-activity heatmap built from real commit dates.
Difficulty comes from scripts/neetcode_all.json (slug to Easy/Medium/Hard).
NeetCode's GitHub Sync makes one commit per synced submission, so the
heatmap uses the repo's git history instead of an API NeetCode doesn't expose.

Run inside the target repo's own GitHub Actions workflow, where GITHUB_TOKEN
and GITHUB_REPOSITORY are provided automatically.
"""

import json
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
BG = "#faf9f5"
BORDER = "#e8e6dc"
TEXT = "#141413"
MUTED = "#6a5a4a"
TITLE_COLOR = "#d97757"
AC_GREEN = "#2cbb5d"
EASY_COLOR = "#00b8a3"
MEDIUM_COLOR = "#ffc01e"
HARD_COLOR = "#ef4743"
DIFFICULTIES = ("Easy", "Medium", "Hard")
DIFF_COLORS = {"Easy": EASY_COLOR, "Medium": MEDIUM_COLOR, "Hard": HARD_COLOR}

# Heatmap intensity scale, lightest to darkest (0 submissions -> 4+)
HEAT_LEVELS = [BORDER, "#f1ddc9", "#e8c9a0", "#D4A27F", "#d97757"]

SUBMISSION_RE = re.compile(r"^submission-(\d+)\.(\w+)$")
ADD_RE = re.compile(r"^(?:Add|Update): (.+) - submission-(\d+)\s*$")
FONT = "Segoe UI, Ubuntu, Sans-Serif"

LANGS = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "java": "Java",
    "cpp": "C++",
    "cs": "C#",
    "go": "Go",
    "rs": "Rust",
    "kt": "Kotlin",
    "swift": "Swift",
    "sql": "SQL",
}
_SMALL_WORDS = {"a", "an", "of", "on", "the", "and", "with", "to", "in", "for", "from", "at", "by"}

WIDTH = 460
LABEL_COL_X = 25
RECENT_LIMIT = 4
NAME_LIMIT = 34
HEAT_WEEKS = 12
HEAT_GAP = 3
MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neetcode_all.json")


def fetch_tree():
    url = f"https://api.github.com/repos/{REPO_FULL}/git/trees/{BRANCH}?recursive=1"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        print("Warning: tree response was truncated by the GitHub API", file=sys.stderr)
    return data.get("tree", [])


def fetch_commits(max_pages=10):
    """Return newest-first commits as {date, message, sha}, skipping bot and merge commits."""
    commits = []
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
            if len(c.get("parents") or []) > 1:
                continue
            date_str = c.get("commit", {}).get("author", {}).get("date")
            if not date_str:
                continue
            commits.append({
                "date": date_str[:10],
                "message": c.get("commit", {}).get("message", ""),
                "sha": c.get("sha", ""),
            })
        if len(batch) < 100:
            break
    return commits


def fetch_commit_paths(sha):
    """File paths touched by one commit. Used for bulk-sync commits, whose message has no problem slug."""
    if not sha:
        return []
    url = f"https://api.github.com/repos/{REPO_FULL}/commits/{sha}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return []
    return [f.get("filename", "") for f in resp.json().get("files", [])]


def collect_stats(tree):
    problems = set()
    topics = set()
    total_submissions = 0

    for item in tree:
        if item.get("type") != "blob":
            continue
        parts = item["path"].split("/")
        if len(parts) != 3:
            continue
        topic, problem, filename = parts
        if not SUBMISSION_RE.match(filename):
            continue
        topics.add(topic)
        problems.add(problem)
        total_submissions += 1

    return problems, total_submissions, len(topics)


def load_difficulty_map(path=MAP_PATH):
    """NeetCode All slug -> Easy/Medium/Hard. Slugs match GitHub Sync folder names."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("neetcode_all.json must be an object of slug to difficulty")
    bad = [slug for slug, diff in data.items() if diff not in DIFFICULTIES]
    if bad:
        raise ValueError("unknown difficulty for: " + ", ".join(bad[:5]))
    return data


def difficulty_totals(mapping):
    totals = {name: 0 for name in DIFFICULTIES}
    for diff in mapping.values():
        totals[diff] += 1
    return totals


def count_solved(problems, mapping):
    """Problems missing from the NeetCode All map count as Easy."""
    solved = {name: 0 for name in DIFFICULTIES}
    for slug in problems:
        solved[mapping.get(slug, "Easy")] += 1
    return solved


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_activity_date(iso_day):
    """LeetCode-card style YY.M.D, e.g. 2026-09-20 -> 26.9.20."""
    y, m, d = iso_day.split("-")
    return f"{int(y) % 100}.{int(m)}.{int(d)}"


def pretty_problem(slug):
    words = slug.split("-")
    parts = []
    for i, word in enumerate(words):
        if i and word in _SMALL_WORDS:
            parts.append(word)
        elif word:
            parts.append(word[0].upper() + word[1:])
    return " ".join(parts)


def fit(text, limit):
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rstrip()
    space = cut.rfind(" ")
    if space >= limit // 2:
        cut = cut[:space]
    return cut + "…"


def submission_index(tree):
    """Map (problem slug, submission number) -> language name."""
    index = {}
    for item in tree:
        if item.get("type") != "blob":
            continue
        parts = item["path"].split("/")
        if len(parts) != 3:
            continue
        match = SUBMISSION_RE.match(parts[2])
        if not match:
            continue
        ext = match.group(2).lower()
        index[(parts[1], match.group(1))] = LANGS.get(ext, ext)
    return index


def activity_from_message(message, index):
    """Parse a NeetCode sync subject. Returns (slug, language) or None."""
    match = ADD_RE.match(message.split("\n", 1)[0].strip())
    if not match:
        return None
    slug, num = match.group(1).strip(), match.group(2)
    return slug, index.get((slug, num), "")


def paths_to_activities(paths):
    found = []
    for path in paths:
        parts = path.split("/")
        if len(parts) != 3:
            continue
        match = SUBMISSION_RE.match(parts[2])
        if not match:
            continue
        ext = match.group(2).lower()
        found.append((parts[1], LANGS.get(ext, ext)))
    return found


def collect_recent(events, limit=RECENT_LIMIT):
    """events: (iso day, slug, language) newest first. One row per problem."""
    seen = set()
    rows = []
    for iso_day, slug, lang in events:
        if slug in seen:
            continue
        seen.add(slug)
        rows.append({
            "date": format_activity_date(iso_day),
            "lang": lang or "Code",
            "name": fit(pretty_problem(slug), NAME_LIMIT),
        })
        if len(rows) >= limit:
            break
    return rows


def recent_activities(commits, tree, limit=RECENT_LIMIT):
    index = submission_index(tree)
    events = []
    seen = set()
    for commit in commits:
        if len(seen) >= limit:
            break
        parsed = activity_from_message(commit["message"], index)
        if parsed:
            found = [parsed]
        elif "sync" in commit["message"].split("\n", 1)[0].lower():
            found = paths_to_activities(fetch_commit_paths(commit["sha"]))
        else:
            continue
        for slug, lang in found:
            if slug in seen:
                continue
            seen.add(slug)
            events.append((commit["date"], slug, lang))
            if len(seen) >= limit:
                break
    return collect_recent(events, limit)


def render_difficulty(solved, totals, top_y):
    """Easy / Medium / Hard rows: label, solved/total, and a thin bar like a LeetCode card."""
    right = WIDTH - LABEL_COL_X
    bar_w = right - LABEL_COL_X
    bar_h = 6
    row_h = 32
    parts = []
    y = top_y
    for name in DIFFICULTIES:
        done = solved[name]
        total = totals[name]
        fill = int(bar_w * done / total) if total else 0
        if done and fill < 4:
            fill = 4
        fill = min(fill, bar_w)
        fill_rect = ""
        if fill:
            fill_rect = (
                f'<rect x="{LABEL_COL_X}" y="{y + 8}" width="{fill}" height="{bar_h}" '
                f'rx="3" fill="{DIFF_COLORS[name]}"/>'
            )
        parts.append(f'''
    <text x="{LABEL_COL_X}" y="{y}" font-size="13" font-weight="600" fill="{TEXT}" font-family="{FONT}">{name}</text>
    <text x="{right}" y="{y}" font-size="12" fill="{MUTED}" text-anchor="end" font-family="{FONT}">{done} / {total}</text>
    <rect x="{LABEL_COL_X}" y="{y + 8}" width="{bar_w}" height="{bar_h}" rx="3" fill="{BORDER}"/>
    {fill_rect}''')
        y += row_h
    return "".join(parts), y


def render_activities(activities, top_y):
    """Recent-activity rows laid out like a LeetCode card: date, AC badge, language, problem."""
    right = WIDTH - LABEL_COL_X
    badge_x = 88
    badge_w = 28
    badge_h = 16
    lang_x = badge_x + badge_w + 10

    parts = [
        f'<line x1="{LABEL_COL_X}" y1="{top_y}" x2="{right}" y2="{top_y}" stroke="{BORDER}" stroke-width="1"/>',
        f'<text x="{LABEL_COL_X}" y="{top_y + 24}" font-size="13" font-weight="600" fill="{TEXT}" '
        f'font-family="{FONT}">Recent Activities</text>',
    ]
    y = top_y + 50
    if not activities:
        parts.append(
            f'<text x="{LABEL_COL_X}" y="{y}" font-size="12" fill="{MUTED}" '
            f'font-family="{FONT}">No submissions yet</text>'
        )
        return "".join(parts), y + 16

    for row in activities:
        badge_y = y - 12
        parts.append(f'''
    <text x="{LABEL_COL_X}" y="{y}" font-size="12" fill="{MUTED}" font-family="{FONT}">{esc(row["date"])}</text>
    <rect x="{badge_x}" y="{badge_y}" width="{badge_w}" height="{badge_h}" rx="3" fill="{AC_GREEN}"/>
    <text x="{badge_x + badge_w / 2}" y="{y - 1}" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="{FONT}">AC</text>
    <text x="{lang_x}" y="{y}" font-size="12" font-weight="700" fill="{TEXT}" font-family="{FONT}">{esc(row["lang"])}</text>
    <text x="{right}" y="{y}" font-size="12" fill="{MUTED}" text-anchor="end" font-family="{FONT}">{esc(row["name"])}</text>''')
        y += 26
    return "".join(parts), y


def heatmap_geometry(width=WIDTH):
    """Square cells sized so 12 week-columns fill the card's content width."""
    usable = width - 2 * LABEL_COL_X
    cell = (usable - (HEAT_WEEKS - 1) * HEAT_GAP) // HEAT_WEEKS
    grid_w = HEAT_WEEKS * cell + (HEAT_WEEKS - 1) * HEAT_GAP
    return cell, HEAT_GAP, grid_w


def render_heatmap(commit_dates, top_y):
    counts = Counter(commit_dates)
    weeks = HEAT_WEEKS
    days = weeks * 7
    today = date.today()
    start = today - timedelta(days=days - 1)

    cell, gap, grid_w = heatmap_geometry()
    step = cell + gap
    radius = max(2, cell // 8)

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
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="{radius}" fill="{HEAT_LEVELS[level]}">'
            f'<title>{d.isoformat()}: {n} submission{"s" if n != 1 else ""}</title></rect>'
        )

    # Legend stays small and sits on the right edge of the widened grid.
    legend_cell = 10
    legend_step = legend_cell + 2
    legend_y = grid_y + 7 * step + 6
    legend_right = LABEL_COL_X + grid_w
    squares_w = len(HEAT_LEVELS) * legend_step - 2
    squares_x = legend_right - 32 - squares_w
    less_x = squares_x - 6
    legend = [
        f'<text x="{less_x}" y="{legend_y + legend_cell}" font-size="10" fill="{MUTED}" '
        f'text-anchor="end" font-family="{FONT}">Less</text>'
    ]
    for i, color in enumerate(HEAT_LEVELS):
        lx = squares_x + i * legend_step
        legend.append(
            f'<rect x="{lx}" y="{legend_y}" width="{legend_cell}" height="{legend_cell}" rx="2" fill="{color}"/>'
        )
    legend.append(
        f'<text x="{legend_right}" y="{legend_y + legend_cell}" font-size="10" fill="{MUTED}" '
        f'text-anchor="end" font-family="{FONT}">More</text>'
    )

    bottom_y = legend_y + legend_cell + 8
    return label + "".join(cells) + "".join(legend), bottom_y


def render_svg(total_problems, total_submissions, commit_dates, activities, solved, totals):
    diff_svg, y_after_diff = render_difficulty(solved, totals, 76)
    activities_svg, y_after = render_activities(activities, y_after_diff + 2)
    heatmap_svg, y_after_heatmap = render_heatmap(commit_dates, y_after + 6)
    height = y_after_heatmap + 8

    dot = "\u00b7"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <text x="{LABEL_COL_X}" y="32" font-size="17" font-weight="700" fill="{TITLE_COLOR}" font-family="{FONT}">NeetCode Progress</text>
  <text x="{LABEL_COL_X}" y="52" font-size="12" fill="{MUTED}" font-family="{FONT}">{total_problems} problems synced {dot} {total_submissions} submissions</text>
  {diff_svg}
  {activities_svg}
  {heatmap_svg}
</svg>'''
    return svg


def _self_check():
    assert format_activity_date("2026-09-20") == "26.9.20"
    assert pretty_problem("concatenation-of-array") == "Concatenation of Array"
    assert pretty_problem("bus-routes") == "Bus Routes"
    assert fit("Replace Elements with Greatest Element on Right Side", NAME_LIMIT) == (
        "Replace Elements with Greatest…"
    )
    rows = collect_recent([
        ("2026-09-26", "remove-element", "Python"),
        ("2026-09-26", "remove-element", "Python"),
        ("2026-09-24", "duplicate-integer", "Python"),
    ])
    assert [row["name"] for row in rows] == ["Remove Element", "Duplicate Integer"]
    assert rows[0]["date"] == "26.9.26"
    assert rows[0]["lang"] == "Python"
    match = ADD_RE.match("Add: remove-element - submission-1")
    assert match and match.group(1) == "remove-element" and match.group(2) == "1"
    index = {("remove-element", "1"): "Python"}
    assert activity_from_message("Add: remove-element - submission-1\n", index) == (
        "remove-element",
        "Python",
    )
    cell, _gap, grid_w = heatmap_geometry()
    usable = WIDTH - 2 * LABEL_COL_X
    assert cell >= 20
    assert grid_w <= usable
    assert usable - grid_w < cell
    mapping = load_difficulty_map()
    assert mapping["concatenation-of-array"] == "Easy"
    assert mapping["duplicate-integer"] == "Easy"
    assert mapping["remove-element"] == "Easy"
    assert mapping["max-consecutive-ones"] == "Easy"
    assert mapping["replace-elements-with-greatest-element-on-right-side"] == "Easy"
    assert mapping["trapping-rain-water"] == "Hard"
    totals = difficulty_totals(mapping)
    assert totals == {"Easy": 224, "Medium": 600, "Hard": 149}
    solved = count_solved({"concatenation-of-array", "not-a-problem"}, mapping)
    assert solved["Easy"] == 2 and solved["Medium"] == 0 and solved["Hard"] == 0


def main():
    _self_check()
    tree = fetch_tree()
    commits = fetch_commits()
    commit_dates = [c["date"] for c in commits]
    problems, total_submissions, topic_count = collect_stats(tree)
    mapping = load_difficulty_map()
    solved = count_solved(problems, mapping)
    totals = difficulty_totals(mapping)
    activities = recent_activities(commits, tree)
    svg = render_svg(
        len(problems), total_submissions, commit_dates, activities, solved, totals
    )
    with open("neetcode-stats-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(
        f"Wrote neetcode-stats-card.svg: {len(problems)} problems, "
        f"{total_submissions} submissions across {topic_count} topics, "
        f"easy {solved['Easy']}/{totals['Easy']}, "
        f"medium {solved['Medium']}/{totals['Medium']}, "
        f"hard {solved['Hard']}/{totals['Hard']}, "
        f"{len(commit_dates)} activity commits, {len(activities)} recent"
    )


if __name__ == "__main__":
    main()