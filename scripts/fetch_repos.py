import requests
import json
import os

USERNAME = "Prateek-Pulastya"
TOKEN = os.getenv("GH_TOKEN")

API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

def fetch():
    if not TOKEN:
        raise Exception("GH_TOKEN missing")

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code != 200:
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        raise Exception("GitHub API failed")

    repos = response.json()

    cleaned = []

    for repo in repos:
        if repo.get("fork"):
            continue

        cleaned.append({
            "name": repo.get("name"),
            "desc": repo.get("description") or "No description provided.",
            "url": repo.get("html_url"),
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language") or "N/A"
        })

    cleaned = sorted(cleaned, key=lambda x: x["stars"], reverse=True)[:8]

    with open("data/repos.json", "w") as f:
        json.dump(cleaned, f, indent=2)

if __name__ == "__main__":
    fetch()
