import os
import requests
import json
from datetime import datetime

LC_SESSION = os.getenv("LEETCODE_SESSION")
USERNAME = os.getenv("LEETCODE_USERNAME")  # optional; used for heading

if not LC_SESSION:
    raise SystemExit("Missing LEETCODE_SESSION environment variable (store it as a GitHub Secret).")

URL = "https://leetcode.com/api/problems/all/"

headers = {
    "User-Agent": "github-action/leetcode-tracker",
    "Referer": "https://leetcode.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

cookies = {
    "LEETCODE_SESSION": LC_SESSION
}

resp = requests.get(URL, headers=headers, cookies=cookies, timeout=30)
if resp.status_code != 200:
    raise SystemExit(f"Failed to fetch LeetCode problems list: HTTP {resp.status_code}\n{resp.text}")

data = resp.json()

pairs = data.get("stat_status_pairs", [])
solved = []
for p in pairs:
    # The 'status' field is usually 'ac' for accepted (solved) for logged-in user
    status = p.get("status")
    stat = p.get("stat", {})
    question_title = stat.get("question__title")
    question_slug = stat.get("question__title_slug")
    difficulty = p.get("difficulty", {}).get("level")  # 1 easy, 2 medium, 3 hard
    if status == "ac":
        solved.append({
            "title": question_title,
            "slug": question_slug,
            "difficulty": difficulty
        })

# Sort solved list by title
solved.sort(key=lambda x: x["title"].lower())

total_solved = len(solved)
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

# Build README content (you can customize)
lines = []
lines.append("# LeetCode Progress")
lines.append("")
if USERNAME:
    lines.append(f"**User:** {USERNAME}")
lines.append(f"**Updated:** {timestamp}")
lines.append(f"**Solved:** {total_solved}")
lines.append("")
lines.append("### Solved problems (title — difficulty)")
lines.append("")
# Map difficulty number to label
diff_map = {1: "Easy", 2: "Medium", 3: "Hard"}
for s in solved:
    diff = diff_map.get(s["difficulty"], "Unknown")
    # link to leetcode problem by slug
    url = f"https://leetcode.com/problems/{s['slug']}/"
    lines.append(f"- [{s['title']}]({url}) — {diff}")

new_content = "\n".join(lines) + "\n"

# Write README.md (or update whatever file you want)
readme_path = "README.md"
old = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        old = f.read()

if old != new_content:
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"README updated: solved {total_solved}")
else:
    print("No changes needed.")
