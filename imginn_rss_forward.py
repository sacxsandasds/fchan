import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils

USERNAME = "forwardobservations2.0"  # change to any username
OUTFILE = f"{USERNAME}_ig.rss"

URL = f"https://imginn.com/{USERNAME}/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

html = requests.get(URL, headers=headers, timeout=15).text
soup = BeautifulSoup(html, "html.parser")

# Prepare RSS structure
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = f"Instagram – {USERNAME}"
ET.SubElement(channel, "link").text = URL
ET.SubElement(channel, "description").text = f"Posts by @{USERNAME} (via imginn)"

seen_posts = set()

# Robust parsing: look for any <a> with /p/ in href
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/p/"):
        post_url = f"https://imginn.com{href}"
        if post_url in seen_posts:
            continue
        seen_posts.add(post_url)

        # Create RSS item
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"Post by {USERNAME}"
        ET.SubElement(item, "link").text = post_url
        ET.SubElement(item, "guid").text = post_url

        # Use current UTC time as pubDate (fallback)
        ET.SubElement(item, "pubDate").text = email.utils.format_datetime(datetime.utcnow())

# Write RSS to file
tree = ET.ElementTree(rss)
tree.write(OUTFILE, encoding="utf-8", xml_declaration=True)
print(f"Wrote {OUTFILE} ({len(seen_posts)} posts)")
