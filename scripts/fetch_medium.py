import requests
import json
import xml.etree.ElementTree as ET
import re

RSS_URL = "https://medium.com/feed/@prateekpulastya"

def clean_html(text):
    return re.sub('<[^<]+?>', '', text or "")

def safe_find_text(parent, tag):
    element = parent.find(tag)
    return element.text if element is not None else ""

def fetch():
    response = requests.get(RSS_URL)
    root = ET.fromstring(response.content)

    items = []

    for item in root.findall(".//item")[:8]:
        title = safe_find_text(item, "title")
        link = safe_find_text(item, "link")
        pubDate = safe_find_text(item, "pubDate")

        # FIX: safe handling
        description_raw = safe_find_text(item, "description")
        clean_desc = clean_html(description_raw)[:180]

        items.append({
            "title": title,
            "link": link,
            "date": pubDate,
            "desc": clean_desc if clean_desc else "No preview available."
        })

    with open("data/blog.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

if __name__ == "__main__":
    fetch()
