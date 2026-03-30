import requests
import json

USERNAME = "Prateek-Pulastya"

def fetch():
    url = f"https://api.github.com/users/Prateek-Pulastya/repos"
    response = requests.get(url)

    repos = response.json()

    # Sort by stars (signal)
    repos = sorted(repos, key=lambda x: x["stargazers_count"], reverse=True)

    selected = []

    for repo in repos[:6]:  # top 6 repos
        selected.append({
            "name": repo["name"],
            "url": repo["html_url"],
            "desc": repo["description"] or "No description provided.",
            "stars": repo["stargazers_count"],
            "language": repo["language"]
        })

    with open("data/repos.json", "w") as f:
        json.dump(selected, f, indent=2)

if __name__ == "__main__":
    fetch()
