"""Cache public repositories into data/repos.json.

Listing the public repos of a public user needs no credentials, so the token is
optional here. It used to be mandatory, and an expired GH_TOKEN secret failed
this job on every scheduled run with "Bad credentials" / 401.

Every repo currently has zero stars, so ranking by stars produced an arbitrary
order. PINNED comes first in the order given; everything else follows by most
recently pushed.
"""

import json
import os
import sys

import requests

USERNAME = "Prateek-Pulastya"
OUT_PATH = os.path.join("data", "repos.json")
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed"
MAX_REPOS = 6

PINNED = [
    "Guardrail-As-A-Service-V2",
    "AI-Powered-Threat-Detection-System-with-Explainability",
    "Hydroficient-Externship",
]

# Profile scaffolding and the site itself say nothing about engineering ability.
EXCLUDE = {
    "Prateek-Pulastya",
    "Prateek-Pulastya.github.io",
    "GitHubGraduation-2021",
}


def rank(repo):
    name = repo["name"]
    pinned_at = PINNED.index(name) if name in PINNED else len(PINNED)
    # ISO-8601 sorts lexically; reverse it so newer comes first within a tier.
    return (pinned_at, [-ord(c) for c in repo["pushed_at"]])


def fetch():
    headers = {"Accept": "application/vnd.github+json"}

    # Optional: only lifts the rate limit, never required for public data.
    token = os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(API_URL, headers=headers, timeout=30)

    if response.status_code != 200:
        print("STATUS:", response.status_code, file=sys.stderr)
        print("RESPONSE:", response.text[:500], file=sys.stderr)
        response.raise_for_status()

    repos = [
        r
        for r in response.json()
        if not r.get("fork") and not r.get("archived") and r["name"] not in EXCLUDE
    ]

    if not repos:
        sys.exit("No repositories returned - refusing to overwrite cache.")

    cleaned = [
        {
            "name": r["name"],
            "desc": r.get("description") or "No description provided.",
            "url": r["html_url"],
            "stars": r.get("stargazers_count", 0),
            "language": r.get("language") or "N/A",
            "topics": (r.get("topics") or [])[:4],
            "pushedAt": r["pushed_at"],
        }
        for r in sorted(repos, key=rank)[:MAX_REPOS]
    ]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(cleaned)} repos to {OUT_PATH} (auth={'yes' if token else 'no'}).")


if __name__ == "__main__":
    fetch()
