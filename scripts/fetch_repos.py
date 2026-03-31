import requests
import json
import os

USERNAME = "Prateek-Pulastya"
TOKEN = os.getenv("GH_TOKEN")

API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

def fetch():
    headers = {
        "Authorization": f"token {TOKEN}"
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code != 200:
        raise Exception("GitHub API failed")

    repos = response.json()

    cleaned = []

    for repo in repos:
        # FILTER OUT USELESS REPOS
        if repo["fork"]:
            continue

        cleaned.append({
            "name": repo["name"],
            "desc": repo["description"] or "No description provided.",
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "language": repo["language"] or "N/A"
        })

    # SORT BY STARS (SIGNAL > NOISE)
    cleaned = sorted(cleaned, key=lambda x: x["stars"], reverse=True)[:8]

    with open("data/repos.json", "w") as f:
        json.dump(cleaned, f, indent=2)

if __name__ == "__main__":
    fetch()
