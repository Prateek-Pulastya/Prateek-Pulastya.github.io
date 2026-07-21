"""Cache the latest Medium posts into data/blog.json.

Medium's RSS feed does not emit a <description> element; the post body lives in
<content:encoded>. Reading "description" is why every cached entry fell back to
"No preview available." Excerpts are derived from content:encoded with the
leading <figure> stripped, so the excerpt starts at real prose.
"""

import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import requests

RSS_URL = "https://medium.com/feed/@prateekpulastya"
OUT_PATH = os.path.join("data", "blog.json")
MAX_POSTS = 6
EXCERPT_CHARS = 190
WORDS_PER_MINUTE = 220

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

# Medium appends "?source=rss-..." tracking noise to every link.
TRACKING = re.compile(r"\?source=rss[^\"'\s]*")
FIGURE = re.compile(r"<figure.*?</figure>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")


def text_of(item, path):
    node = item.find(path, NS)
    return (node.text or "").strip() if node is not None else ""


def to_plain(markup):
    """Strip a Medium content:encoded body down to readable prose."""
    if not markup:
        return ""
    without_figures = FIGURE.sub(" ", markup)
    stripped = TAG.sub(" ", without_figures)
    return re.sub(r"\s+", " ", html.unescape(stripped)).strip()


def excerpt(prose):
    if len(prose) <= EXCERPT_CHARS:
        return prose
    cut = prose[:EXCERPT_CHARS]
    # Prefer breaking on a word boundary rather than mid-token.
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,.;:-") + "…"


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    posts = []

    for item in root.findall(".//item")[:MAX_POSTS]:
        prose = to_plain(text_of(item, "content:encoded"))
        link = TRACKING.sub("", text_of(item, "link"))
        tags = [c.text.strip() for c in item.findall("category") if c.text]

        posts.append(
            {
                "title": text_of(item, "title"),
                "link": link,
                "date": text_of(item, "pubDate"),
                "desc": excerpt(prose) or "Read the full write-up on Medium.",
                "tags": tags[:3],
                "readingMinutes": max(1, round(len(prose.split()) / WORDS_PER_MINUTE)),
            }
        )

    return posts


def fetch():
    response = requests.get(
        RSS_URL,
        timeout=30,
        headers={"User-Agent": "prateek-pulastya.github.io blog cache"},
    )
    response.raise_for_status()

    posts = parse(response.content)

    # An empty feed means the fetch silently degraded. Fail the job rather than
    # overwrite a good cache with [] and report success.
    if not posts:
        sys.exit("No items parsed from the Medium feed - refusing to overwrite cache.")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")

    missing = sum(1 for p in posts if p["desc"].startswith("Read the full"))
    print(f"Wrote {len(posts)} posts to {OUT_PATH} ({missing} without an excerpt).")


if __name__ == "__main__":
    fetch()
