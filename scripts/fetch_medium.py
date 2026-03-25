import requests
import json
import xml.etree.ElementTree as ET
import re

RSS_URL = "https://medium.com/feed/@prateekpulastya"

def clean_html(text):
    return re.sub('<[^<]+?>', '', text)

def fetch():
    response = requests.get(RSS_URL)
    root = ET.fromstring(response.content)

    items = []

    for item in root.findall(".//item")[:8]:
        title = item.find("title").text
        link = item.find("link").text
        pubDate = item.find("pubDate").text
        description = item.find("description").text

        clean_desc = clean_html(description)[:180]

        items.append({
            "title": title,
            "link": link,
            "date": pubDate,
            "desc": clean_desc
        })

    with open("data/blog.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

if __name__ == "__main__":
    fetch()
