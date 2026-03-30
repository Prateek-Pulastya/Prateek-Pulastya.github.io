import requests
import json

USERNAME = "Prateek-Pulastya"

def fetch():
    url = f"https://api.github.com/users/{USERNAME}/repos"

    response = requests.get(url)

    # 🔥 DEBUG OUTPUT
    print("STATUS:", response.status_code)
    print("RAW:", response.text[:500])

    if response.status_code != 200:
        raise Exception("GitHub API failed")

    repos = response.json()

    if not repos:
        raise Exception("No repos returned from GitHub")

    # Sort by stars
    repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)

    selected = []

    for repo in repos:
        # 🔥 FILTER OUT FORKS + EMPTY
        if repo.get("fork"):
            continue

        selected.append({
            "name": repo.get("name"),
            "url": repo.get("html_url"),
            "desc": repo.get("description") or "No description provided.",
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language")
        })

    if not selected:
        raise Exception("All repos filtered out")

    with open("data/repos.json", "w") as f:
        json.dump(selected[:6], f, indent=2)

    print("SUCCESS: repos.json updated")

if __name__ == "__main__":
    fetch()
